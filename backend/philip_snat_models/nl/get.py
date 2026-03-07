from datetime import date
from app.core.database import SessionLocal
from app.models.philip_snat_nl_game import PhilipSnatNlGame


class NlGetter:
    def fill_finished_games(self):
        db = SessionLocal()
        try:
            today = date.today()
            games = (
                db.query(PhilipSnatNlGame)
                .filter(
                    PhilipSnatNlGame.winner.is_(None),
                    PhilipSnatNlGame.date < today,
                )
                .all()
            )
            print(f"[fill_finished_games] Found {len(games)} unresolved past games")
            print(
                "[fill_finished_games] Note: This requires external API integration to fill game results"
            )
        finally:
            db.close()

    def get_new_games(self, for_tomorrow=False):
        db = SessionLocal()
        try:
            print(
                "[get_new_games] Note: This requires external API integration to fetch new games"
            )
        finally:
            db.close()
