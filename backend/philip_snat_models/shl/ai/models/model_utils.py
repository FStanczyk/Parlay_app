import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "..", "..", "..", "assets", "shl_games.csv")

WINNER_STRATEGY = {
    "attributes": [
        "HomeRank", "AwayRank", "RankDiff",
        "HGPG", "AGPG", "GPGDiff", "GPMutual",
        "HGAPG", "AGAPG", "GAPGDiff", "GAPMutual",
        "HPPPerc", "APPPerc", "HPKPerc", "APKPerc",
        "HSEff", "ASEff", "HSVSPerc", "ASVSPerc",
        "HFOPerc", "AFOPerc", "HCFPerc", "ACFPerc",
        "HFFPerc", "AFFPerc", "HCloseCFPerc", "ACloseCFPerc",
        "HCloseFFPerc", "ACloseFFPerc", "HPDO", "APDO",
        "HSTPerc", "ASTPerc", "HPPSEff", "APPSEff",
        "HSOGPG", "ASOGPG", "SOGPGDiff", "SOGPGMutual",
        "HL5GW", "AL5GW", "L5GWDiff",
        "HLmdGPG1", "ALmdGPG1", "HLmdGPG2", "ALmdGPG2",
        "HLmdGAPG1", "ALmdGAPG1", "HLmdGAPG2", "ALmdGAPG2",
        "HShameFactor", "AShameFactor",
        "HHungerFG", "AHungerFG", "HungerFGDiff", "HungerFGMutual",
    ],
    "labels": ["winner"],
    "filePath": DATA_FILE,
    "name": "winner_model",
}

GOALS_STRATEGY = {
    "attributes": [
        "HomeRank", "AwayRank", "RankDiff",
        "HGPG", "AGPG", "GPGDiff", "GPMutual",
        "HGAPG", "AGAPG", "GAPGDiff", "GAPMutual",
        "HPPPerc", "APPPerc", "HPKPerc", "APKPerc",
        "HSEff", "ASEff", "HSVSPerc", "ASVSPerc",
        "HFOPerc", "AFOPerc", "HCFPerc", "ACFPerc",
        "HFFPerc", "AFFPerc", "HCloseCFPerc", "ACloseCFPerc",
        "HCloseFFPerc", "ACloseFFPerc", "HPDO", "APDO",
        "HSTPerc", "ASTPerc", "HPPSEff", "APPSEff",
        "HSOGPG", "ASOGPG", "SOGPGDiff", "SOGPGMutual",
        "HL5GW", "AL5GW", "L5GWDiff",
        "HLmdGPG1", "ALmdGPG1", "HLmdGPG2", "ALmdGPG2",
        "HLmdGAPG1", "ALmdGAPG1", "HLmdGAPG2", "ALmdGAPG2",
        "HShameFactor", "AShameFactor",
        "HHungerFG", "AHungerFG", "HungerFGDiff", "HungerFGMutual",
    ],
    "labels": ["totalGoalsNoOT", "homeScoreNoOT", "awayScoreNoOT"],
    "filePath": DATA_FILE,
    "name": "goals_model",
}


def normalize_dataframe(df, df_full=None):
    if df_full is None:
        df_full = df

    df = df.copy()

    boolean_columns = ["OT", "SO"]
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool).astype(int)

    return df


def get_attributes(strategy, split=None, df=None):
    if df is None:
        if not os.path.exists(strategy["filePath"]):
            raise FileNotFoundError(f"Training data file not found: {strategy['filePath']}")
        df = pd.read_csv(strategy["filePath"])
    else:
        df = df.copy()

    df = df.dropna(subset=["winner"])
    df = df[df["winner"].notna()]
    df = df[df["winner"] != ""]

    df = normalize_dataframe(df)

    attribute_columns = strategy["attributes"]

    available_attrs = [col for col in attribute_columns if col in df.columns]
    missing_attrs = [col for col in attribute_columns if col not in df.columns]

    if missing_attrs:
        print(f"Warning: Missing attribute columns: {missing_attrs}")

    X = df[available_attrs].copy()
    y = df[strategy["labels"]].copy()

    X = X.fillna(0)
    y = y.fillna(0)

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    for col in y.columns:
        y[col] = pd.to_numeric(y[col], errors="coerce").fillna(0)

    if split is None:
        train_attr = X.values if isinstance(X, pd.DataFrame) else X
        test_attr = np.array([]).reshape(0, len(available_attrs))
        train_labels = y.values if isinstance(y, pd.DataFrame) else y
        test_labels = np.array([])
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=split, random_state=42, shuffle=True
        )
        train_attr = X_train.values if isinstance(X_train, pd.DataFrame) else X_train
        test_attr = X_test.values if isinstance(X_test, pd.DataFrame) else X_test
        train_labels = y_train.values if isinstance(y_train, pd.DataFrame) else y_train
        test_labels = y_test.values if isinstance(y_test, pd.DataFrame) else y_test

    return train_attr, test_attr, train_labels, test_labels


def get_games_to_predict(strategy):
    df = pd.read_csv(strategy["filePath"])

    games_to_predict = []
    for idx in range(len(df) - 1, -1, -1):
        row = df.iloc[idx]
        winner = row["winner"]

        if pd.isna(winner) or (isinstance(winner, float) and pd.isna(winner)):
            games_to_predict.append(idx)
        else:
            break

    if not games_to_predict:
        return pd.DataFrame(), pd.DataFrame()

    games_to_predict.reverse()
    df_predict = df.iloc[games_to_predict].copy()

    df_predict = normalize_dataframe(df_predict, df_full=df)

    attribute_columns = strategy["attributes"]
    available_attrs = [col for col in attribute_columns if col in df_predict.columns]

    X = df_predict[available_attrs].copy()
    X = X.fillna(0)

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    return X, df_predict
