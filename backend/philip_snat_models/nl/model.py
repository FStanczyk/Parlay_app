import csv
import os
import pandas as pd
from datetime import date

from app.core.database import SessionLocal
from app.models.philip_snat_nl_game import PhilipSnatNlGame
from philip_snat_models.model_interface import AiModelInterface
from philip_snat_models.nl.get import NlGetter
from philip_snat_models.nl.ai.models.model_handler import (
    predict_all_from_df,
    fit_winner,
    fit_goals,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "predictions"))

CSV_HEADERS = [
    "date",
    "home",
    "away",
    "1ML",
    "2ML",
    "X",
    "1",
    "2",
    "1X",
    "2X",
    "over3.5",
    "over4.5",
    "over5.5",
    "over6.5",
    "over7.5",
    "over8.5",
    "under3.5",
    "under4.5",
    "under5.5",
    "under6.5",
    "under7.5",
    "under8.5",
    "home_over1.5",
    "home_over2.5",
    "home_over3.5",
    "home_over4.5",
    "away_over1.5",
    "away_over2.5",
    "away_over3.5",
    "away_over4.5",
    "home_-1.5",
    "away_-1.5",
    "home/o4.5",
    "home/o5.5",
    "home/o6.5",
    "home/u4.5",
    "home/u5.5",
    "home/u6.5",
    "away/o4.5",
    "away/o5.5",
    "away/o6.5",
    "away/u4.5",
    "away/u5.5",
    "away/u6.5",
]


class NlAiModel(AiModelInterface):

    LEAGUE_NAME = "NL"

    def update_games(self):
        db = SessionLocal()
        try:
            getter = NlGetter()
            getter.fill_finished_games()
        finally:
            db.close()

    def download_new_games(self):
        db = SessionLocal()
        try:
            getter = NlGetter()
            getter.get_new_games(for_tomorrow=False)
            getter.get_new_games(for_tomorrow=True)
        finally:
            db.close()

    def _games_to_dataframe(self, games):
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

    def _calculate_odds(self, prediction):
        winner_prob = prediction.winner if prediction.winner is not None else 0.5
        home_pct = 1.0 - winner_prob
        away_pct = winner_prob

        prob_home_win = 0.0
        prob_away_win = 0.0
        prob_draw = 0.0
        prob_home_win_by_1_5_plus = 0.0
        prob_away_win_by_1_5_plus = 0.0

        for hg in prediction.home_goals.keys():
            for ag in prediction.away_goals.keys():
                ph = prediction.home_goals.get(hg, 0.0)
                pa = prediction.away_goals.get(ag, 0.0)
                match_prob = ph * pa
                hi = int(hg)
                ai = int(ag)

                if hi > ai:
                    prob_home_win += match_prob
                    if hi - ai > 1.5:
                        prob_home_win_by_1_5_plus += match_prob
                elif ai > hi:
                    prob_away_win += match_prob
                    if ai - hi > 1.5:
                        prob_away_win_by_1_5_plus += match_prob
                else:
                    prob_draw += match_prob

        o = {}
        o["1ML"] = home_pct
        o["2ML"] = away_pct
        o["X"] = prob_draw
        o["1"] = prob_home_win
        o["2"] = prob_away_win
        o["1X"] = prob_home_win + prob_draw
        o["2X"] = prob_away_win + prob_draw

        total_goals = prediction.total_goals
        o["over3.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(4))
        o["over4.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(5))
        o["over5.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(6))
        o["over6.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(7))
        o["over7.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(8))
        o["over8.5"] = 1.0 - sum(total_goals.get(i, 0.0) for i in range(9))

        o["under3.5"] = sum(total_goals.get(i, 0.0) for i in range(4))
        o["under4.5"] = sum(total_goals.get(i, 0.0) for i in range(5))
        o["under5.5"] = sum(total_goals.get(i, 0.0) for i in range(6))
        o["under6.5"] = sum(total_goals.get(i, 0.0) for i in range(7))
        o["under7.5"] = sum(total_goals.get(i, 0.0) for i in range(8))
        o["under8.5"] = sum(total_goals.get(i, 0.0) for i in range(9))

        home_goals = prediction.home_goals
        o["home_over1.5"] = 1.0 - sum(home_goals.get(i, 0.0) for i in range(2))
        o["home_over2.5"] = 1.0 - sum(home_goals.get(i, 0.0) for i in range(3))
        o["home_over3.5"] = 1.0 - sum(home_goals.get(i, 0.0) for i in range(4))
        o["home_over4.5"] = 1.0 - sum(home_goals.get(i, 0.0) for i in range(5))

        away_goals = prediction.away_goals
        o["away_over1.5"] = 1.0 - sum(away_goals.get(i, 0.0) for i in range(2))
        o["away_over2.5"] = 1.0 - sum(away_goals.get(i, 0.0) for i in range(3))
        o["away_over3.5"] = 1.0 - sum(away_goals.get(i, 0.0) for i in range(4))
        o["away_over4.5"] = 1.0 - sum(away_goals.get(i, 0.0) for i in range(5))

        o["home_-1.5"] = prob_home_win_by_1_5_plus
        o["away_-1.5"] = prob_away_win_by_1_5_plus

        o["home/o4.5"] = o["over4.5"] * o["1"]
        o["home/o5.5"] = o["over5.5"] * o["1"]
        o["home/o6.5"] = o["over6.5"] * o["1"]
        o["home/u4.5"] = o["under4.5"] * o["1"]
        o["home/u5.5"] = o["under5.5"] * o["1"]
        o["home/u6.5"] = o["under6.5"] * o["1"]
        o["away/o4.5"] = o["over4.5"] * o["2"]
        o["away/o5.5"] = o["over5.5"] * o["2"]
        o["away/o6.5"] = o["over6.5"] * o["2"]
        o["away/u4.5"] = o["under4.5"] * o["2"]
        o["away/u5.5"] = o["under5.5"] * o["2"]
        o["away/u6.5"] = o["under6.5"] * o["2"]

        return o

    def predict(self):
        db = SessionLocal()
        try:
            today = date.today()

            today_file = os.path.join(
                PREDICTIONS_DIR, f"{self.LEAGUE_NAME}-{today}.csv"
            )
            if os.path.exists(today_file):
                print(
                    f"[NL predict] Prediction file for today already exists: {today_file}, skipping"
                )
                return

            games = (
                db.query(PhilipSnatNlGame)
                .filter(
                    PhilipSnatNlGame.winner.is_(None),
                    PhilipSnatNlGame.date >= today,
                )
                .all()
            )
            print(f"[NL predict] Found {len(games)} upcoming games")

            if not games:
                print("[NL predict] No games to predict")
                return

            all_games = (
                db.query(PhilipSnatNlGame)
                .order_by(PhilipSnatNlGame.date.asc())
                .all()
            )
            df = self._games_to_dataframe(all_games)

            predictions = predict_all_from_df(df)
            for p in predictions:
                p.calculate_events()

            rows = []
            for p in predictions:
                game = (
                    db.query(PhilipSnatNlGame)
                    .filter(PhilipSnatNlGame.nl_id == str(p.game_id))
                    .first()
                )
                if game:
                    try:
                        from sqlalchemy import Table, MetaData

                        metadata = MetaData()
                        table = Table(
                            "philip_snat_nl_games", metadata, autoload_with=db.bind
                        )
                        prediction_goals = (
                            {str(k): float(v) for k, v in p.total_goals.items()}
                            if p.total_goals
                            else None
                        )
                        db.execute(
                            table.update()
                            .where(table.c.id == game.id)
                            .values(
                                prediction_winner=(
                                    p.winner if p.winner is not None else None
                                ),
                                prediction_goals=prediction_goals,
                            )
                        )
                        db.commit()
                    except Exception as db_error:
                        print(
                            f"  Error saving predictions for game {p.game_id}: {db_error}"
                        )
                        db.rollback()

                odds = self._calculate_odds(p)
                rows.append(
                    {
                        "date": str(p.date),
                        "home": p.home_team,
                        "away": p.away_team,
                        **odds,
                    }
                )
                print(
                    f"  {p.home_team} vs {p.away_team} ({p.date}): "
                    f"1ML={odds['1ML']:.2%} 2ML={odds['2ML']:.2%} over4.5={odds['over4.5']:.2%}"
                )

            if rows:
                self._save_predictions_csv(rows, PREDICTIONS_DIR, today)

            print(f"[NL predict] Done — {len(rows)} games written")
        finally:
            db.close()

    def _save_predictions_csv(self, rows, out_dir, today):
        os.makedirs(out_dir, exist_ok=True)
        filename = f"NL-{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(out_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: f"{v:.4f}" if isinstance(v, float) else v
                        for k, v in row.items()
                    }
                )

        print(f"[NL predict] Saved predictions to {filepath}")
