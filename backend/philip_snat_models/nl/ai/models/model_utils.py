import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

WINNER_STRATEGY = {
    "attributes": [
        "HRank",
        "ARank",
        "RankDiff",
        "HGpG",
        "AGpG",
        "GpGDiff",
        "HGApG",
        "AGApG",
        "GApGDiff",
        "HSOGpG",
        "ASOGpG",
        "SOGpGDiff",
        "HSSlotPG",
        "ASSlotPG",
        "SSlotPGDiff",
        "HSHMpG",
        "ASHMpG",
        "HMpGDiff",
        "HSHPpG",
        "ASHPpG",
        "HPpGDiff",
        "HPPGpG",
        "APPGpG",
        "PGpGDiff",
        "HPPGApG",
        "APPGApG",
        "PPGApGDiff",
        "HPPGEff",
        "APPGEff",
        "PPGEffDiff",
        "HPKEff",
        "APKEff",
        "PKEffDiff",
        "HSApG",
        "ASApG",
        "SApGDiff",
        "HSSlotApG",
        "ASSlotApG",
        "SSlotApGDiff",
        "HLGD",
        "ALGD",
        "HLGPA",
        "ALGPA",
        "HLGOP",
        "ALGOP",
        "LGOPDiff",
        "HL5GW",
        "AL5GW",
        "L5GWDiff",
    ],
    "labels": ["winner"],
    "name": "winner_model",
}

GOALS_STRATEGY = {
    "attributes": [
        "HRank",
        "ARank",
        "RankDiff",
        "HGpG",
        "AGpG",
        "GpGDiff",
        "HGApG",
        "AGApG",
        "GApGDiff",
        "HSOGpG",
        "ASOGpG",
        "SOGpGDiff",
        "HSSlotPG",
        "ASSlotPG",
        "SSlotPGDiff",
        "HSHMpG",
        "ASHMpG",
        "HMpGDiff",
        "HSHPpG",
        "ASHPpG",
        "HPpGDiff",
        "HPPGpG",
        "APPGpG",
        "PGpGDiff",
        "HPPGApG",
        "APPGApG",
        "PPGApGDiff",
        "HPPGEff",
        "APPGEff",
        "PPGEffDiff",
        "HPKEff",
        "APKEff",
        "PKEffDiff",
        "HSApG",
        "ASApG",
        "SApGDiff",
        "HSSlotApG",
        "ASSlotApG",
        "SSlotApGDiff",
        "HLGD",
        "ALGD",
        "HLGPA",
        "ALGPA",
        "HLGOP",
        "ALGOP",
        "LGOPDiff",
        "HL5GW",
        "AL5GW",
        "L5GWDiff",
    ],
    "labels": ["total_score_no_ot", "home_score_no_ot", "away_score_no_ot"],
    "name": "goals_model",
}


def normalize_dataframe(df, df_full=None, include_winner=False):
    df = df.copy()

    boolean_columns = ["OT", "SO"]
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool).astype(int)

    categorical_columns = ["HLGD", "ALGD", "HLGPA", "ALGPA"]
    if include_winner:
        categorical_columns.append("winner")

    for col in categorical_columns:
        if col in df.columns:
            all_unique_values = (
                sorted(df_full[col].dropna().unique())
                if df_full is not None
                else sorted(df[col].dropna().unique())
            )
            label_encoder = {val: idx for idx, val in enumerate(all_unique_values)}
            df[col] = df[col].map(label_encoder).fillna(-1)

    return df


def get_attributes_from_df(df, strategy, split=None):
    df = df.dropna(subset=["winner"])
    df = df[df["winner"].astype(str).str.strip() != ""]

    include_winner = "winner" in strategy.get("labels", [])
    df = normalize_dataframe(df, df_full=df, include_winner=include_winner)

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


def get_games_to_predict_from_df(df, strategy):
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

    df_predict = normalize_dataframe(df_predict, df_full=df)

    attribute_columns = strategy["attributes"]
    available_attrs = [col for col in attribute_columns if col in df_predict.columns]

    X = df_predict[available_attrs].copy()
    X = X.fillna(0)

    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    return X, df_predict
