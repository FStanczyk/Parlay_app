import torch
import torch.nn as nn
import pandas as pd
import os
from datetime import date
from app.core.database import SessionLocal
from app.models.philip_snat_nl_game import PhilipSnatNlGame
from philip_snat_models.nl.ai.models.models_classes import WinnerModel, GoalsModel, Prediction
from philip_snat_models.nl.ai.models.model_utils import (
    WINNER_STRATEGY,
    GOALS_STRATEGY,
    get_attributes_from_df,
    get_games_to_predict_from_df,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR)
WINNER_MODEL_PATH = os.path.join(MODELS_DIR, "winner_model.pth")
GOALS_MODEL_PATH = os.path.join(MODELS_DIR, "goals_model.pth")
MODEL_UPDATES_FILE = os.path.join(MODELS_DIR, "model_updates.csv")


def _games_to_dataframe(games):
    rows = []
    for g in games:
        rows.append(
            {
                "game_id": g.nl_id,
                "date": str(g.date),
                "hour": g.hour or "",
                "home_team": g.home_team,
                "away_team": g.away_team,
                "winner": g.winner or "",
                "home_score": g.home_score,
                "away_score": g.away_score,
                "home_score_no_ot": g.home_score_no_ot,
                "away_score_no_ot": g.away_score_no_ot,
                "total_score": g.total_score,
                "total_score_no_ot": g.total_score_no_ot,
                "OT": g.ot,
                "SO": g.so,
                "HRank": g.h_rank,
                "ARank": g.a_rank,
                "RankDiff": g.rank_diff,
                "HGpG": g.h_gpg,
                "AGpG": g.a_gpg,
                "GpGDiff": g.gpg_diff,
                "HGApG": g.h_gapg,
                "AGApG": g.a_gapg,
                "GApGDiff": g.gapg_diff,
                "HSOGpG": g.h_sogpg,
                "ASOGpG": g.a_sogpg,
                "SOGpGDiff": g.sogpg_diff,
                "HSSlotPG": g.h_sslotpg,
                "ASSlotPG": g.a_sslotpg,
                "SSlotPGDiff": g.sslotpg_diff,
                "HSHMpG": g.h_shmpg,
                "ASHMpG": g.a_shmpg,
                "HMpGDiff": g.hmpg_diff,
                "HSHPpG": g.h_shppg,
                "ASHPpG": g.a_shppg,
                "HPpGDiff": g.hpppg_diff,
                "HPPGpG": g.h_ppgpgg,
                "APPGpG": g.a_ppgpgg,
                "PGpGDiff": g.ppgpgg_diff,
                "HPPGApG": g.h_ppgapg,
                "APPGApG": g.a_ppgapg,
                "PPGApGDiff": g.ppgapg_diff,
                "HPPGEff": g.h_ppgeff,
                "APPGEff": g.a_ppgeff,
                "PPGEffDiff": g.ppgeff_diff,
                "HPKEff": g.h_pkeff,
                "APKEff": g.a_pkeff,
                "PKEffDiff": g.pkeff_diff,
                "HSApG": g.h_sapg,
                "ASApG": g.a_sapg,
                "SApGDiff": g.sapg_diff,
                "HSSlotApG": g.h_sslotapg,
                "ASSlotApG": g.a_sslotapg,
                "SSlotApGDiff": g.sslotapg_diff,
                "HLGD": g.h_lgd,
                "ALGD": g.a_lgd,
                "HLGPA": g.h_lgpa,
                "ALGPA": g.a_lgpa,
                "HLGOP": g.h_lgop,
                "ALGOP": g.a_lgop,
                "LGOPDiff": g.lgop_diff,
                "HL5GW": g.h_l5gw,
                "AL5GW": g.a_l5gw,
                "L5GWDiff": g.l5gw_diff,
            }
        )
    return pd.DataFrame(rows)


def load_model(strategy):
    model_name = strategy["name"]
    model_path = (
        WINNER_MODEL_PATH if model_name == "winner_model" else GOALS_MODEL_PATH
    )
    current_date = date.today()

    if os.path.exists(MODEL_UPDATES_FILE):
        df = pd.read_csv(MODEL_UPDATES_FILE)
        if model_name in df["model"].values:
            last_update_str = df.loc[df["model"] == model_name, "last_update"].values[
                0
            ]
            last_update = pd.to_datetime(last_update_str).date()
            days_since_update = (current_date - last_update).days

            if days_since_update > 30:
                if model_name == WINNER_STRATEGY["name"]:
                    fit_winner()
                elif model_name == GOALS_STRATEGY["name"]:
                    fit_goals()

    if os.path.exists(model_path):
        if model_name == WINNER_STRATEGY["name"]:
            model = WinnerModel(len(WINNER_STRATEGY["attributes"]))
        elif model_name == GOALS_STRATEGY["name"]:
            model = GoalsModel(GOALS_STRATEGY)
        else:
            return None
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        return model
    else:
        return None


def fit_winner(split=0.2, show_plot=False):
    db = SessionLocal()
    try:
        all_games = (
            db.query(PhilipSnatNlGame)
            .filter(PhilipSnatNlGame.winner.isnot(None))
            .order_by(PhilipSnatNlGame.date.asc())
            .all()
        )
        df = _games_to_dataframe(all_games)
    finally:
        db.close()

    if len(df) == 0:
        print("No training data available")
        return None

    train_attr, test_attr, train_labels, test_labels = get_attributes_from_df(
        df, WINNER_STRATEGY, split
    )

    train_attr_tensor = torch.FloatTensor(train_attr)
    train_labels_tensor = torch.FloatTensor(1 - train_labels).reshape(-1, 1)

    if len(test_attr) > 0:
        test_attr_tensor = torch.FloatTensor(test_attr)
        test_labels_tensor = torch.FloatTensor(1 - test_labels).reshape(-1, 1)
    else:
        test_attr_tensor = None
        test_labels_tensor = None

    model = WinnerModel(len(WINNER_STRATEGY["attributes"]))
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_losses = []
    test_losses = []
    epochs = 100

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

    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(model.state_dict(), WINNER_MODEL_PATH)

    current_date = date.today().strftime("%Y-%m-%d")
    model_name = WINNER_STRATEGY["name"]

    if os.path.exists(MODEL_UPDATES_FILE):
        df = pd.read_csv(MODEL_UPDATES_FILE)
        if model_name in df["model"].values:
            df.loc[df["model"] == model_name, "last_update"] = current_date
        else:
            new_row = pd.DataFrame({"model": [model_name], "last_update": [current_date]})
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(MODEL_UPDATES_FILE, index=False)
    else:
        os.makedirs(os.path.dirname(MODEL_UPDATES_FILE), exist_ok=True)
        df = pd.DataFrame({"model": [model_name], "last_update": [current_date]})
        df.to_csv(MODEL_UPDATES_FILE, index=False)

    return model


def fit_goals(split=0.2, show_plot=False):
    db = SessionLocal()
    try:
        all_games = (
            db.query(PhilipSnatNlGame)
            .filter(PhilipSnatNlGame.winner.isnot(None))
            .order_by(PhilipSnatNlGame.date.asc())
            .all()
        )
        df = _games_to_dataframe(all_games)
    finally:
        db.close()

    if len(df) == 0:
        print("No training data available")
        return None

    train_attr, test_attr, train_labels, test_labels = get_attributes_from_df(
        df, GOALS_STRATEGY, split
    )

    train_labels_total = (
        train_labels["total_score_no_ot"].clip(0, 10).astype(int).values
    )
    train_labels_home = train_labels["home_score_no_ot"].clip(0, 5).astype(int).values
    train_labels_away = train_labels["away_score_no_ot"].clip(0, 5).astype(int).values

    train_labels_total_tensor = torch.LongTensor(train_labels_total)
    train_labels_home_tensor = torch.LongTensor(train_labels_home)
    train_labels_away_tensor = torch.LongTensor(train_labels_away)

    if len(test_attr) > 0:
        test_attr_tensor = torch.FloatTensor(test_attr)
        test_labels_total = (
            test_labels["total_score_no_ot"].clip(0, 10).astype(int).values
        )
        test_labels_home = (
            test_labels["home_score_no_ot"].clip(0, 5).astype(int).values
        )
        test_labels_away = (
            test_labels["away_score_no_ot"].clip(0, 5).astype(int).values
        )
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
    epochs = 100

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
                test_loss_home = criterion(test_outputs["home"], test_labels_home_tensor)
                test_loss_away = criterion(test_outputs["away"], test_labels_away_tensor)
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

    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(model.state_dict(), GOALS_MODEL_PATH)

    current_date = date.today().strftime("%Y-%m-%d")
    model_name = GOALS_STRATEGY["name"]

    if os.path.exists(MODEL_UPDATES_FILE):
        df = pd.read_csv(MODEL_UPDATES_FILE)
        if model_name in df["model"].values:
            df.loc[df["model"] == model_name, "last_update"] = current_date
        else:
            new_row = pd.DataFrame({"model": [model_name], "last_update": [current_date]})
            df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(MODEL_UPDATES_FILE, index=False)
    else:
        os.makedirs(os.path.dirname(MODEL_UPDATES_FILE), exist_ok=True)
        df = pd.DataFrame({"model": [model_name], "last_update": [current_date]})
        df.to_csv(MODEL_UPDATES_FILE, index=False)

    return model


def predict_all_from_df(df):
    winner_model = load_model(WINNER_STRATEGY)
    goals_model = load_model(GOALS_STRATEGY)

    if winner_model is None or goals_model is None:
        print("Models not found. Training new models...")
        if winner_model is None:
            fit_winner(show_plot=False)
        if goals_model is None:
            fit_goals(show_plot=False)
        winner_model = load_model(WINNER_STRATEGY)
        goals_model = load_model(GOALS_STRATEGY)

    winner_predictions = predict(WINNER_STRATEGY, df, winner_model)
    goals_predictions = predict(GOALS_STRATEGY, df, goals_model)

    all_game_ids = set(winner_predictions.keys()) | set(goals_predictions.keys())
    results = []

    for game_id in all_game_ids:
        winner_pred = winner_predictions.get(game_id)
        goals_pred = goals_predictions.get(game_id)

        if goals_pred:
            home_team = goals_pred["home_team"]
            away_team = goals_pred["away_team"]
            date = goals_pred["date"]
        elif winner_pred:
            home_team = winner_pred["home_team"]
            away_team = winner_pred["away_team"]
            date = winner_pred["date"]
        else:
            continue

        new_prediction = Prediction(home_team, away_team, game_id, date)

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


def predict(strategy, df, model):
    X, df_predict = get_games_to_predict_from_df(df, strategy)

    if X.empty:
        return {}

    X_tensor = torch.FloatTensor(X.values)
    model.eval()
    with torch.no_grad():
        predictions = model(X_tensor)

    results = {}
    for i, (idx, row) in enumerate(df_predict.iterrows()):
        game_id = str(row["game_id"])

        if strategy["name"] == GOALS_STRATEGY["name"]:
            total_probs = predictions["total"][i].numpy()
            home_probs = predictions["home"][i].numpy()
            away_probs = predictions["away"][i].numpy()

            total_dict = {}
            for goal_count in range(11):
                total_dict[goal_count] = round(float(total_probs[goal_count]), 4)

            home_dict = {}
            for goal_count in range(6):
                home_dict[goal_count] = round(float(home_probs[goal_count]), 4)

            away_dict = {}
            for goal_count in range(6):
                away_dict[goal_count] = round(float(away_probs[goal_count]), 4)

            results[game_id] = {
                "home_team": str(row["home_team"]),
                "away_team": str(row["away_team"]),
                "date": row["date"],
                "total_goals": total_dict,
                "home_goals": home_dict,
                "away_goals": away_dict,
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
