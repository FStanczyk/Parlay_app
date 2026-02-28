import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.philip_snat_league import PhilipSnatLeague
from philip_snat_models.nhl.model import NhlAiModel
from philip_snat_models.khl.model import KhlAiModel

ALL_MODELS = [
    NhlAiModel,
    KhlAiModel,
]

if __name__ == "__main__":
    db = SessionLocal()
    try:
        leagues = {row.name: row for row in db.query(PhilipSnatLeague).all()}
    finally:
        db.close()

    for ModelClass in ALL_MODELS:
        league = leagues.get(ModelClass.LEAGUE_NAME)
        if league is None:
            print(f"[{ModelClass.LEAGUE_NAME}] No league row found in DB, skipping")
            continue

        model = ModelClass()

        if league.update:
            print(f"=== [{league.name}] update_games ===")
            model.update_games()

        if league.download:
            print(f"=== [{league.name}] download_new_games ===")
            model.download_new_games()

        if league.predict:
            print(f"=== [{league.name}] predict ===")
            model.predict()
