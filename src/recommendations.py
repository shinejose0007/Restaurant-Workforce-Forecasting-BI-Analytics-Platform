"""Generate customer-facing operational recommendations from predictions."""
from __future__ import annotations

import pandas as pd

try:
    from src.config import PREDICTIONS_PATH, RECOMMENDATIONS_PATH
except ModuleNotFoundError:
    from config import PREDICTIONS_PATH, RECOMMENDATIONS_PATH


def classify_recommendation(row) -> str:
    gap = row["staffing_gap_hours"]
    pcr = row["personnel_cost_ratio"]
    ape = row["absolute_percentage_error"]

    if gap > 8:
        return "Increase planned staff hours for expected demand"
    if gap < -8:
        return "Review potential overstaffing and reduce planned hours"
    if pcr > 0.32:
        return "Investigate high personnel cost ratio"
    if ape > 25:
        return "Check forecast deviation and possible local event/anomaly"
    return "Staffing and productivity look stable"


def priority(row) -> str:
    if abs(row["staffing_gap_hours"]) > 14 or row["personnel_cost_ratio"] > 0.38 or row["absolute_percentage_error"] > 35:
        return "High"
    if abs(row["staffing_gap_hours"]) > 8 or row["personnel_cost_ratio"] > 0.32 or row["absolute_percentage_error"] > 25:
        return "Medium"
    return "Low"


def generate_recommendations(input_path=PREDICTIONS_PATH, output_path=RECOMMENDATIONS_PATH) -> pd.DataFrame:
    df = pd.read_csv(input_path, parse_dates=["date"])
    rec = df.copy()
    rec["recommendation"] = rec.apply(classify_recommendation, axis=1)
    rec["priority"] = rec.apply(priority, axis=1)
    cols = [
        "date", "restaurant_id", "city", "restaurant_type", "weekday_name",
        "revenue", "predicted_revenue", "orders", "staff_hours", "recommended_staff_hours",
        "staffing_gap_hours", "personnel_cost_ratio", "predicted_personnel_cost_ratio",
        "productivity_per_hour", "absolute_percentage_error", "anomaly_flag", "priority", "recommendation"
    ]
    rec = rec[cols].sort_values(["priority", "date", "restaurant_id"], ascending=[True, False, True])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rec.to_csv(output_path, index=False)
    print(f"Saved recommendations -> {output_path}")
    return rec


if __name__ == "__main__":
    generate_recommendations()
