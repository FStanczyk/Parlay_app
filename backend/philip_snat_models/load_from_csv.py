import csv
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame
from app.models.philip_snat_khl_game import PhilipSnatKhlGame
from app.models.philip_snat_shl_game import PhilipSnatShlGame
from app.models.philip_snat_nl_game import PhilipSnatNlGame

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


SHL_CSV_TO_MODEL = {
    "uuid": "shl_uuid",
    "date": "date",
    "home": "home_team",
    "away": "away_team",
    "winner": "winner",
    "homeScore": "home_score",
    "awayScore": "away_score",
    "homeScoreNoOT": "home_score_no_ot",
    "awayScoreNoOT": "away_score_no_ot",
    "totalGoals": "total_goals",
    "totalGoalsNoOT": "total_goals_no_ot",
    "OT": "ot",
    "SO": "so",
    "HomeRank": "home_rank",
    "AwayRank": "away_rank",
    "RankDiff": "rank_diff",
    "HGPG": "h_gpg",
    "AGPG": "a_gpg",
    "GPGDiff": "gpg_diff",
    "GPMutual": "gpmutual",
    "HGAPG": "h_gapg",
    "AGAPG": "a_gapg",
    "GAPGDiff": "gapg_diff",
    "GAPMutual": "gapmutual",
    "HPPPerc": "h_pp_perc",
    "APPPerc": "a_pp_perc",
    "HPKPerc": "h_pk_perc",
    "APKPerc": "a_pk_perc",
    "HSEff": "h_s_eff",
    "ASEff": "a_s_eff",
    "HSVSPerc": "h_svs_perc",
    "ASVSPerc": "a_svs_perc",
    "HFOPerc": "h_fo_perc",
    "AFOPerc": "a_fo_perc",
    "HCFPerc": "h_cf_perc",
    "ACFPerc": "a_cf_perc",
    "HFFPerc": "h_ff_perc",
    "AFFPerc": "a_ff_perc",
    "HCloseCFPerc": "h_close_cf_perc",
    "ACloseCFPerc": "a_close_cf_perc",
    "HCloseFFPerc": "h_close_ff_perc",
    "ACloseFFPerc": "a_close_ff_perc",
    "HPDO": "h_pdo",
    "APDO": "a_pdo",
    "HSTPerc": "h_st_perc",
    "ASTPerc": "a_st_perc",
    "HPPSEff": "h_pps_eff",
    "APPSEff": "a_pps_eff",
    "HSOGPG": "h_sogpg",
    "ASOGPG": "a_sogpg",
    "SOGPGDiff": "sogpg_diff",
    "SOGPGMutual": "sogpg_mutual",
    "HL5GW": "h_l5gw",
    "AL5GW": "a_l5gw",
    "L5GWDiff": "l5gw_diff",
    "HLmdGPG1": "h_lmd_gpg1",
    "ALmdGPG1": "a_lmd_gpg1",
    "HLmdGPG2": "h_lmd_gpg2",
    "ALmdGPG2": "a_lmd_gpg2",
    "HLmdGAPG1": "h_lmd_gapg1",
    "ALmdGAPG1": "a_lmd_gapg1",
    "HLmdGAPG2": "h_lmd_gapg2",
    "ALmdGAPG2": "a_lmd_gapg2",
    "HShameFactor": "h_shame_factor",
    "AShameFactor": "a_shame_factor",
    "HHungerFG": "h_hunger_fg",
    "AHungerFG": "a_hunger_fg",
    "HungerFGDiff": "hunger_fg_diff",
    "HungerFGMutual": "hunger_fg_mutual",
}

SHL_BOOL_FIELDS = {"ot", "so"}

SHL_NULLABLE_FIELDS = {
    "winner",
    "home_score",
    "away_score",
    "home_score_no_ot",
    "away_score_no_ot",
    "total_goals",
    "total_goals_no_ot",
    "ot",
    "so",
}


def _parse_shl_value(field: str, raw: str):
    if raw == "" or raw is None:
        return None
    if field == "date":
        return date.fromisoformat(raw.strip())
    if field in SHL_BOOL_FIELDS:
        raw_val = raw.strip()
        return raw_val.lower() in ("true", "1") or float(raw_val) == 1.0
    if field == "winner":
        raw_val = raw.strip()
        if raw_val == "":
            return None
        return int(float(raw_val))
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw.strip() or None


def load_shl_games_from_csv(csv_path: str, skip_existing: bool = True) -> None:
    path = Path(csv_path)
    if not path.exists():
        print(f"File not found: {csv_path}")
        return

    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        existing_shl_uuids: set[str] = set()
        if skip_existing:
            existing_shl_uuids = {
                row[0]
                for row in db.query(PhilipSnatShlGame.shl_uuid).all()
                if row[0] is not None
            }

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kwargs: dict = {}
                for csv_col, model_field in SHL_CSV_TO_MODEL.items():
                    raw = row.get(csv_col, "")
                    kwargs[model_field] = _parse_shl_value(model_field, raw)

                shl_uuid = kwargs.get("shl_uuid")
                if skip_existing and shl_uuid in existing_shl_uuids:
                    skipped += 1
                    continue

                game = PhilipSnatShlGame(**kwargs)
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


NL_CSV_TO_MODEL = {
    "game_id": "nl_id",
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
    "HGApG": "h_gapg",
    "AGApG": "a_gapg",
    "GApGDiff": "gapg_diff",
    "HSOGpG": "h_sogpg",
    "ASOGpG": "a_sogpg",
    "SOGpGDiff": "sogpg_diff",
    "HSSlotPG": "h_sslotpg",
    "ASSlotPG": "a_sslotpg",
    "SSlotPGDiff": "sslotpg_diff",
    "HSHMpG": "h_shmpg",
    "ASHMpG": "a_shmpg",
    "HMpGDiff": "hmpg_diff",
    "HSHPpG": "h_shppg",
    "ASHPpG": "a_shppg",
    "HPpGDiff": "hpppg_diff",
    "HPPGpG": "h_ppgpgg",
    "APPGpG": "a_ppgpgg",
    "PGpGDiff": "ppgpgg_diff",
    "HPPGApG": "h_ppgapg",
    "APPGApG": "a_ppgapg",
    "PPGApGDiff": "ppgapg_diff",
    "HPPGEff": "h_ppgeff",
    "APPGEff": "a_ppgeff",
    "PPGEffDiff": "ppgeff_diff",
    "HPKEff": "h_pkeff",
    "APKEff": "a_pkeff",
    "PKEffDiff": "pkeff_diff",
    "HSApG": "h_sapg",
    "ASApG": "a_sapg",
    "SApGDiff": "sapg_diff",
    "HSSlotApG": "h_sslotapg",
    "ASSlotApG": "a_sslotapg",
    "SSlotApGDiff": "sslotapg_diff",
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
}

NL_STRING_FIELDS = {
    "nl_id",
    "h_lgd",
    "a_lgd",
    "h_lgpa",
    "a_lgpa",
    "h_lgop",
    "a_lgop",
    "winner",
    "hour",
}

NL_BOOL_FIELDS = {"ot", "so"}

NL_NULLABLE_FIELDS = {
    "winner",
    "home_score",
    "away_score",
    "home_score_no_ot",
    "away_score_no_ot",
    "total_score",
    "total_score_no_ot",
    "ot",
    "so",
}


def _parse_nl_value(field: str, raw: str):
    if raw == "" or raw is None:
        return None
    if field == "date":
        return date.fromisoformat(raw.strip())
    if field in NL_BOOL_FIELDS:
        return raw.strip().lower() in ("true", "1")
    if field in NL_STRING_FIELDS:
        return raw.strip() or None
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw.strip() or None


def load_nl_games_from_csv(csv_path: str, skip_existing: bool = True) -> None:
    path = Path(csv_path)
    if not path.exists():
        print(f"File not found: {csv_path}")
        return

    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        existing_nl_ids: set[str] = set()
        if skip_existing:
            existing_nl_ids = {
                str(row[0])
                for row in db.query(PhilipSnatNlGame.nl_id).all()
                if row[0] is not None
            }

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kwargs: dict = {}
                for csv_col, model_field in NL_CSV_TO_MODEL.items():
                    raw = row.get(csv_col, "")
                    kwargs[model_field] = _parse_nl_value(model_field, raw)

                nl_id = kwargs.get("nl_id")
                if skip_existing and nl_id and str(nl_id) in existing_nl_ids:
                    skipped += 1
                    continue

                game = PhilipSnatNlGame(**kwargs)
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
        print("Usage: python load_from_csv.py <nhl|khl|shl|nl> <path_to_csv>")
        sys.exit(1)
    league = sys.argv[1].lower()
    csv_file = sys.argv[2]
    if league == "nhl":
        load_nhl_games_from_csv(csv_file)
    elif league == "khl":
        load_khl_games_from_csv(csv_file)
    elif league == "shl":
        load_shl_games_from_csv(csv_file)
    elif league == "nl":
        load_nl_games_from_csv(csv_file)
    else:
        print(f"Unknown league '{league}'. Use 'nhl', 'khl', 'shl', or 'nl'.")
        sys.exit(1)
