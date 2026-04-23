from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal, Optional, Tuple

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = Path(__file__).resolve().parent / "medicine_dataset.csv"


TaskType = Literal["classification", "regression"]


@dataclass(frozen=True)
class TrainResult:
    model_path: Path
    task: TaskType
    test_size: float
    random_state: int


def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize column names expected from your CSV
    # Medicine_Name,Category,Batch_Number,Manufacturing_Date,Expiry_Date,Quantity
    df["Manufacturing_Date"] = pd.to_datetime(df["Manufacturing_Date"], errors="coerce")
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")

    today = pd.Timestamp(date.today())
    df["days_to_expiry"] = (df["Expiry_Date"] - today).dt.days
    df["mfg_year"] = df["Manufacturing_Date"].dt.year
    df["mfg_month"] = df["Manufacturing_Date"].dt.month
    df["exp_year"] = df["Expiry_Date"].dt.year
    df["exp_month"] = df["Expiry_Date"].dt.month

    return df


def _build_features_and_target(
    df: pd.DataFrame, task: TaskType, expiring_within_days: int
) -> Tuple[pd.DataFrame, pd.Series]:
    df = _add_derived_columns(df)

    feature_cols = [
        "Category",
        "Quantity",
        "mfg_year",
        "mfg_month",
        "exp_year",
        "exp_month",
    ]

    # Keep only the columns we need; drop rows with missing target.
    X = df[feature_cols]

    if task == "regression":
        y = df["days_to_expiry"]
        keep = y.notna()
        return X.loc[keep], y.loc[keep].astype(float)

    # classification: label = 1 if expiring within N days (and not already expired)
    days = df["days_to_expiry"]
    y = ((days.notna()) & (days >= 0) & (days <= expiring_within_days)).astype(int)
    return X, y


def train_model(
    csv_path: Path,
    task: TaskType,
    expiring_within_days: int = 30,
    test_size: float = 0.2,
    random_state: int = 42,
    out_dir: Optional[Path] = None,
) -> TrainResult:
    if out_dir is None:
        out_dir = Path(__file__).resolve().parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    X, y = _build_features_and_target(df, task=task, expiring_within_days=expiring_within_days)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y if task == "classification" else None
    )

    numeric_features = ["Quantity", "mfg_year", "mfg_month", "exp_year", "exp_month"]
    categorical_features = ["Category"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    if task == "classification":
        estimator = RandomForestClassifier(n_estimators=300, random_state=random_state)
    else:
        estimator = RandomForestRegressor(n_estimators=400, random_state=random_state)

    model = Pipeline(steps=[("preprocess", preprocessor), ("model", estimator)])
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    if task == "classification":
        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        print(f"Task: classification (expiring_within_days={expiring_within_days})")
        print(f"Test accuracy: {acc:.4f}")
        print(f"Test F1: {f1:.4f}")
        model_path = out_dir / f"expiry_classifier_{expiring_within_days}d.joblib"
    else:
        rmse = float(mean_squared_error(y_test, y_pred)**0.5)
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        print("Task: regression (predict days_to_expiry)")
        print(f"Test RMSE: {rmse:.4f}")
        print(f"Test MAE: {mae:.4f}")
        print(f"Test R^2: {r2:.4f}")
        model_path = out_dir / "days_to_expiry_regressor.joblib"

    joblib.dump(
        {
            "task": task,
            "expiring_within_days": expiring_within_days,
            "feature_schema": list(X.columns),
            "model": model,
        },
        model_path,
    )

    print(f"Saved model to: {model_path}")
    return TrainResult(model_path=model_path, task=task, test_size=test_size, random_state=random_state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train ML model from medicine_dataset.csv")
    parser.add_argument("--csv", type=str, default=str(DEFAULT_DATASET), help="Path to CSV dataset")
    parser.add_argument(
        "--task",
        type=str,
        choices=["classification", "regression"],
        default="classification",
        help="Train a classifier or regressor",
    )
    parser.add_argument("--days", type=int, default=30, help="For classification: expiring within N days")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split size (0-1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_model(
        csv_path=Path(args.csv),
        task=args.task,  # type: ignore[arg-type]
        expiring_within_days=args.days,
        test_size=args.test_size,
        random_state=args.seed,
    )


if __name__ == "__main__":
    main()

