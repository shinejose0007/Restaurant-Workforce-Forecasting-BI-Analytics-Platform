"""Train a revenue forecasting model and create predictions."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from src.config import FEATURE_DATA_PATH, PREDICTIONS_PATH, MODEL_PATH, METRICS_PATH, RANDOM_SEED
except ModuleNotFoundError:
    from config import FEATURE_DATA_PATH, PREDICTIONS_PATH, MODEL_PATH, METRICS_PATH, RANDOM_SEED


NUMERIC_FEATURES = [
    "weekday", "month", "day_of_year", "week_of_year", "quarter",
    "is_weekend", "is_holiday", "temperature", "promotion_active",
    "revenue_lag_1", "revenue_lag_7", "orders_lag_7", "staff_hours_lag_7",
    "revenue_rolling_7", "orders_rolling_7", "productivity_rolling_7",
]
CATEGORICAL_FEATURES = ["city", "restaurant_type", "weather"]
TARGET = "revenue"


def mape(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def train_model(feature_path=FEATURE_DATA_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(feature_path, parse_dates=["date"])
    df = df.sort_values("date")

    cutoff = df["date"].max() - pd.Timedelta(days=60)
    train_df = df[df["date"] <= cutoff].copy()
    test_df = df[df["date"] > cutoff].copy()

    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = train_df[TARGET]
    X_test = test_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_test = test_df[TARGET]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=35,
        min_samples_leaf=3,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
    pipeline.fit(X_train, y_train)

    test_pred = pipeline.predict(X_test)
    all_pred = pipeline.predict(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])

    rmse = float(np.sqrt(mean_squared_error(y_test, test_pred)))
    mae = float(mean_absolute_error(y_test, test_pred))
    mape_score = mape(y_test, test_pred)

    df["predicted_revenue"] = np.round(all_pred, 2)
    df["forecast_error"] = np.round(df["revenue"] - df["predicted_revenue"], 2)
    df["absolute_percentage_error"] = np.round(np.abs(df["forecast_error"] / df["revenue"]) * 100, 2)
    df["split"] = np.where(df["date"] <= cutoff, "train", "test")

    df["target_productivity_per_hour"] = df.groupby("restaurant_type")["productivity_per_hour"].transform("median")
    df["recommended_staff_hours"] = np.round(df["predicted_revenue"] / df["target_productivity_per_hour"], 2)
    df["staffing_gap_hours"] = np.round(df["recommended_staff_hours"] - df["staff_hours"], 2)
    df["recommended_labor_cost"] = np.round(df["recommended_staff_hours"] * df["hourly_wage"], 2)
    df["predicted_personnel_cost_ratio"] = np.round(df["recommended_labor_cost"] / df["predicted_revenue"], 4)

    test_error_std = float(np.std(test_df[TARGET] - test_pred))
    df["anomaly_flag"] = ((np.abs(df["forecast_error"]) > 2 * test_error_std) | (df["absolute_percentage_error"] > 25)).astype(int)

    metrics = pd.DataFrame([
        {
            "model": "RandomForestRegressor",
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "cutoff_date": cutoff.date().isoformat(),
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE_percent": round(mape_score, 2),
        }
    ])

    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PREDICTIONS_PATH, index=False)
    metrics.to_csv(METRICS_PATH, index=False)
    joblib.dump(pipeline, MODEL_PATH)

    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved predictions -> {PREDICTIONS_PATH}")
    print(f"Metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape_score:.2f}%")
    return df, metrics


if __name__ == "__main__":
    train_model()
