"""Prepare modelling and analytics features."""
from __future__ import annotations

import pandas as pd

try:
    from src.config import RAW_DATA_PATH, FEATURE_DATA_PATH
except ModuleNotFoundError:
    from config import RAW_DATA_PATH, FEATURE_DATA_PATH


def prepare_features(input_path=RAW_DATA_PATH, output_path=FEATURE_DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["date"])
    df = df.sort_values(["restaurant_id", "date"]).reset_index(drop=True)

    df["day_of_year"] = df["date"].dt.dayofyear
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"] = df["date"].dt.quarter

    group = df.groupby("restaurant_id", group_keys=False)
    df["revenue_lag_1"] = group["revenue"].shift(1)
    df["revenue_lag_7"] = group["revenue"].shift(7)
    df["orders_lag_7"] = group["orders"].shift(7)
    df["staff_hours_lag_7"] = group["staff_hours"].shift(7)
    df["revenue_rolling_7"] = group["revenue"].shift(1).rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    df["orders_rolling_7"] = group["orders"].shift(1).rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    df["productivity_rolling_7"] = group["productivity_per_hour"].shift(1).rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)

    for col in ["revenue_lag_1", "revenue_lag_7", "orders_lag_7", "staff_hours_lag_7", "revenue_rolling_7", "orders_rolling_7", "productivity_rolling_7"]:
        df[col] = df[col].fillna(group[col].transform("median"))
        df[col] = df[col].fillna(df[col].median())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    out = prepare_features()
    print(f"Prepared features: {out.shape[0]:,} rows, {out.shape[1]} columns -> {FEATURE_DATA_PATH}")
