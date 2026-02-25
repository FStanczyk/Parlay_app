import csv
import os
import joblib
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn import svm, tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression
from datetime import date, datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame
from app.models.philip_snat_league import PhilipSnatLeague
from app.models.philip_snat_ai_model import PhilipSnatAiModel
from philip_snat_models.model_interface import AiModelInterface
from philip_snat_models.nhl.get import NhlGetter
from philip_snat_models.nhl.algorithms import run_ensemble, average_distributions

MODEL_NAMES = ["WINNER_MODEL"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "pytorch_models")
SCALERS_DIR = os.path.join(BASE_DIR, "scalers")
TRAINING_CSV = os.path.join(BASE_DIR, "..", "assets", "merge_no_missing.csv")

WINNER_FEATURES = [
    "diff_l5gw",
    "diff_standing",
    "diff_gpg",
    "away_l5gw",
    "diff_gpga",
    "home_l5gw",
    "outcome_shame_factor",
    "away_gpg",
    "home_gpga",
    "diff_sv",
    "home_shame_factor",
    "home_gpg",
    "away_gpga",
    "away_shame_factor",
    "home_sv",
    "away_spg",
    "away_spga",
    "away_lmd1",
    "home_spg",
    "away_sv",
    "home_spga",
    "away_lmd2",
    "home_lmd1",
    "home_lgop",
    "home_lgd",
]

# CSV column names for training data (UNIVERSAL_COLUMN_ORDER indices)
# GOALS: attrCols [11,12,38,25,39,42,47,48], labelCol=7
GOALS_CSV_COLS = [
    "homeGpG",
    "awayGpG",
    "lmd1Home",
    "SFOutcome",
    "lmd1Away",
    "homeSpG",
    "lmd1Mutual",
    "GpGMutual",
]
GOALS_LABEL_COL = "total_noOT"

# HOME_GOALS: attrCols [11,12,14,17,21,28,29,38,40,41,47], labelCol=5
HOME_GOALS_CSV_COLS = [
    "homeGpG",
    "awayGpG",
    "awayLGpG",
    "LGDhome",
    "LGOPhome",
    "L5GWDiff",
    "GpGDiff",
    "lmd1Home",
    "lmd2Home",
    "lmd2Away",
    "lmd1Mutual",
]
HOME_GOALS_LABEL_COL = "homeGoals_noOT"

# AWAY_GOALS: attrCols [11,12,13,18,23,27,28,29,30,39,48], labelCol=6
AWAY_GOALS_CSV_COLS = [
    "homeGpG",
    "awayGpG",
    "homeLGpG",
    "LGDaway",
    "SFHome",
    "L5GWAway",
    "L5GWDiff",
    "GpGDiff",
    "LGpGDiff",
    "lmd1Away",
    "GpGMutual",
]
AWAY_GOALS_LABEL_COL = "awayGoals_noOT"

# DB field names matching CSV columns (same order as CSV cols above)
GOALS_DB_FEATURES = [
    "home_gpg",
    "away_gpg",
    "home_lmd1",
    "outcome_shame_factor",
    "away_lmd1",
    "home_spg",
    "lmd1_mutual",
    "mutual_gpg",
]
HOME_GOALS_DB_FEATURES = [
    "home_gpg",
    "away_gpg",
    "away_gpga",
    "home_lgd",
    "home_lgop",
    "diff_l5gw",
    "diff_gpg",
    "home_lmd1",
    "home_lmd2",
    "away_lmd2",
    "lmd1_mutual",
]
AWAY_GOALS_DB_FEATURES = [
    "home_gpg",
    "away_gpg",
    "home_gpga",
    "away_lgd",
    "home_shame_factor",
    "away_l5gw",
    "diff_l5gw",
    "diff_gpg",
    "diff_gpga",
    "away_lmd1",
    "mutual_gpg",
]

TOTAL_GOALS_KEYS = [str(i) for i in range(13)]
TEAM_GOALS_KEYS = [str(i) for i in range(8)]

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
    "over4.5",
    "over5.5",
    "over6.5",
    "over7.5",
    "over8.5",
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
    "home/o5.5",
    "home/o6.5",
    "home/u5.5",
    "home/u6.5",
    "away/o5.5",
    "away/o6.5",
    "away/u5.5",
    "away/u6.5",
]


class _WinnerModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(len(WINNER_FEATURES), 6)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.1)
        self.fc2 = nn.Linear(6, 1)
        self.sigm2 = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = self.sigm2(x)
        return x


def _fit_ensemble(attr, labels):
    print(f"[ensemble] Training on {len(attr)} samples, {len(set(labels))} classes...")
    models = {}

    _svm = svm.SVC(kernel="rbf", C=300, gamma=0.01, probability=True)
    _svm.fit(attr, labels)
    models["svm"] = _svm

    _knn = KNeighborsClassifier(n_neighbors=17)
    _knn.fit(attr, labels)
    models["knn"] = _knn

    _dt = tree.DecisionTreeClassifier(max_depth=5, min_samples_split=40)
    _dt.fit(attr, labels)
    models["dt"] = _dt

    _gbdt = GradientBoostingClassifier(n_estimators=100, learning_rate=0.01)
    _gbdt.fit(attr, labels)
    models["gbdt"] = _gbdt

    _rf = RandomForestClassifier(n_estimators=100, min_samples_split=2)
    _rf.fit(attr, labels)
    models["rf"] = _rf

    _et = ExtraTreesClassifier(n_estimators=100, max_depth=14)
    _et.fit(attr, labels)
    models["et"] = _et

    _absvm = AdaBoostClassifier(n_estimators=300, learning_rate=0.05)
    _absvm.fit(attr, labels)
    models["absvm"] = _absvm

    _lr = LogisticRegression(solver="lbfgs", max_iter=10000)
    _lr.fit(attr, labels)
    models["lr"] = _lr

    print(f"[ensemble] Done training {len(models)} classifiers")
    return models


class NhlAiModel(AiModelInterface):

    LEAGUE_NAME = "NHL"

    def __init__(self):
        self.getter = NhlGetter()
        self._winner_model = None
        self._winner_scaler = None
        self._goals_models = None
        self._home_goals_models = None
        self._away_goals_models = None

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

    def _load_models(self):
        if self._winner_model is not None:
            return

        winner = _WinnerModel()
        winner.load_state_dict(
            torch.load(os.path.join(MODELS_DIR, "WINNER_MODEL"), map_location="cpu")
        )
        winner.eval()
        self._winner_model = winner
        self._winner_scaler = joblib.load(
            os.path.join(SCALERS_DIR, "scaler_winner.save")
        )

        self._train_goal_ensembles()

        db = SessionLocal()
        try:
            league = self._get_or_create_league(db)
            for name in MODEL_NAMES:
                self._record_model_load(db, league.id, name)
            print(f"[models] Loaded under league '{self.LEAGUE_NAME}'")
        finally:
            db.close()

    def _train_goal_ensembles(self):
        if not os.path.exists(TRAINING_CSV):
            raise FileNotFoundError(f"Training CSV not found: {TRAINING_CSV}")

        df = pd.read_csv(TRAINING_CSV)
        df = df.dropna(
            subset=[GOALS_LABEL_COL, HOME_GOALS_LABEL_COL, AWAY_GOALS_LABEL_COL]
        )
        print(f"[train] {len(df)} rows from {TRAINING_CSV}")

        goals_df = df.dropna(subset=GOALS_CSV_COLS)
        goals_attr = goals_df[GOALS_CSV_COLS].values.astype(float)
        goals_labels = goals_df[GOALS_LABEL_COL].astype(int).values.clip(0, 12)
        print(f"[train] GOALS: {len(goals_df)} samples")
        self._goals_models = _fit_ensemble(goals_attr, goals_labels)

        home_df = df.dropna(subset=HOME_GOALS_CSV_COLS)
        home_attr = home_df[HOME_GOALS_CSV_COLS].values.astype(float)
        home_labels = home_df[HOME_GOALS_LABEL_COL].astype(int).values.clip(0, 6)
        print(f"[train] HOME_GOALS: {len(home_df)} samples")
        self._home_goals_models = _fit_ensemble(home_attr, home_labels)

        away_df = df.dropna(subset=AWAY_GOALS_CSV_COLS)
        away_attr = away_df[AWAY_GOALS_CSV_COLS].values.astype(float)
        away_labels = away_df[AWAY_GOALS_LABEL_COL].astype(int).values.clip(0, 6)
        print(f"[train] AWAY_GOALS: {len(away_df)} samples")
        self._away_goals_models = _fit_ensemble(away_attr, away_labels)

    @staticmethod
    def _extract(game, fields):
        values = []
        for f in fields:
            v = getattr(game, f)
            if v is None:
                return None
            values.append(float(v))
        return values

    @staticmethod
    def _compute_odds(winner_prob, home_means, away_means, total_means):
        home_pct = 1.0 - winner_prob
        away_pct = winner_prob

        prob_home_win = 0.0
        prob_away_win = 0.0
        prob_draw = 0.0
        prob_home_win_by_1_5_plus = 0.0
        prob_away_win_by_1_5_plus = 0.0

        for hg in TEAM_GOALS_KEYS:
            for ag in TEAM_GOALS_KEYS:
                ph = home_means.get(hg, 0.0)
                pa = away_means.get(ag, 0.0)
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

        o["over4.5"] = 1.0 - sum(total_means.get(str(i), 0.0) for i in range(5))
        o["over5.5"] = 1.0 - sum(total_means.get(str(i), 0.0) for i in range(6))
        o["over6.5"] = 1.0 - sum(total_means.get(str(i), 0.0) for i in range(7))
        o["over7.5"] = 1.0 - sum(total_means.get(str(i), 0.0) for i in range(8))
        o["over8.5"] = 1.0 - sum(total_means.get(str(i), 0.0) for i in range(9))

        o["under4.5"] = sum(total_means.get(str(i), 0.0) for i in range(5))
        o["under5.5"] = sum(total_means.get(str(i), 0.0) for i in range(6))
        o["under6.5"] = sum(total_means.get(str(i), 0.0) for i in range(7))
        o["under7.5"] = sum(total_means.get(str(i), 0.0) for i in range(8))
        o["under8.5"] = sum(total_means.get(str(i), 0.0) for i in range(9))

        o["home_over1.5"] = 1.0 - sum(home_means.get(str(i), 0.0) for i in range(2))
        o["home_over2.5"] = 1.0 - sum(home_means.get(str(i), 0.0) for i in range(3))
        o["home_over3.5"] = 1.0 - sum(home_means.get(str(i), 0.0) for i in range(4))
        o["home_over4.5"] = 1.0 - sum(home_means.get(str(i), 0.0) for i in range(5))

        o["away_over1.5"] = 1.0 - sum(away_means.get(str(i), 0.0) for i in range(2))
        o["away_over2.5"] = 1.0 - sum(away_means.get(str(i), 0.0) for i in range(3))
        o["away_over3.5"] = 1.0 - sum(away_means.get(str(i), 0.0) for i in range(4))
        o["away_over4.5"] = 1.0 - sum(away_means.get(str(i), 0.0) for i in range(5))

        o["home_-1.5"] = prob_home_win_by_1_5_plus
        o["away_-1.5"] = prob_away_win_by_1_5_plus

        o["home/o5.5"] = o["over5.5"] * o["1"]
        o["home/o6.5"] = o["over6.5"] * o["1"]
        o["home/u5.5"] = o["under5.5"] * o["1"]
        o["home/u6.5"] = o["under6.5"] * o["1"]
        o["away/o5.5"] = o["over5.5"] * o["2"]
        o["away/o6.5"] = o["over6.5"] * o["2"]
        o["away/u5.5"] = o["under5.5"] * o["2"]
        o["away/u6.5"] = o["under6.5"] * o["2"]

        return o

    @staticmethod
    def _save_predictions_csv(rows, out_dir, league_name, today):
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, f"{league_name}-{today}.csv")

        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
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

    def update_games(self):
        db = SessionLocal()
        try:
            today = date.today()
            games = (
                db.query(PhilipSnatNhlGame)
                .filter(
                    PhilipSnatNhlGame.winner.is_(None), PhilipSnatNhlGame.date < today
                )
                .all()
            )
            print(f"[update_games] Found {len(games)} unresolved past games")

            filled = 0
            for game in games:
                try:
                    data = self.getter.get_game_boxscore(game.nhl_id)
                    home_team = data.get("homeTeam", {})
                    away_team = data.get("awayTeam", {})

                    if "score" not in home_team or "score" not in away_team:
                        print(f"  Game {game.nhl_id} still has no scores, skipping")
                        continue

                    h_score = home_team["score"]
                    a_score = away_team["score"]
                    period = data.get("periodDescriptor", {}).get("number", 3)
                    overtime = period > 3

                    h_goals = h_score
                    a_goals = a_score
                    total = h_score + a_score

                    if overtime:
                        total -= 1
                        if h_score > a_score:
                            h_goals -= 1
                        else:
                            a_goals -= 1

                    game.winner = 0 if h_goals > a_goals else 1
                    game.home_goals_no_ot = h_goals
                    game.away_goals_no_ot = a_goals
                    game.total_goals_no_ot = total
                    db.commit()

                    print(
                        f"  Updated {game.home_team} {h_goals} - {a_goals} {game.away_team} (winner={game.winner})"
                    )
                    filled += 1

                except Exception as e:
                    db.rollback()
                    print(f"  Error updating game {game.nhl_id}: {e}")

            print(f"[update_games] Done — filled {filled}/{len(games)}")
        finally:
            db.close()

    def download_new_games(self):
        db = SessionLocal()
        try:
            today = datetime.strptime(self.getter.today(), "%Y-%m-%d")
            dates = [today, today + timedelta(days=1)]

            print(
                f"[download_new_games] Scanning {dates[0].date()} and {dates[1].date()}"
            )
            inserted = 0

            for current in dates:
                date_str = current.strftime("%Y-%m-%d")
                try:
                    games_on_day = self.getter.get_schedule(date_str)
                except Exception as e:
                    print(f"  Could not fetch schedule for {date_str}: {e}")
                    continue

                print(f"  {date_str}: {len(games_on_day)} games")

                for game in games_on_day:
                    if game.get("gameType") != 2:
                        continue

                    game_id = game["id"]
                    existing = (
                        db.query(PhilipSnatNhlGame)
                        .filter(PhilipSnatNhlGame.nhl_id == game_id)
                        .first()
                    )
                    if existing:
                        continue

                    home_id = game["homeTeam"]["id"]
                    away_id = game["awayTeam"]["id"]
                    try:
                        home_name = self.getter.get_team_name(home_id)
                        away_name = self.getter.get_team_name(away_id)
                    except KeyError:
                        print(f"  Unknown team id in game {game_id}, skipping")
                        continue

                    print(f"  Processing {home_name} vs {away_name} ({date_str})")
                    features = self.getter.build_game_features(game, date_str)
                    if features is None:
                        continue

                    db.add(PhilipSnatNhlGame(**features))
                    db.commit()
                    inserted += 1

            print(f"[download_new_games] Done — inserted {inserted} new games")
        finally:
            db.close()

    def predict(self):
        self._load_models()
        db = SessionLocal()
        try:
            league = (
                db.query(PhilipSnatLeague)
                .filter(PhilipSnatLeague.name == self.LEAGUE_NAME)
                .first()
            )
            predictions_path = league.predictions_path if league else None

            today = date.today()
            games = (
                db.query(PhilipSnatNhlGame)
                .filter(
                    PhilipSnatNhlGame.winner.is_(None),
                    PhilipSnatNhlGame.date >= today,
                )
                .all()
            )
            print(f"[predict] Found {len(games)} upcoming games")

            rows = []
            for game in games:
                winner_feats = self._extract(game, WINNER_FEATURES)
                goals_feats = self._extract(game, GOALS_DB_FEATURES)
                home_goals_feats = self._extract(game, HOME_GOALS_DB_FEATURES)
                away_goals_feats = self._extract(game, AWAY_GOALS_DB_FEATURES)

                if any(
                    f is None
                    for f in [
                        winner_feats,
                        goals_feats,
                        home_goals_feats,
                        away_goals_feats,
                    ]
                ):
                    print(f"  Game {game.nhl_id}: missing features, skipping")
                    continue

                try:
                    winner_scaled = self._winner_scaler.transform([winner_feats])
                    with torch.inference_mode():
                        winner_prob = float(
                            self._winner_model(torch.FloatTensor(winner_scaled))[0][0]
                        )

                    goals_preds = run_ensemble(goals_feats, self._goals_models)
                    home_preds = run_ensemble(home_goals_feats, self._home_goals_models)
                    away_preds = run_ensemble(away_goals_feats, self._away_goals_models)

                    total_means = average_distributions(goals_preds, TOTAL_GOALS_KEYS)
                    home_means = average_distributions(home_preds, TEAM_GOALS_KEYS)
                    away_means = average_distributions(away_preds, TEAM_GOALS_KEYS)

                    odds = self._compute_odds(
                        winner_prob, home_means, away_means, total_means
                    )

                    rows.append(
                        {
                            "date": str(game.date),
                            "home": game.home_team,
                            "away": game.away_team,
                            **odds,
                        }
                    )
                    print(
                        f"  {game.home_team} vs {game.away_team} ({game.date}): "
                        f"1ML={odds['1ML']:.2%} 2ML={odds['2ML']:.2%} "
                        f"over5.5={odds['over5.5']:.2%}"
                    )

                except Exception as e:
                    print(f"  Error predicting game {game.nhl_id}: {e}")

            if rows and predictions_path:
                out_dir = os.path.join(
                    BASE_DIR, "..", predictions_path.split("/", 1)[-1]
                )
                out_dir = os.path.normpath(out_dir)
                self._save_predictions_csv(rows, out_dir, self.LEAGUE_NAME, today)
                self._cleanup_old_files(out_dir)
            elif rows:
                print("[predict] No predictions_path set on league, skipping CSV write")

            print(f"[predict] Done — {len(rows)} games written")
        finally:
            db.close()
