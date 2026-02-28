import csv
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame
from app.models.philip_snat_khl_game import PhilipSnatKhlGame

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


KHL_CSV_TO_MODEL = {
    "game_id": "khl_id",
    "date": "date",
    "hour": "hour",
    "home_team": "home_team",
    "away_team": "away_team",
    "winner": "winner",
    "home_score": "home_score",
    "away_score": "away_score",
    "home_score_no_ot": "home_score_no_ot",
    "away_score_no_ot": "away_score_no_ot",
    "total_score": "total_score",
    "total_score_no_ot": "total_score_no_ot",
    "OT": "ot",
    "SO": "so",
    "HRank": "h_rank",
    "ARank": "a_rank",
    "RankDiff": "rank_diff",
    "HGpG": "h_gpg",
    "AGpG": "a_gpg",
    "GpGDiff": "gpg_diff",
    "HPK%": "h_pk_pct",
    "APK%": "a_pk_pct",
    "PK%Diff": "pk_pct_diff",
    "HPMpG": "h_pm_pg",
    "APMpG": "a_pm_pg",
    "PMpGDiff": "pm_pg_diff",
    "HPP%": "h_pp_pct",
    "APP%": "a_pp_pct",
    "PP%Diff": "pp_pct_diff",
    "HPPGApG": "h_ppg_apg",
    "APPGApG": "a_ppg_apg",
    "PPGApGDiff": "ppg_apg_diff",
    "HSV%": "h_sv_pct",
    "ASV%": "a_sv_pct",
    "SV%Diff": "sv_pct_diff",
    "HSVpG": "h_svpg",
    "ASVpG": "a_svpg",
    "SVpGDiff": "svpg_diff",
    "HSpG": "h_spg",
    "ASpG": "a_spg",
    "SpGDiff": "spg_diff",
    "HLGD": "h_lgd",
    "ALGD": "a_lgd",
    "HLGPA": "h_lgpa",
    "ALGPA": "a_lgpa",
    "HLGOP": "h_lgop",
    "ALGOP": "a_lgop",
    "LGOPDiff": "lgop_diff",
    "HL5GW": "h_l5gw",
    "AL5GW": "a_l5gw",
    "L5GWDiff": "l5gw_diff",
    "hom_score_no_ot": "hom_score_no_ot",
}

KHL_STRING_FIELDS = {
    "h_pk_pct",
    "a_pk_pct",
    "h_pm_pg",
    "a_pm_pg",
    "h_pp_pct",
    "a_pp_pct",
    "h_sv_pct",
    "a_sv_pct",
    "h_lgd",
    "a_lgd",
    "h_lgpa",
    "a_lgpa",
    "h_lgop",
    "a_lgop",
    "winner",
    "hour",
}

KHL_BOOL_FIELDS = {"ot", "so"}

KHL_NULLABLE_FIELDS = {
    "winner",
    "home_score",
    "away_score",
    "home_score_no_ot",
    "away_score_no_ot",
    "total_score",
    "total_score_no_ot",
    "ot",
    "so",
    "hom_score_no_ot",
}


def _parse_khl_value(field: str, raw: str):
    if raw == "" or raw is None:
        return None
    if field == "date":
        return datetime.strptime(raw.strip(), "%d-%m-%Y").date()
    if field in KHL_BOOL_FIELDS:
        return raw.strip().lower() in ("true", "1")
    if field in KHL_STRING_FIELDS:
        return raw.strip() or None
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw.strip() or None


def load_khl_games_from_csv(csv_path: str, skip_existing: bool = True) -> None:
    path = Path(csv_path)
    if not path.exists():
        print(f"File not found: {csv_path}")
        return

    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        existing_khl_ids: set[int] = set()
        if skip_existing:
            existing_khl_ids = {
                row[0]
                for row in db.query(PhilipSnatKhlGame.khl_id).all()
                if row[0] is not None
            }

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kwargs: dict = {}
                for csv_col, model_field in KHL_CSV_TO_MODEL.items():
                    raw = row.get(csv_col, "")
                    kwargs[model_field] = _parse_khl_value(model_field, raw)

                khl_id = kwargs.get("khl_id")
                if skip_existing and khl_id in existing_khl_ids:
                    skipped += 1
                    continue

                game = PhilipSnatKhlGame(**kwargs)
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
    if len(sys.argv) < 3:
        print("Usage: python load_from_csv.py <nhl|khl> <path_to_csv>")
        sys.exit(1)
    league = sys.argv[1].lower()
    csv_file = sys.argv[2]
    if league == "nhl":
        load_nhl_games_from_csv(csv_file)
    elif league == "khl":
        load_khl_games_from_csv(csv_file)
    else:
        print(f"Unknown league '{league}'. Use 'nhl' or 'khl'.")
        sys.exit(1)
