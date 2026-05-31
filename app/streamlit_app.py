from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PREDICTIONS_PATH, RECOMMENDATIONS_PATH, METRICS_PATH, POWERBI_DIR

st.set_page_config(
    page_title="Restaurant Workforce Forecasting & BI Analytics",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data():
    if not PREDICTIONS_PATH.exists() or not RECOMMENDATIONS_PATH.exists():
        st.error("Data files not found. Please run: python scripts/build_all.py")
        st.stop()
    df = pd.read_csv(PREDICTIONS_PATH, parse_dates=["date"])
    rec = pd.read_csv(RECOMMENDATIONS_PATH, parse_dates=["date"])
    metrics = pd.read_csv(METRICS_PATH) if METRICS_PATH.exists() else pd.DataFrame()
    return df, rec, metrics


def format_eur(value):
    return f"€{value:,.0f}".replace(",", ".")


def format_pct(value):
    return f"{value * 100:.1f}%"


df, rec, metrics = load_data()

st.title("Restaurant Workforce Forecasting & BI Analytics Platform")
st.caption("Synthetic restaurant operations data · Python + scikit-learn forecasting · BI dashboard · Power BI-ready exports")

with st.sidebar:
    st.header("Filters")
    selected_cities = st.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))
    selected_types = st.multiselect("Restaurant type", sorted(df["restaurant_type"].unique()), default=sorted(df["restaurant_type"].unique()))
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    page = st.radio("Page", ["Executive Overview", "Forecasting", "Staffing Recommendations", "What-if Simulation", "Power BI Export"])

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = df["date"].min(), df["date"].max()

f = df[
    (df["city"].isin(selected_cities)) &
    (df["restaurant_type"].isin(selected_types)) &
    (df["date"].between(start_date, end_date))
].copy()

fr = rec[
    (rec["city"].isin(selected_cities)) &
    (rec["restaurant_type"].isin(selected_types)) &
    (rec["date"].between(start_date, end_date))
].copy()

if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

if page == "Executive Overview":
    st.subheader("Executive Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", format_eur(f["revenue"].sum()))
    c2.metric("Orders", f"{int(f['orders'].sum()):,}".replace(",", "."))
    c3.metric("Productivity / staff hour", format_eur(f["productivity_per_hour"].mean()))
    c4.metric("Personnel cost ratio", format_pct(f["personnel_cost_ratio"].mean()))
    c5.metric("Anomalies", int(f["anomaly_flag"].sum()))

    daily = f.groupby("date", as_index=False).agg(
        revenue=("revenue", "sum"),
        predicted_revenue=("predicted_revenue", "sum"),
        orders=("orders", "sum"),
        staff_hours=("staff_hours", "sum"),
        labor_cost=("labor_cost", "sum"),
    )
    daily["personnel_cost_ratio"] = daily["labor_cost"] / daily["revenue"]

    st.plotly_chart(
        px.line(daily, x="date", y=["revenue", "predicted_revenue"], title="Actual vs Forecasted Revenue"),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    city_summary = f.groupby("city", as_index=False).agg(revenue=("revenue", "sum"), staff_hours=("staff_hours", "sum"))
    city_summary["productivity_per_hour"] = city_summary["revenue"] / city_summary["staff_hours"]
    col1.plotly_chart(px.bar(city_summary.sort_values("revenue"), x="city", y="revenue", title="Revenue by City"), use_container_width=True)

    type_summary = f.groupby("restaurant_type", as_index=False).agg(revenue=("revenue", "sum"), labor_cost=("labor_cost", "sum"))
    type_summary["personnel_cost_ratio"] = type_summary["labor_cost"] / type_summary["revenue"]
    col2.plotly_chart(px.bar(type_summary, x="restaurant_type", y="personnel_cost_ratio", title="Personnel Cost Ratio by Restaurant Type"), use_container_width=True)

    st.markdown("### Business interpretation")
    st.write(
        "This dashboard converts restaurant operations data into decision-ready KPIs. "
        "Managers can compare actual and forecasted revenue, monitor productivity, detect unusual deviations, "
        "and identify staffing gaps before operational problems occur."
    )

elif page == "Forecasting":
    st.subheader("Forecasting Performance")
    if not metrics.empty:
        st.dataframe(metrics, use_container_width=True)

    daily = f.groupby("date", as_index=False).agg(revenue=("revenue", "sum"), predicted_revenue=("predicted_revenue", "sum"))
    daily["forecast_error"] = daily["revenue"] - daily["predicted_revenue"]
    daily["absolute_error"] = daily["forecast_error"].abs()

    st.plotly_chart(px.line(daily, x="date", y=["revenue", "predicted_revenue"], title="Actual vs Predicted Revenue"), use_container_width=True)
    st.plotly_chart(px.bar(daily, x="date", y="forecast_error", title="Forecast Error Over Time"), use_container_width=True)

    st.markdown("### Largest forecast deviations")
    cols = ["date", "restaurant_id", "city", "restaurant_type", "revenue", "predicted_revenue", "forecast_error", "absolute_percentage_error", "weather", "promotion_active"]
    st.dataframe(f.sort_values("absolute_percentage_error", ascending=False)[cols].head(25), use_container_width=True)

elif page == "Staffing Recommendations":
    st.subheader("Staffing Recommendations")
    st.write("Recommendations are generated from predicted revenue, expected productivity and personnel cost ratio.")

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    fr["priority_sort"] = fr["priority"].map(priority_order)
    display_cols = [
        "date", "restaurant_id", "city", "restaurant_type", "revenue", "predicted_revenue",
        "staff_hours", "recommended_staff_hours", "staffing_gap_hours", "personnel_cost_ratio",
        "priority", "recommendation"
    ]
    st.dataframe(fr.sort_values(["priority_sort", "date"], ascending=[True, False])[display_cols].head(100), use_container_width=True)

    top_gap = fr.copy()
    top_gap["abs_gap"] = top_gap["staffing_gap_hours"].abs()
    st.plotly_chart(
        px.bar(top_gap.sort_values("abs_gap", ascending=False).head(30), x="restaurant_id", y="staffing_gap_hours", color="priority", title="Largest Staffing Gaps"),
        use_container_width=True,
    )

elif page == "What-if Simulation":
    st.subheader("What-if Simulation")
    st.write("Simulate how revenue growth or productivity assumptions affect staff-hour requirements and labor-cost ratio.")

    base_revenue = float(f["predicted_revenue"].sum())
    base_staff_hours = float(f["recommended_staff_hours"].sum())
    avg_wage = float(f["hourly_wage"].mean())
    base_productivity = base_revenue / base_staff_hours

    col1, col2, col3 = st.columns(3)
    revenue_uplift = col1.slider("Expected revenue change", -30, 50, 10, step=1) / 100
    productivity_change = col2.slider("Productivity change", -20, 30, 5, step=1) / 100
    wage_change = col3.slider("Hourly wage change", -10, 30, 0, step=1) / 100

    simulated_revenue = base_revenue * (1 + revenue_uplift)
    simulated_productivity = base_productivity * (1 + productivity_change)
    simulated_staff_hours = simulated_revenue / simulated_productivity
    simulated_wage = avg_wage * (1 + wage_change)
    simulated_labor_cost = simulated_staff_hours * simulated_wage
    simulated_pcr = simulated_labor_cost / simulated_revenue

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Simulated revenue", format_eur(simulated_revenue), delta=f"{revenue_uplift*100:.0f}%")
    c2.metric("Required staff hours", f"{simulated_staff_hours:,.0f}".replace(",", "."), delta=f"{simulated_staff_hours - base_staff_hours:,.0f}".replace(",", "."))
    c3.metric("Labor cost", format_eur(simulated_labor_cost))
    c4.metric("Personnel cost ratio", format_pct(simulated_pcr))

    st.markdown("### Interpretation")
    if simulated_pcr > 0.32:
        st.warning("The simulated personnel cost ratio is high. Management may need to improve productivity, adjust staffing, or review opening hours/promotions.")
    else:
        st.success("The simulated scenario keeps personnel cost ratio in a healthier range.")

elif page == "Power BI Export":
    st.subheader("Power BI Export")
    st.write("The project exports Power BI-ready CSV tables into the `powerbi/` folder.")

    export_files = sorted(POWERBI_DIR.glob("*.csv")) + sorted(POWERBI_DIR.glob("*.txt"))
    for path in export_files:
        st.write(f"- `{path.name}`")

    st.markdown("### Recommended Power BI pages")
    st.write("1. Executive KPI Overview")
    st.write("2. Forecast Accuracy & Revenue Trends")
    st.write("3. Staffing and Productivity Analysis")
    st.write("4. Restaurant / City Performance")
    st.write("5. Recommendations and Anomaly Monitoring")

st.divider()
st.caption("Portfolio project: synthetic data only. Designed to demonstrate data science, BI analytics, forecasting, dashboarding and business recommendations.")
