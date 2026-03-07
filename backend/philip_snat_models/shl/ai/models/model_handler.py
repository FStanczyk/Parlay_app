import torch
import torch.nn as nn
import pandas as pd
import os
from datetime import date
from philip_snat_models.shl.ai.models.models_classes import WinnerModel, GoalsModel, Prediction
from philip_snat_models.shl.ai.models.model_utils import (
    get_attributes,
    get_games_to_predict,
    WINNER_STRATEGY,
    GOALS_STRATEGY,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _model_path(name):
    return os.path.join(BASE_DIR, f"{name}.pth")


def _updates_file():
    return os.path.join(BASE_DIR, "model_updates.csv")


def load_model(strategy, training_df=None):
    model_name = strategy["name"]
    model_path = _model_path(model_name)
    updates_file = _updates_file()
    current_date = date.today()

    if os.path.exists(updates_file):
        df = pd.read_csv(updates_file)
        if model_name in df["model"].values:
            last_update_str = df.loc[df["model"] == model_name, "last_update"].values[0]
            last_update = pd.to_datetime(last_update_str).date()
            days_since_update = (current_date - last_update).days
            if days_since_update > 30:
                if model_name == GOALS_STRATEGY["name"]:
                    fit_goals(show_learning_curve=False, training_df=training_df)
                elif model_name == WINNER_STRATEGY["name"]:
                    fit_winner(show_learning_curve=False, training_df=training_df)

    if os.path.exists(model_path):
        if model_name == WINNER_STRATEGY["name"]:
            model = WinnerModel()
        elif model_name == GOALS_STRATEGY["name"]:
            model = GoalsModel(strategy)
        else:
            return None
        model.load_state_dict(torch.load(model_path, weights_only=True))
        model.eval()
        return model
    else:
        print(f"Model file not found: {model_path}")
        print(f"Training {model_name} model...")
        if model_name == WINNER_STRATEGY["name"]:
            return fit_winner(show_learning_curve=False, training_df=training_df)
        elif model_name == GOALS_STRATEGY["name"]:
            return fit_goals(show_learning_curve=False, training_df=training_df)
        else:
            return None


def fit_winner(split=0.2, show_learning_curve=True, training_df=None):
    try:
        train_attr, test_attr, train_labels, test_labels = get_attributes(
            WINNER_STRATEGY, split, df=training_df
        )
    except FileNotFoundError as e:
        print(f"Error: Training data not available")
        print("Please ensure games with winners are loaded in the database.")
        raise

    train_attr_tensor = torch.FloatTensor(train_attr)
    train_labels_tensor = torch.FloatTensor(train_labels).reshape(-1, 1)

    if len(test_attr) > 0:
        test_attr_tensor = torch.FloatTensor(test_attr)
        test_labels_tensor = torch.FloatTensor(test_labels).reshape(-1, 1)
    else:
        test_attr_tensor = None
        test_labels_tensor = None

    model = WinnerModel()
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_losses = []
    test_losses = []
    epochs = 300

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        outputs = model(train_attr_tensor)
        train_loss = criterion(outputs, train_labels_tensor)
        train_losses.append(train_loss.item())

        train_loss.backward()
        optimizer.step()

        if len(test_attr) > 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(test_attr_tensor)
                test_loss = criterion(test_outputs, test_labels_tensor)
                test_losses.append(test_loss.item())
        else:
            test_losses = None

        if (epoch + 1) % 10 == 0:
            if test_losses:
                print(
                    f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss.item():.4f}, Test Loss: {test_losses[-1]:.4f}"
                )
            else:
                print(
                    f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss.item():.4f}"
                )

    model.eval()

    model_name = WINNER_STRATEGY["name"]
    model_path = _model_path(model_name)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    torch.save(model.state_dict(), model_path)

    _record_update(WINNER_STRATEGY["name"])

    return model


def fit_goals(split=0.2, show_learning_curve=True, training_df=None):
    try:
        train_attr, test_attr, train_labels, test_labels = get_attributes(
            GOALS_STRATEGY, split, df=training_df
        )
    except FileNotFoundError as e:
        print(f"Error: Training data not available")
        print("Please ensure games with winners are loaded in the database.")
        raise

    train_labels_total = train_labels[:, 0].clip(0, 10).astype(int)
    train_labels_home = train_labels[:, 1].clip(0, 5).astype(int)
    train_labels_away = train_labels[:, 2].clip(0, 5).astype(int)

    train_labels_total_tensor = torch.LongTensor(train_labels_total)
    train_labels_home_tensor = torch.LongTensor(train_labels_home)
    train_labels_away_tensor = torch.LongTensor(train_labels_away)

    if len(test_attr) > 0:
        test_attr_tensor = torch.FloatTensor(test_attr)
        test_labels_total = test_labels[:, 0].clip(0, 10).astype(int)
        test_labels_home = test_labels[:, 1].clip(0, 5).astype(int)
        test_labels_away = test_labels[:, 2].clip(0, 5).astype(int)
        test_labels_total_tensor = torch.LongTensor(test_labels_total)
        test_labels_home_tensor = torch.LongTensor(test_labels_home)
        test_labels_away_tensor = torch.LongTensor(test_labels_away)
    else:
        test_attr_tensor = None
        test_labels_total_tensor = None
        test_labels_home_tensor = None
        test_labels_away_tensor = None

    train_attr_tensor = torch.FloatTensor(train_attr)
    model = GoalsModel(GOALS_STRATEGY)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_losses = []
    test_losses = []
    epochs = 300

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        outputs = model(train_attr_tensor)
        loss_total = criterion(outputs["total"], train_labels_total_tensor)
        loss_home = criterion(outputs["home"], train_labels_home_tensor)
        loss_away = criterion(outputs["away"], train_labels_away_tensor)
        train_loss = loss_total + loss_home + loss_away
        train_losses.append(train_loss.item())

        train_loss.backward()
        optimizer.step()

        if len(test_attr) > 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(test_attr_tensor)
                test_loss_total = criterion(
                    test_outputs["total"], test_labels_total_tensor
                )
                test_loss_home = criterion(
                    test_outputs["home"], test_labels_home_tensor
                )
                test_loss_away = criterion(
                    test_outputs["away"], test_labels_away_tensor
                )
                test_loss = test_loss_total + test_loss_home + test_loss_away
                test_losses.append(test_loss.item())
        else:
            test_losses = None

        if (epoch + 1) % 10 == 0:
            if test_losses:
                print(
                    f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss.item():.4f}, Test Loss: {test_losses[-1]:.4f}"
                )
            else:
                print(
                    f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss.item():.4f}"
                )

    model.eval()

    model_name = GOALS_STRATEGY["name"]
    model_path = _model_path(model_name)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    torch.save(model.state_dict(), model_path)

    _record_update(GOALS_STRATEGY["name"])

    return model


def _record_update(model_name):
    updates_file = _updates_file()
    current_date = date.today().strftime("%Y-%m-%d")
    if os.path.exists(updates_file):
        df = pd.read_csv(updates_file)
        if model_name in df["model"].values:
            df.loc[df["model"] == model_name, "last_update"] = current_date
        else:
            new_row = pd.DataFrame(
                {"model": [model_name], "last_update": [current_date]}
            )
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(updates_file, index=False)
    else:
        os.makedirs(os.path.dirname(updates_file), exist_ok=True)
        df = pd.DataFrame({"model": [model_name], "last_update": [current_date]})
        df.to_csv(updates_file, index=False)


def predict_goals(training_df=None):
    winner_model = load_model(WINNER_STRATEGY, training_df=training_df)
    goals_model = load_model(GOALS_STRATEGY, training_df=training_df)

    if goals_model is None:
        print("Goals model not found. Please train the model first.")
        return []

    X_goals, df_predict = get_games_to_predict(GOALS_STRATEGY)

    if X_goals.empty:
        print("No games to predict.")
        return []

    X_goals_tensor = torch.FloatTensor(X_goals.values)
    goals_model.eval()
    with torch.no_grad():
        goals_predictions = goals_model(X_goals_tensor)

    winner_predictions = None
    if winner_model is not None:
        X_winner, _ = get_games_to_predict(WINNER_STRATEGY)
        if not X_winner.empty:
            X_winner_tensor = torch.FloatTensor(X_winner.values)
            winner_model.eval()
            with torch.no_grad():
                winner_predictions = winner_model(X_winner_tensor)

    results = []
    for i, (idx, row) in enumerate(df_predict.iterrows()):
        uuid = str(row["uuid"])
        home_team = str(row["home"])
        away_team = str(row["away"])
        game_date = str(row["date"])

        total_probs = goals_predictions["total"][i].numpy()
        home_probs = goals_predictions["home"][i].numpy()
        away_probs = goals_predictions["away"][i].numpy()

        new_prediction = Prediction(uuid, home_team, away_team, game_date)

        if winner_predictions is not None:
            winner_prob = winner_predictions[i].item()
            new_prediction.add_winner(winner_prob)

        for goal_count in range(11):
            new_prediction.add_total_goal(goal_count, float(total_probs[goal_count]))

        for goal_count in range(6):
            new_prediction.add_home_goal(goal_count, float(home_probs[goal_count]))

        for goal_count in range(6):
            new_prediction.add_away_goal(goal_count, float(away_probs[goal_count]))

        results.append(new_prediction)

    return results
