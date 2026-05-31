# Project Report: Restaurant Workforce Forecasting & BI Analytics Platform

## Objective

The objective is to build a practical data science and BI analytics project for restaurant operations. The project predicts restaurant revenue and translates forecasts into staffing recommendations.

## Business context

Restaurants face fluctuating demand based on weekday, seasonality, weather, holidays and promotions. Better demand forecasts can improve shift planning, reduce overstaffing, prevent understaffing and support better productivity.

## Data

The project uses synthetic restaurant data with the following variables:

- Date
- Restaurant ID
- City
- Restaurant type
- Weather
- Temperature
- Promotion flag
- Orders
- Revenue
- Staff hours
- Labor cost
- Productivity per hour
- Personnel cost ratio

## Methodology

1. Generate synthetic data with realistic seasonality and business patterns.
2. Create lag and rolling features per restaurant.
3. Train a Random Forest forecasting model.
4. Evaluate model performance using MAE, RMSE and MAPE.
5. Generate recommended staff hours based on predicted revenue and expected productivity.
6. Export data into Power BI-ready tables.
7. Build a Streamlit dashboard for portfolio demonstration.

## Business KPIs

- Revenue
- Orders
- Average Order Value
- Labor Cost
- Personnel Cost Ratio
- Productivity per Staff Hour
- Forecast Error
- Recommended Staff Hours
- Staffing Gap Hours
- Anomaly Flag

## Stakeholder value

The platform helps restaurant managers and customer success teams understand:

- Which restaurants are underperforming
- Where staffing should be adjusted
- How accurate demand forecasts are
- Which locations show unusual business patterns
- How productivity and personnel cost ratio change by city, restaurant type and time

## Future improvements

- Add real weather API integration
- Add holiday calendars by German state
- Include hourly data instead of daily data
- Build a Power BI `.pbix` dashboard file
- Add SQL database integration
- Add Azure Data Factory or SAP Datasphere architecture simulation
- Add recommendation system for shift templates
