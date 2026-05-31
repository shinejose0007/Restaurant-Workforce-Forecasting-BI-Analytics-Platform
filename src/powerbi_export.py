"""Export Power BI-ready CSV tables."""
from __future__ import annotations

import pandas as pd

try:
    from src.config import PREDICTIONS_PATH, RECOMMENDATIONS_PATH, POWERBI_DIR, METRICS_PATH
except ModuleNotFoundError:
    from config import PREDICTIONS_PATH, RECOMMENDATIONS_PATH, POWERBI_DIR, METRICS_PATH


def export_powerbi_tables() -> None:
    df = pd.read_csv(PREDICTIONS_PATH, parse_dates=["date"])
    rec = pd.read_csv(RECOMMENDATIONS_PATH, parse_dates=["date"])
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    dim_restaurant = (
        df[["restaurant_id", "city", "restaurant_type", "hourly_wage"]]
        .drop_duplicates()
        .sort_values("restaurant_id")
    )

    dim_date = df[["date", "weekday", "weekday_name", "month", "week_of_year", "quarter", "is_weekend", "is_holiday"]].drop_duplicates()
    dim_date["year"] = dim_date["date"].dt.year
    dim_date = dim_date.sort_values("date")

    fact_daily_cols = [
        "date", "restaurant_id", "weather", "temperature", "promotion_active", "orders",
        "delivery_orders", "dine_in_orders", "avg_order_value", "revenue", "staff_hours",
        "labor_cost", "productivity_per_hour", "personnel_cost_ratio"
    ]
    fact_daily = df[fact_daily_cols]

    fact_predictions_cols = [
        "date", "restaurant_id", "revenue", "predicted_revenue", "forecast_error",
        "absolute_percentage_error", "recommended_staff_hours", "staffing_gap_hours",
        "recommended_labor_cost", "predicted_personnel_cost_ratio", "anomaly_flag", "split"
    ]
    fact_predictions = df[fact_predictions_cols]

    kpi_summary = pd.DataFrame([
        {
            "total_revenue": round(df["revenue"].sum(), 2),
            "total_orders": int(df["orders"].sum()),
            "total_staff_hours": round(df["staff_hours"].sum(), 2),
            "avg_productivity_per_hour": round(df["productivity_per_hour"].mean(), 2),
            "avg_personnel_cost_ratio": round(df["personnel_cost_ratio"].mean(), 4),
            "avg_absolute_percentage_error": round(df["absolute_percentage_error"].mean(), 2),
            "anomaly_count": int(df["anomaly_flag"].sum()),
            "restaurant_count": int(df["restaurant_id"].nunique()),
            "date_count": int(df["date"].nunique()),
        }
    ])

    dim_restaurant.to_csv(POWERBI_DIR / "dim_restaurant.csv", index=False)
    dim_date.to_csv(POWERBI_DIR / "dim_date.csv", index=False)
    fact_daily.to_csv(POWERBI_DIR / "fact_restaurant_daily.csv", index=False)
    fact_predictions.to_csv(POWERBI_DIR / "fact_predictions.csv", index=False)
    rec.to_csv(POWERBI_DIR / "recommendations.csv", index=False)
    kpi_summary.to_csv(POWERBI_DIR / "kpi_summary.csv", index=False)

    if METRICS_PATH.exists():
        pd.read_csv(METRICS_PATH).to_csv(POWERBI_DIR / "model_metrics.csv", index=False)

    dax = """
Total Revenue = SUM(fact_restaurant_daily[revenue])
Total Orders = SUM(fact_restaurant_daily[orders])
Total Staff Hours = SUM(fact_restaurant_daily[staff_hours])
Labor Cost = SUM(fact_restaurant_daily[labor_cost])
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
Productivity per Staff Hour = DIVIDE([Total Revenue], [Total Staff Hours])
Personnel Cost Ratio = DIVIDE([Labor Cost], [Total Revenue])
Forecast Revenue = SUM(fact_predictions[predicted_revenue])
Forecast Error = SUM(fact_predictions[forecast_error])
Average Forecast Error % = AVERAGE(fact_predictions[absolute_percentage_error])
Recommended Staff Hours = SUM(fact_predictions[recommended_staff_hours])
Staffing Gap Hours = SUM(fact_predictions[staffing_gap_hours])
Anomaly Count = SUM(fact_predictions[anomaly_flag])
High Priority Recommendations = CALCULATE(COUNTROWS(recommendations), recommendations[priority] = "High")
""".strip()
    (POWERBI_DIR / "measures_dax.txt").write_text(dax, encoding="utf-8")

    print(f"Exported Power BI tables -> {POWERBI_DIR}")


if __name__ == "__main__":
    export_powerbi_tables()
