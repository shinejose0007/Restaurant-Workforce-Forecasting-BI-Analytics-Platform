# Power BI Guide

This project is designed to be opened later in Power BI using exported CSV files.

## 1. Generate the export files

Run:

```bash
python scripts/build_all.py
```

This creates:

- `powerbi/fact_restaurant_daily.csv`
- `powerbi/fact_predictions.csv`
- `powerbi/dim_restaurant.csv`
- `powerbi/dim_date.csv`
- `powerbi/recommendations.csv`
- `powerbi/kpi_summary.csv`
- `powerbi/model_metrics.csv`
- `powerbi/measures_dax.txt`

## 2. Import into Power BI Desktop

In Power BI Desktop:

1. Get Data → Text/CSV
2. Select all CSV files from the `powerbi/` folder
3. Load the tables
4. Create relationships

## 3. Recommended relationships

- `fact_restaurant_daily[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `fact_predictions[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `recommendations[restaurant_id]` → `dim_restaurant[restaurant_id]`
- `fact_restaurant_daily[date]` → `dim_date[date]`
- `fact_predictions[date]` → `dim_date[date]`
- `recommendations[date]` → `dim_date[date]`

## 4. Suggested dashboard pages

### Page 1: Executive Overview

Cards:

- Total Revenue
- Total Orders
- Average Order Value
- Productivity per Staff Hour
- Personnel Cost Ratio
- Anomaly Count

Charts:

- Revenue by date
- Revenue by city
- Personnel cost ratio by restaurant type
- Actual vs forecasted revenue

### Page 2: Forecast Accuracy

Cards:

- Average Forecast Error %
- Total Forecast Error
- MAE / RMSE / MAPE from model metrics

Charts:

- Actual vs predicted revenue line chart
- Forecast error by date
- Forecast error by restaurant
- High-error restaurants table

### Page 3: Staffing Recommendations

Cards:

- Recommended Staff Hours
- Staffing Gap Hours
- High Priority Recommendations

Charts:

- Staffing gap by restaurant
- Staffing gap by city
- Personnel cost ratio by restaurant
- Recommendation table filtered by priority

### Page 4: Operations Deep Dive

Charts:

- Orders by weekday
- Revenue by weather
- Promotion active vs revenue
- Productivity by city and restaurant type
- Labor cost trend

## 5. DAX measures

The file `powerbi/measures_dax.txt` contains ready-to-copy DAX measures.
