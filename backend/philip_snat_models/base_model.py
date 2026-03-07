import csv
import os
from datetime import date, datetime, timedelta, timezone
from abc import ABC

from app.core.database import SessionLocal
from app.models.philip_snat_league import PhilipSnatLeague
from app.models.philip_snat_ai_model import PhilipSnatAiModel
from philip_snat_models.model_interface import AiModelInterface


class BaseAiModel(AiModelInterface, ABC):
    def _get_or_create_league(self, db):
        league = (
            db.query(PhilipSnatLeague)
            .filter(PhilipSnatLeague.name == self.LEAGUE_NAME)
            .first()
        )
        if not league:
            league = PhilipSnatLeague(
                name=self.LEAGUE_NAME, update=True, download=True, predict=True
            )
            db.add(league)
            db.commit()
            db.refresh(league)
        return league

    def _record_model_load(self, db, league_id, model_name):
        record = (
            db.query(PhilipSnatAiModel)
            .filter(
                PhilipSnatAiModel.philip_snat_league_id == league_id,
                PhilipSnatAiModel.name == model_name,
            )
            .first()
        )
        now = datetime.now(timezone.utc)
        if not record:
            record = PhilipSnatAiModel(
                philip_snat_league_id=league_id,
                name=model_name,
                last_update=now,
            )
            db.add(record)
        else:
            record.last_update = now
        db.commit()

    @staticmethod
    def _save_predictions_csv(rows, out_dir, league_name, today_date, csv_headers):
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, f"{league_name}-{today_date}.csv")

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: f"{v:.4f}" if isinstance(v, float) else v
                        for k, v in row.items()
                    }
                )
        print(f"[predict] Saved predictions → {file_path}")

    @staticmethod
    def _cleanup_old_files(out_dir, days=3):
        if not os.path.isdir(out_dir):
            return
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        for fname in os.listdir(out_dir):
            if fname.endswith(".csv"):
                fp = os.path.join(out_dir, fname)
                if datetime.fromtimestamp(os.path.getmtime(fp)) < cutoff:
                    os.remove(fp)
                    removed += 1
        if removed:
            print(f"[predict] Removed {removed} old prediction file(s)")

    @staticmethod
    def _save_prediction_to_db(
        db, table_name, game_id, prediction_winner, prediction_goals
    ):
        try:
            from sqlalchemy import Table, MetaData

            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=db.bind)
            db.execute(
                table.update()
                .where(table.c.id == game_id)
                .values(
                    prediction_winner=prediction_winner,
                    prediction_goals=prediction_goals,
                )
            )
            db.commit()
        except Exception as db_error:
            print(f"  Error saving predictions for game {game_id}: {db_error}")
            db.rollback()
            raise
