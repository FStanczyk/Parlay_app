import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame

CSV_TO_MODEL = {
    "id": "nhl_id",
    "date": "date",
    "home": "home_team",
    "away": "away_team",
    "winner": "winner",
    "homeGoals_noOT": "home_goals_no_ot",
    "awayGoals_noOT": "away_goals_no_ot",
    "total_noOT": "total_goals_no_ot",
    "homeStanding": "home_standing",
    "awayStanding": "away_standing",
    "standingDifference": "diff_standing",
    "homeGpG": "home_gpg",
    "awayGpG": "away_gpg",
    "GpGMutual": "mutual_gpg",
    "GpGDiff": "diff_gpg",
    "homeLGpG": "home_gpga",
    "awayLGpG": "away_gpga",
    "LGpGDiff": "diff_gpga",
    "SVhome": "home_sv",
    "SVaway": "away_sv",
    "SVDiff": "diff_sv",
    "LGDhome": "home_lgd",
    "LGDaway": "away_lgd",
    "LGPAhome": "home_lgpa",
    "LGPAaway": "away_lgpa",
    "LGOPhome": "home_lgop",
    "LGOPaway": "away_lgop",
    "SFHome": "home_shame_factor",
    "SFAway": "away_shame_factor",
    "SFOutcome": "outcome_shame_factor",
    "L5GWHome": "home_l5gw",
    "L5GWAway": "away_l5gw",
    "L5GWDiff": "diff_l5gw",
    "DFLGHome": "home_dflg",
    "DFLGAway": "away_dflg",
    "LGOTHome": "home_lgot",
    "LGOTAway": "away_lgot",
    "LGSOHome": "home_lgso",
    "LGSOAway": "away_lgso",
    "lmd1Home": "home_lmd1",
    "lmd1Away": "away_lmd1",
    "lmd1Mutual": "lmd1_mutual",
    "lmd2Home": "home_lmd2",
    "lmd2Away": "away_lmd2",
    "homeSpG": "home_spg",
    "awaySpG": "away_spg",
    "homeSpGA": "home_spga",
    "awaySpGA": "away_spga",
    "hungerFG": "hunger_fg",
    "HomeFatigue": "home_fatigue",
    "AwayFatigue": "away_fatigue",
}

BOOL_FIELDS = {"home_lgot", "away_lgot", "home_lgso", "away_lgso"}
NULLABLE_FIELDS = {
    "winner",
    "home_goals_no_ot",
    "away_goals_no_ot",
    "total_goals_no_ot",
    "ai_predicted_winner",
    "ai_predicted_home_goals",
    "ai_predicted_away_goals",
    "ai_predicted_total_goals",
}


def _parse_value(field: str, raw: str):
    if raw == "" or raw is None:
        return None
    if field == "date":
        return date.fromisoformat(raw)
    if field in BOOL_FIELDS:
        return raw.strip() == "1"
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def load_nhl_games_from_csv(csv_path: str, skip_existing: bool = True) -> None:
    path = Path(csv_path)
    if not path.exists():
        print(f"File not found: {csv_path}")
        return

    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        existing_nhl_ids: set[int] = set()
        if skip_existing:
            existing_nhl_ids = {
                row[0]
                for row in db.query(PhilipSnatNhlGame.nhl_id).all()
                if row[0] is not None
            }

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kwargs: dict = {}
                for csv_col, model_field in CSV_TO_MODEL.items():
                    raw = row.get(csv_col, "")
                    kwargs[model_field] = _parse_value(model_field, raw)

                nhl_id = kwargs.get("nhl_id")
                if skip_existing and nhl_id in existing_nhl_ids:
                    skipped += 1
                    continue

                game = PhilipSnatNhlGame(**kwargs)
                db.add(game)
                inserted += 1

        db.commit()
        print(f"Done — inserted: {inserted}, skipped (already exist): {skipped}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_from_csv.py <path_to_csv>")
        sys.exit(1)
    load_nhl_games_from_csv(sys.argv[1])
