import csv
import os
import pandas as pd
import torch
from datetime import date, datetime, timedelta

from app.core.database import SessionLocal
from app.models.philip_snat_shl_game import PhilipSnatShlGame
from philip_snat_models.base_model import BaseAiModel
from philip_snat_models.shl.get import ShlGetter
from philip_snat_models.shl.ai.models.model_handler import load_model, predict_goals
from philip_snat_models.shl.ai.models.model_utils import WINNER_STRATEGY, GOALS_STRATEGY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "predictions"))

CSV_HEADERS = [
    "date", "home", "away", "1ML", "2ML", "X", "1", "2", "1X", "2X",
    "over3.5", "over4.5", "over5.5", "over6.5", "over7.5", "over8.5",
    "under3.5", "under4.5", "under5.5", "under6.5", "under7.5", "under8.5",
    "home_over1.5", "home_over2.5", "home_over3.5", "home_over4.5",
    "away_over1.5", "away_over2.5", "away_over3.5", "away_over4.5",
    "home_-1.5", "away_-1.5",
    "home/o4.5", "home/o5.5", "home/o6.5",
    "home/u4.5", "home/u5.5", "home/u6.5",
    "away/o4.5", "away/o5.5", "away/o6.5",
    "away/u4.5", "away/u5.5", "away/u6.5",
]


class ShlAiModel(BaseAiModel):
    LEAGUE_NAME = "SHL"

    def __init__(self):
        self.getter = ShlGetter()

    def update_games(self):
        db = SessionLocal()
        try:
            today = date.today()
            games = (
                db.query(PhilipSnatShlGame)
                .filter(
                    PhilipSnatShlGame.winner.is_(None),
                    PhilipSnatShlGame.date < today
                )
                .all()
            )
            print(f"[update_games] Found {len(games)} unresolved past games")

            filled = 0
            for game in games:
                try:
                    data = self.getter.get_single_game(game.shl_uuid)
                    if not data:
                        continue

                    game_info = data.get("gameInfo", {})
                    if game_info.get("state") != "post_game":
                        continue

                    home_team = data.get("homeTeam", {})
                    away_team = data.get("awayTeam", {})

                    home_score = home_team.get("score", 0)
                    away_score = away_team.get("score", 0)
                    overtime = game_info.get("overtime", False)
                    shootout = game_info.get("shootout", False)

                    home_score_no_ot = home_score
                    away_score_no_ot = away_score
                    total_goals_no_ot = home_score + away_score

                    if overtime:
                        total_goals_no_ot -= 1
                        if home_score > away_score:
                            home_score_no_ot -= 1
                        else:
                            away_score_no_ot -= 1

                    winner = 0 if home_score_no_ot > away_score_no_ot else 1

                    game.winner = winner
                    game.home_score = home_score
                    game.away_score = away_score
                    game.home_score_no_ot = home_score_no_ot
                    game.away_score_no_ot = away_score_no_ot
                    game.total_goals = home_score + away_score
                    game.total_goals_no_ot = total_goals_no_ot
                    game.ot = overtime
                    game.so = shootout
                    db.commit()

                    print(
                        f"  Updated {game.home_team} {home_score_no_ot} - {away_score_no_ot} {game.away_team} (winner={winner})"
                    )
                    filled += 1

                except Exception as e:
                    db.rollback()
                    print(f"  Error updating game {game.shl_uuid}: {e}")

            print(f"[update_games] Done — filled {filled}/{len(games)}")
        finally:
            db.close()

    def download_new_games(self):
        db = SessionLocal()
        try:
            today_date = date.today()
            dates = [today_date, today_date + timedelta(days=1)]

            print(
                f"[download_new_games] Scanning {dates[0]} and {dates[1]}"
            )
            inserted = 0

            for current_date in dates:
                date_str = current_date.strftime("%Y-%m-%d")
                try:
                    games_on_day = self.getter.get_games_for_day(date_str)
                except Exception as e:
                    print(f"  Could not fetch schedule for {date_str}: {e}")
                    continue

                print(f"  {date_str}: {len(games_on_day)} games")

                for game in games_on_day:
                    game_uuid = game.get("uuid")
                    if not game_uuid:
                        continue

                    existing = (
                        db.query(PhilipSnatShlGame)
                        .filter(PhilipSnatShlGame.shl_uuid == game_uuid)
                        .first()
                    )
                    if existing:
                        continue

                    try:
                        features = self.getter.build_game_features(game, date_str)
                        if features is None:
                            continue

                        db.add(PhilipSnatShlGame(**features))
                        db.commit()
                        inserted += 1
                    except Exception as e:
                        db.rollback()
                        print(f"  Error inserting game {game_uuid}: {e}")

            print(f"[download_new_games] Done — inserted {inserted} new games")
        finally:
            db.close()

    def predict(self):
        db = SessionLocal()
        try:
            today_date = date.today()

            today_file = os.path.join(
                PREDICTIONS_DIR, f"{self.LEAGUE_NAME}-{today_date}.csv"
            )
            if os.path.exists(today_file):
                print(
                    f"[SHL predict] Prediction file for today already exists: {today_file}, skipping"
                )
                return

            games = (
                db.query(PhilipSnatShlGame)
                .filter(
                    PhilipSnatShlGame.winner.is_(None),
                    PhilipSnatShlGame.date >= today_date,
                )
                .all()
            )
            print(f"[SHL predict] Found {len(games)} upcoming games")

            if not games:
                print("[SHL predict] No games to predict")
                return

            all_games = (
                db.query(PhilipSnatShlGame).order_by(PhilipSnatShlGame.date.asc()).all()
            )
            df = self._games_to_dataframe(all_games)

            training_df = df[df["winner"] != ""].copy()
            if len(training_df) == 0:
                training_df = None
            else:
                print(f"[SHL predict] Using {len(training_df)} completed games for training")

            predictions = self._predict_from_dataframe(df, training_df=training_df)

            rows = []
            for pred in predictions:
                game = (
                    db.query(PhilipSnatShlGame)
                    .filter(PhilipSnatShlGame.shl_uuid == pred["uuid"])
                    .first()
                )
                if game:
                    try:
                        self._save_prediction_to_db(
                            db,
                            "philip_snat_shl_games",
                            game.id,
                            pred.get("prediction_winner"),
                            pred.get("prediction_goals"),
                        )
                    except Exception as db_error:
                        print(
                            f"  Error saving predictions for game {pred['uuid']}: {db_error}"
                        )

                odds = self._calculate_odds(pred)
                rows.append({
                    "date": str(pred["date"]),
                    "home": pred["home_team"],
                    "away": pred["away_team"],
                    **odds,
                })
                print(
                    f"  {pred['home_team']} vs {pred['away_team']} ({pred['date']}): "
                    f"1ML={odds['1ML']:.2%} 2ML={odds['2ML']:.2%} over4.5={odds['over4.5']:.2%}"
                )

            if rows:
                self._save_predictions_csv(
                    rows, PREDICTIONS_DIR, self.LEAGUE_NAME, today_date, CSV_HEADERS
                )
                self._cleanup_old_files(PREDICTIONS_DIR)

            print(f"[SHL predict] Done — {len(rows)} games written")
        finally:
            db.close()

    def _games_to_dataframe(self, games):
        rows = []
        for g in games:
            rows.append({
                "uuid": g.shl_uuid,
                "date": str(g.date),
                "home": g.home_team,
                "away": g.away_team,
                "winner": float(g.winner) if g.winner is not None else "",
                "HomeRank": g.home_rank or 0,
                "AwayRank": g.away_rank or 0,
                "RankDiff": g.rank_diff or 0,
                "HGPG": g.h_gpg or 0,
                "AGPG": g.a_gpg or 0,
                "GPGDiff": g.gpg_diff or 0,
                "GPMutual": g.gpmutual or 0,
                "HGAPG": g.h_gapg or 0,
                "AGAPG": g.a_gapg or 0,
                "GAPGDiff": g.gapg_diff or 0,
                "GAPMutual": g.gapmutual or 0,
                "HPPPerc": g.h_pp_perc or 0,
                "APPPerc": g.a_pp_perc or 0,
                "HPKPerc": g.h_pk_perc or 0,
                "APKPerc": g.a_pk_perc or 0,
                "HSEff": g.h_s_eff or 0,
                "ASEff": g.a_s_eff or 0,
                "HSVSPerc": g.h_svs_perc or 0,
                "ASVSPerc": g.a_svs_perc or 0,
                "HFOPerc": g.h_fo_perc or 0,
                "AFOPerc": g.a_fo_perc or 0,
                "HCFPerc": g.h_cf_perc or 0,
                "ACFPerc": g.a_cf_perc or 0,
                "HFFPerc": g.h_ff_perc or 0,
                "AFFPerc": g.a_ff_perc or 0,
                "HCloseCFPerc": g.h_close_cf_perc or 0,
                "ACloseCFPerc": g.a_close_cf_perc or 0,
                "HCloseFFPerc": g.h_close_ff_perc or 0,
                "ACloseFFPerc": g.a_close_ff_perc or 0,
                "HPDO": g.h_pdo or 0,
                "APDO": g.a_pdo or 0,
                "HSTPerc": g.h_st_perc or 0,
                "ASTPerc": g.a_st_perc or 0,
                "HPPSEff": g.h_pps_eff or 0,
                "APPSEff": g.a_pps_eff or 0,
                "HSOGPG": g.h_sogpg or 0,
                "ASOGPG": g.a_sogpg or 0,
                "SOGPGDiff": g.sogpg_diff or 0,
                "SOGPGMutual": g.sogpg_mutual or 0,
                "HL5GW": g.h_l5gw or 0,
                "AL5GW": g.a_l5gw or 0,
                "L5GWDiff": g.l5gw_diff or 0,
                "HLmdGPG1": g.h_lmd_gpg1 or 0,
                "ALmdGPG1": g.a_lmd_gpg1 or 0,
                "HLmdGPG2": g.h_lmd_gpg2 or 0,
                "ALmdGPG2": g.a_lmd_gpg2 or 0,
                "HLmdGAPG1": g.h_lmd_gapg1 or 0,
                "ALmdGAPG1": g.a_lmd_gapg1 or 0,
                "HLmdGAPG2": g.h_lmd_gapg2 or 0,
                "ALmdGAPG2": g.a_lmd_gapg2 or 0,
                "HShameFactor": g.h_shame_factor or 0,
                "AShameFactor": g.a_shame_factor or 0,
                "HHungerFG": g.h_hunger_fg or 0,
                "AHungerFG": g.a_hunger_fg or 0,
                "HungerFGDiff": g.hunger_fg_diff or 0,
                "HungerFGMutual": g.hunger_fg_mutual or 0,
                "totalGoalsNoOT": g.total_goals_no_ot if g.total_goals_no_ot is not None else "",
                "homeScoreNoOT": g.home_score_no_ot if g.home_score_no_ot is not None else "",
                "awayScoreNoOT": g.away_score_no_ot if g.away_score_no_ot is not None else "",
            })
        return pd.DataFrame(rows)

    def _predict_from_dataframe(self, df, training_df=None):
        winner_model = load_model(WINNER_STRATEGY, training_df=training_df)
        goals_model = load_model(GOALS_STRATEGY, training_df=training_df)

        if not goals_model:
            print("Goals model not found. Please train the model first.")
            return []

        df_predict = df[df["winner"] == ""].copy()
        if df_predict.empty:
            return []

        attribute_columns = GOALS_STRATEGY["attributes"]
        available_attrs = [col for col in attribute_columns if col in df_predict.columns]
        missing_attrs = [col for col in attribute_columns if col not in df_predict.columns]

        if missing_attrs:
            print(f"Warning: Missing attribute columns: {missing_attrs}")

        X_goals = df_predict[available_attrs].copy()
        X_goals = X_goals.fillna(0)

        for col in X_goals.columns:
            X_goals[col] = pd.to_numeric(X_goals[col], errors="coerce").fillna(0)

        X_goals_tensor = torch.FloatTensor(X_goals.values)
        goals_model.eval()
        with torch.no_grad():
            goals_predictions = goals_model(X_goals_tensor)

        winner_predictions = None
        if winner_model:
            X_winner = X_goals
            X_winner_tensor = torch.FloatTensor(X_winner.values)
            winner_model.eval()
            with torch.no_grad():
                winner_predictions = winner_model(X_winner_tensor)

        results = []
        for i, (idx, row) in enumerate(df_predict.iterrows()):
            total_probs = goals_predictions["total"][i].numpy()
            home_probs = goals_predictions["home"][i].numpy()
            away_probs = goals_predictions["away"][i].numpy()

            prediction_goals = {str(k): float(total_probs[k]) for k in range(11)}

            winner_prob = None
            if winner_predictions is not None:
                winner_prob = float(winner_predictions[i].item())

            results.append({
                "uuid": str(row["uuid"]),
                "date": str(row["date"]),
                "home_team": str(row["home"]),
                "away_team": str(row["away"]),
                "prediction_winner": winner_prob,
                "prediction_goals": prediction_goals,
                "total_goals": {k: float(total_probs[k]) for k in range(11)},
                "home_goals": {k: float(home_probs[k]) for k in range(6)},
                "away_goals": {k: float(away_probs[k]) for k in range(6)},
            })

        return results

    def _calculate_odds(self, pred):
        total_goals = pred.get("total_goals", {})
        home_goals = pred.get("home_goals", {})
        away_goals = pred.get("away_goals", {})
        winner_prob = pred.get("prediction_winner", 0.5)

        home_pct = 1.0 - winner_prob
        away_pct = winner_prob

        prob_home_win = 0.0
        prob_away_win = 0.0
        prob_draw = 0.0
        prob_home_win_by_1_5_plus = 0.0
        prob_away_win_by_1_5_plus = 0.0

        for hg in range(6):
            for ag in range(6):
                ph = home_goals.get(hg, 0.0)
                pa = away_goals.get(ag, 0.0)
                match_prob = ph * pa

                if hg > ag:
                    prob_home_win += match_prob
                    if hg - ag > 1.5:
                        prob_home_win_by_1_5_plus += match_prob
                elif ag > hg:
                    prob_away_win += match_prob
                    if ag - hg > 1.5:
                        prob_away_win_by_1_5_plus += match_prob
                else:
                    prob_draw += match_prob

        odds = {}
        odds["1ML"] = home_pct
        odds["2ML"] = away_pct
        odds["X"] = prob_draw
        odds["1"] = prob_home_win
        odds["2"] = prob_away_win
        odds["1X"] = prob_home_win + prob_draw
        odds["2X"] = prob_away_win + prob_draw

        for threshold in [3.5, 4.5, 5.5, 6.5, 7.5, 8.5]:
            over_key = f"over{threshold}"
            under_key = f"under{threshold}"
            threshold_int = int(threshold)
            odds[over_key] = 1.0 - sum(total_goals.get(str(i), 0.0) for i in range(threshold_int + 1))
            odds[under_key] = sum(total_goals.get(str(i), 0.0) for i in range(threshold_int + 1))

        for threshold in [1.5, 2.5, 3.5, 4.5]:
            odds[f"home_over{threshold}"] = 1.0 - sum(home_goals.get(i, 0.0) for i in range(int(threshold) + 1))
            odds[f"away_over{threshold}"] = 1.0 - sum(away_goals.get(i, 0.0) for i in range(int(threshold) + 1))

        odds["home_-1.5"] = prob_home_win_by_1_5_plus
        odds["away_-1.5"] = prob_away_win_by_1_5_plus

        for threshold in [4.5, 5.5, 6.5]:
            odds[f"home/o{threshold}"] = odds[f"over{threshold}"] * odds["1"]
            odds[f"home/u{threshold}"] = odds[f"under{threshold}"] * odds["1"]
            odds[f"away/o{threshold}"] = odds[f"over{threshold}"] * odds["2"]
            odds[f"away/u{threshold}"] = odds[f"under{threshold}"] * odds["2"]

        return odds
