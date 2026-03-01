import fcntl
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

LOCK_FILE = "/tmp/philip_snat_runner.lock"

if __name__ == "__main__":
    _lock_fh = open(LOCK_FILE, "w")
    try:
        fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[runner] Another instance is already running — exiting.")
        sys.exit(0)

    try:
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
    finally:
        fcntl.flock(_lock_fh, fcntl.LOCK_UN)
        _lock_fh.close()
