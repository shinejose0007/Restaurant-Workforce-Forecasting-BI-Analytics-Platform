# Restaurant Workforce Forecasting & BI Analytics Platform

Data Science + BI Analytics project designed for roles focused on operational analytics, forecasting, dashboards, KPI reporting, and customer-facing business recommendations.

The project simulates restaurant operations data and builds an end-to-end workflow:

1. Generate realistic synthetic restaurant data
2. Prepare features for analytics and modelling
3. Train forecasting models with Python and scikit-learn
4. Create operational recommendations for staffing and productivity
5. Export clean CSV tables for Power BI
6. Run an interactive Streamlit dashboard locally

## Why this project

It demonstrates the exact bridge between Data Science and Business Intelligence:

- Python data preparation with pandas and NumPy
- Sales and demand forecasting with scikit-learn
- KPI analysis for revenue, orders, staff hours, productivity, and personnel cost ratio
- Model evaluation with MAE, RMSE, and MAPE
- Business recommendations based on forecasts and productivity targets
- Streamlit dashboard for quick local demo
- Power BI-ready star-schema CSV exports
- Clear stakeholder-oriented explanations

## Business problem

Restaurant managers need to plan shifts before demand is known. If staffing is too low, service quality drops. If staffing is too high, personnel cost ratio becomes inefficient.

This project answers:

> How many staff hours are needed for each restaurant and day based on expected demand, revenue, seasonality, weather, promotions, and historical productivity?

## Project structure

```text
restaurant_workforce_analytics/
├── app/
│   └── streamlit_app.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── POWER_BI_GUIDE.md
│   └── PROJECT_REPORT.md
├── models/
├── notebooks/
├── powerbi/
│   ├── fact_restaurant_daily.csv
│   ├── fact_predictions.csv
│   ├── dim_restaurant.csv
│   ├── dim_date.csv
│   ├── kpi_summary.csv
│   ├── recommendations.csv
│   └── measures_dax.txt
├── scripts/
│   └── build_all.py
├── src/
│   ├── config.py
│   ├── generate_data.py
│   ├── prepare_features.py
│   ├── train_model.py
│   ├── recommendations.py
│   └── powerbi_export.py
├── requirements.txt
├── run_local.bat
└── run_local.sh
```

## Quick start on Windows

Open Command Prompt or PowerShell in the project folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/build_all.py
streamlit run app/streamlit_app.py
```

Or double-click / run:

```bash
run_local.bat
```

## Quick start on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_all.py
streamlit run app/streamlit_app.py
```

## Power BI usage

After running `python scripts/build_all.py`, import the CSV files from the `powerbi/` folder into Power BI Desktop.

Recommended relationships:

- `fact_restaurant_daily[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `fact_predictions[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `recommendations[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `fact_restaurant_daily[date]` → `dim_date[date]`
- `fact_predictions[date]` → `dim_date[date]`
- `recommendations[date]` → `dim_date[date]`

See `docs/POWER_BI_GUIDE.md` for dashboard pages and DAX measure suggestions.

## Main KPIs

- Revenue
- Orders
- Average Order Value
- Staff Hours
- Labor Cost
- Personnel Cost Ratio
- Productivity per Staff Hour
- Forecast Error
- Recommended Staff Hours
- Staffing Gap
- Anomaly Flag
