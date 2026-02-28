import csv
import os
import pandas as pd
from datetime import date, datetime

from app.core.database import SessionLocal
from app.models.philip_snat_khl_game import PhilipSnatKhlGame
from philip_snat_models.model_interface import AiModelInterface
from philip_snat_models.khl.logger import Logger
from philip_snat_models.khl.get import Getter
from philip_snat_models.khl.ai.models.model_handler import predict_all_from_df

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "predictions"))

CSV_HEADERS = [
    "date", "home", "away",
    "1ML", "2ML", "X", "1", "2", "1X", "2X",
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


class KhlAiModel(AiModelInterface):

    LEAGUE_NAME = "KHL"

    def update_games(self):
        db = SessionLocal()
        try:
            logger = Logger(verbose=2)
            getter = Getter(logger, db)
            getter.fill_finished_games()
        finally:
            db.close()

    def download_new_games(self):
        db = SessionLocal()
        try:
            logger = Logger(verbose=2)
            getter = Getter(logger, db)
            getter.get_new_games(for_tomorrow=False)
            getter.get_new_games(for_tomorrow=True)
        finally:
            db.close()

    def predict(self):
        db = SessionLocal()
        try:
            today = date.today()

            today_file = os.path.join(PREDICTIONS_DIR, f"{self.LEAGUE_NAME}-{today}.csv")
            if os.path.exists(today_file):
                print(f"[KHL predict] Prediction file for today already exists: {today_file}, skipping")
                return

            games = (
                db.query(PhilipSnatKhlGame)
                .filter(
                    PhilipSnatKhlGame.winner.is_(None),
                    PhilipSnatKhlGame.date >= today,
                )
                .all()
            )
            print(f"[KHL predict] Found {len(games)} upcoming games")

            if not games:
                print("[KHL predict] No games to predict")
                return

            all_games = db.query(PhilipSnatKhlGame).order_by(PhilipSnatKhlGame.date.asc()).all()
            df = self._games_to_dataframe(all_games)

            predictions = predict_all_from_df(df)
            for p in predictions:
                p.calculate_events()

            rows = []
            for p in predictions:
                rows.append({
                    "date": str(p.date),
                    "home": p.home_team,
                    "away": p.away_team,
                    "1ML": round(p.ML1, 4),
                    "2ML": round(p.ML2, 4),
                    "X": round(p.X, 4),
                    "1": round(p.homeReg, 4),
                    "2": round(p.awayReg, 4),
                    "1X": round(p.X1, 4),
                    "2X": round(p.X2, 4),
                    "over3.5": round(p.o35, 4),
                    "over4.5": round(p.o45, 4),
                    "over5.5": round(p.o55, 4),
                    "over6.5": round(p.o65, 4),
                    "over7.5": round(p.o75, 4),
                    "over8.5": round(p.o85, 4),
                    "under3.5": round(p.u35, 4),
                    "under4.5": round(p.u45, 4),
                    "under5.5": round(p.u55, 4),
                    "under6.5": round(p.u65, 4),
                    "under7.5": round(p.u75, 4),
                    "under8.5": round(p.u85, 4),
                    "home_over1.5": round(p.homeOver15, 4),
                    "home_over2.5": round(p.homeOver25, 4),
                    "home_over3.5": round(p.homeOver35, 4),
                    "home_over4.5": round(p.homeOver45, 4),
                    "away_over1.5": round(p.awayOver15, 4),
                    "away_over2.5": round(p.awayOver25, 4),
                    "away_over3.5": round(p.awayOver35, 4),
                    "away_over4.5": round(p.awayOver45, 4),
                    "home_-1.5": round(p.homeHandi15, 4),
                    "away_-1.5": round(p.awayHandi15, 4),
                    "home/o4.5": round(p.homeAndOver45, 4),
                    "home/o5.5": round(p.homeAndOver55, 4),
                    "home/o6.5": round(p.homeAndOver65, 4),
                    "home/u4.5": round(p.homeAndUnder45, 4),
                    "home/u5.5": round(p.homeAndUnder55, 4),
                    "home/u6.5": round(p.homeAndUnder65, 4),
                    "away/o4.5": round(p.awayAndOver45, 4),
                    "away/o5.5": round(p.awayAndOver55, 4),
                    "away/o6.5": round(p.awayAndOver65, 4),
                    "away/u4.5": round(p.awayAndUnder45, 4),
                    "away/u5.5": round(p.awayAndUnder55, 4),
                    "away/u6.5": round(p.awayAndUnder65, 4),
                })
                print(
                    f"  {p.home_team} vs {p.away_team} ({p.date}): "
                    f"1ML={p.ML1:.2%} 2ML={p.ML2:.2%} over4.5={p.o45:.2%}"
                )

            if rows:
                self._save_predictions_csv(rows, PREDICTIONS_DIR, today)

            print(f"[KHL predict] Done — {len(rows)} games written")
        finally:
            db.close()

    def _games_to_dataframe(self, games):
        rows = []
        for g in games:
            rows.append({
                "game_id": g.khl_id,
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
                "HPK%": g.h_pk_pct,
                "APK%": g.a_pk_pct,
                "PK%Diff": g.pk_pct_diff,
                "HPMpG": g.h_pm_pg,
                "APMpG": g.a_pm_pg,
                "PMpGDiff": g.pm_pg_diff,
                "HPP%": g.h_pp_pct,
                "APP%": g.a_pp_pct,
                "PP%Diff": g.pp_pct_diff,
                "HPPGApG": g.h_ppg_apg,
                "APPGApG": g.a_ppg_apg,
                "PPGApGDiff": g.ppg_apg_diff,
                "HSV%": g.h_sv_pct,
                "ASV%": g.a_sv_pct,
                "SV%Diff": g.sv_pct_diff,
                "HSVpG": g.h_svpg,
                "ASVpG": g.a_svpg,
                "SVpGDiff": g.svpg_diff,
                "HSpG": g.h_spg,
                "ASpG": g.a_spg,
                "SpGDiff": g.spg_diff,
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
                "hom_score_no_ot": g.hom_score_no_ot,
            })
        return pd.DataFrame(rows)

    def _save_predictions_csv(self, rows, out_dir, today):
        os.makedirs(out_dir, exist_ok=True)
        filename = f"KHL-{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(out_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        print(f"[KHL predict] Saved predictions to {filepath}")
