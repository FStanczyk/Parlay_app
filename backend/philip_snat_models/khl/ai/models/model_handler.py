import torch
import torch.nn as nn
import pandas as pd
import os
from datetime import date
from philip_snat_models.khl.ai.models.models_classes import WinnerModel, GoalsModel, Prediction
from philip_snat_models.khl.ai.models.model_utils import (
    getAttributes,
    get_games_to_predict,
    get_games_to_predict_df,
    WINNER_STRATEGY,
    GOALS_STRATEGY,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _model_path(name):
    return os.path.join(BASE_DIR, f"{name}.pth")


def _updates_file():
    return os.path.join(BASE_DIR, "model_updates.csv")


def load_model(STRATEGY):
    model_name = STRATEGY["name"]
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
                if model_name == WINNER_STRATEGY["name"]:
                    fit_winner()
                elif model_name == GOALS_STRATEGY["name"]:
                    fit_goals()

    if os.path.exists(model_path):
        if model_name == WINNER_STRATEGY["name"]:
            model = WinnerModel()
        elif model_name == GOALS_STRATEGY["name"]:
            model = GoalsModel(STRATEGY)
        else:
            return None
        model.load_state_dict(torch.load(model_path, weights_only=True))
        model.eval()
        return model
    else:
        print(f"Model file not found: {model_path}")
        return None


def fit_winner(split=0.2):
    train_attr, test_attr, train_labels, test_labels = getAttributes(WINNER_STRATEGY, split)

    train_attr_tensor = torch.FloatTensor(train_attr)
    train_labels_tensor = torch.FloatTensor(1 - train_labels).reshape(-1, 1)

    test_attr_tensor = torch.FloatTensor(test_attr) if len(test_attr) > 0 else None
    test_labels_tensor = (
        torch.FloatTensor(1 - test_labels).reshape(-1, 1) if len(test_attr) > 0 else None
    )

    model = WinnerModel()
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        outputs = model(train_attr_tensor)
        train_loss = criterion(outputs, train_labels_tensor)
        train_loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/100 - Train Loss: {train_loss.item():.4f}")

    model.eval()
    torch.save(model.state_dict(), _model_path(WINNER_STRATEGY["name"]))
    _record_update(WINNER_STRATEGY["name"])
    return model


def fit_goals(split=0.2):
    train_attr, test_attr, train_labels, test_labels = getAttributes(GOALS_STRATEGY, split)

    train_labels_total = train_labels["total_score_no_ot"].clip(0, 10).astype(int).values
    train_labels_home = train_labels["home_score_no_ot"].clip(0, 5).astype(int).values
    train_labels_away = train_labels["away_score_no_ot"].clip(0, 5).astype(int).values

    train_attr_tensor = torch.FloatTensor(train_attr)
    model = GoalsModel(GOALS_STRATEGY)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        outputs = model(train_attr_tensor)
        loss = (
            criterion(outputs["total"], torch.LongTensor(train_labels_total))
            + criterion(outputs["home"], torch.LongTensor(train_labels_home))
            + criterion(outputs["away"], torch.LongTensor(train_labels_away))
        )
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/100 - Train Loss: {loss.item():.4f}")

    model.eval()
    torch.save(model.state_dict(), _model_path(GOALS_STRATEGY["name"]))
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
            df = pd.concat(
                [df, pd.DataFrame({"model": [model_name], "last_update": [current_date]})],
                ignore_index=True,
            )
        df.to_csv(updates_file, index=False)
    else:
        pd.DataFrame({"model": [model_name], "last_update": [current_date]}).to_csv(
            updates_file, index=False
        )


def predict_all_from_df(df):
    winner_model = load_model(WINNER_STRATEGY)
    goals_model = load_model(GOALS_STRATEGY)

    if winner_model is None or goals_model is None:
        print("KHL models not found — skipping prediction")
        return []

    winner_predictions = _predict_from_df(WINNER_STRATEGY, winner_model, df)
    goals_predictions = _predict_from_df(GOALS_STRATEGY, goals_model, df)

    all_game_ids = set(winner_predictions.keys()) | set(goals_predictions.keys())
    results = []

    for game_id in all_game_ids:
        winner_pred = winner_predictions.get(game_id)
        goals_pred = goals_predictions.get(game_id)

        if goals_pred:
            home_team = goals_pred["home_team"]
            away_team = goals_pred["away_team"]
            pred_date = goals_pred["date"]
        elif winner_pred:
            home_team = winner_pred["home_team"]
            away_team = winner_pred["away_team"]
            pred_date = winner_pred["date"]
        else:
            continue

        new_prediction = Prediction(home_team, away_team, game_id, pred_date)

        if winner_pred:
            new_prediction.add_winner(winner_pred["winner"])

        if goals_pred:
            for goal_count, prob in goals_pred["total_goals"].items():
                new_prediction.add_total_goal(goal_count, prob)
            for goal_count, prob in goals_pred["home_goals"].items():
                new_prediction.add_home_goal(goal_count, prob)
            for goal_count, prob in goals_pred["away_goals"].items():
                new_prediction.add_away_goal(goal_count, prob)

        results.append(new_prediction)

    return results


def _predict_from_df(strategy, model, df):
    X, df_predict = get_games_to_predict_df(strategy, df)

    if X.empty:
        return {}

    X_tensor = torch.FloatTensor(X.values)
    model.eval()
    with torch.no_grad():
        predictions = model(X_tensor)

    results = {}
    for i, (idx, row) in enumerate(df_predict.iterrows()):
        game_id = int(row["game_id"])

        if strategy["name"] == GOALS_STRATEGY["name"]:
            total_probs = predictions["total"][i].numpy()
            home_probs = predictions["home"][i].numpy()
            away_probs = predictions["away"][i].numpy()

            results[game_id] = {
                "home_team": str(row["home_team"]),
                "away_team": str(row["away_team"]),
                "date": row["date"],
                "total_goals": {k: round(float(total_probs[k]), 4) for k in range(11)},
                "home_goals": {k: round(float(home_probs[k]), 4) for k in range(6)},
                "away_goals": {k: round(float(away_probs[k]), 4) for k in range(6)},
            }
        else:
            pred_value = (
                predictions[i].item()
                if hasattr(predictions[i], "item")
                else float(predictions[i])
            )
            results[game_id] = {
                "home_team": str(row["home_team"]),
                "away_team": str(row["away_team"]),
                "date": row["date"],
                "winner": round(float(pred_value), 4),
            }

    return results
