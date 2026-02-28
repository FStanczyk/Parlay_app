import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "..", "data", "games_khl.csv")

WINNER_STRATEGY = {
    "attributes": [
        "HRank", "ARank", "RankDiff",
        "HGpG", "AGpG", "GpGDiff",
        "HPK%", "APK%", "PK%Diff",
        "HPMpG", "APMpG", "PMpGDiff",
        "HPP%", "APP%", "PP%Diff",
        "HPPGApG", "APPGApG", "PPGApGDiff",
        "HSV%", "ASV%", "SV%Diff",
        "HSVpG", "ASVpG", "SVpGDiff",
        "HSpG", "ASpG", "SpGDiff",
        "HLGD", "ALGD", "HLGPA", "ALGPA", "HLGOP", "ALGOP", "LGOPDiff",
        "HL5GW", "AL5GW", "L5GWDiff",
        "hom_score_no_ot",
    ],
    "labels": ["winner"],
    "filePath": DATA_FILE,
    "name": "winner_model",
}

GOALS_STRATEGY = {
    "attributes": [
        "HRank", "ARank", "RankDiff",
        "HGpG", "AGpG", "GpGDiff",
        "HPK%", "APK%", "PK%Diff",
        "HPMpG", "APMpG", "PMpGDiff",
        "HPP%", "APP%", "PP%Diff",
        "HPPGApG", "APPGApG", "PPGApGDiff",
        "HSV%", "ASV%", "SV%Diff",
        "HSVpG", "ASVpG", "SVpGDiff",
        "HSpG", "ASpG", "SpGDiff",
        "HLGD", "ALGD", "HLGPA", "ALGPA", "HLGOP", "ALGOP", "LGOPDiff",
        "HL5GW", "AL5GW", "L5GWDiff",
        "hom_score_no_ot",
    ],
    "labels": ["total_score_no_ot", "home_score_no_ot", "away_score_no_ot"],
    "filePath": DATA_FILE,
    "name": "goals_model",
}


def time_to_minutes(time_str):
    if pd.isna(time_str) or time_str == "":
        return 0.0
    try:
        time_str = str(time_str)
        if ":" in time_str:
            parts = time_str.split(":")
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes + seconds / 60.0
        else:
            return float(time_str)
    except Exception:
        return 0.0


def normalize_dataframe(df, df_full=None, include_winner=False):
    if df_full is None:
        df_full = df

    df = df.copy()

    boolean_columns = ["OT", "SO"]
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool).astype(int)

    percentage_columns = [
        "HPK%", "APK%", "PK%Diff",
        "HPP%", "APP%", "PP%Diff",
        "HSV%", "ASV%", "SV%Diff",
    ]
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("%", "").astype(float)

    time_columns = ["HPMpG", "APMpG"]
    for col in time_columns:
        if col in df.columns:
            df[col] = df[col].apply(time_to_minutes)

    categorical_columns = ["HLGD", "ALGD", "HLGPA", "ALGPA", "HLGOP", "ALGOP"]
    if include_winner:
        categorical_columns.append("winner")

    for col in categorical_columns:
        if col in df.columns:
            all_unique_values = sorted(df_full[col].dropna().unique())
            label_encoder = {val: idx for idx, val in enumerate(all_unique_values)}
            df[col] = df[col].map(label_encoder).fillna(-1)

    return df


def getAttributes(strategy, split=None):
    df = pd.read_csv(strategy["filePath"])
    df = df.dropna(subset=["winner"])
    df = df[df["winner"].str.strip() != ""]
    df = normalize_dataframe(df, include_winner=True)

    attribute_columns = strategy["attributes"]
    available_attrs = [col for col in attribute_columns if col in df.columns]
    missing_attrs = [col for col in attribute_columns if col not in df.columns]

    if missing_attrs:
        print(f"Warning: Missing attribute columns: {missing_attrs}")

    X = df[available_attrs].copy()
    y = df[strategy["labels"]].copy()

    X = X.fillna(0)
    y = y.fillna(-1)

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    if isinstance(strategy["labels"], list) and len(strategy["labels"]) > 1:
        for col in y.columns:
            y[col] = pd.to_numeric(y[col], errors="coerce").fillna(-1)
    else:
        y = pd.to_numeric(y[strategy["labels"][0]], errors="coerce").fillna(-1)

    if split is None:
        train_attr = X.values if isinstance(X, pd.DataFrame) else X
        test_attr = np.array([]).reshape(0, len(available_attrs))
        train_labels = y.values if isinstance(y, pd.Series) else y
        test_labels = np.array([])
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=split, random_state=42, shuffle=True
        )
        train_attr = X_train.values if isinstance(X_train, pd.DataFrame) else X_train
        test_attr = X_test.values if isinstance(X_test, pd.DataFrame) else X_test
        train_labels = y_train.values if isinstance(y_train, pd.Series) else y_train
        test_labels = y_test.values if isinstance(y_test, pd.Series) else y_test

    return train_attr, test_attr, train_labels, test_labels


def get_games_to_predict(strategy):
    df = pd.read_csv(strategy["filePath"])
    return get_games_to_predict_df(strategy, df)


def get_games_to_predict_df(strategy, df):
    games_to_predict = []
    for idx in range(len(df) - 1, -1, -1):
        row = df.iloc[idx]
        winner = row["winner"]
        if pd.isna(winner) or str(winner).strip() == "":
            games_to_predict.append(idx)
        else:
            break

    if not games_to_predict:
        return pd.DataFrame(), pd.DataFrame()

    games_to_predict.reverse()
    df_predict = df.iloc[games_to_predict].copy()
    df_predict = normalize_dataframe(df_predict, df_full=df, include_winner=False)

    attribute_columns = strategy["attributes"]
    available_attrs = [col for col in attribute_columns if col in df_predict.columns]

    X = df_predict[available_attrs].copy()
    X = X.fillna(0)

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    return X, df_predict


def merge_predictions(dict1, dict2):
    winner_dict = dict1
    goals_dict = dict2

    if dict1 and any("total_goals" in pred.keys() for pred in dict1.values()):
        winner_dict = dict2
        goals_dict = dict1

    merged = goals_dict.copy()

    for game_id, winner_pred in winner_dict.items():
        winner_value = winner_pred.get("winner")
        if game_id in merged:
            merged[game_id]["winner"] = winner_value
        else:
            merged[game_id] = {
                "home_team": winner_pred["home_team"],
                "away_team": winner_pred["away_team"],
                "date": winner_pred["date"],
                "total_goals": {},
                "home_goals": {},
                "away_goals": {},
                "winner": winner_value,
            }

    return merged
