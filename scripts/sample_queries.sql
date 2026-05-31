-- Example SQL queries for BI / Analytics discussion

-- 1. Daily revenue and personnel cost ratio
SELECT
    date,
    SUM(revenue) AS total_revenue,
    SUM(labor_cost) AS total_labor_cost,
    SUM(labor_cost) / NULLIF(SUM(revenue), 0) AS personnel_cost_ratio
FROM fact_restaurant_daily
GROUP BY date
ORDER BY date;

-- 2. Productivity by city
SELECT
    r.city,
    SUM(f.revenue) AS revenue,
    SUM(f.staff_hours) AS staff_hours,
    SUM(f.revenue) / NULLIF(SUM(f.staff_hours), 0) AS productivity_per_hour
FROM fact_restaurant_daily f
JOIN dim_restaurant r
    ON f.restaurant_id = r.restaurant_id
GROUP BY r.city
ORDER BY productivity_per_hour DESC;

-- 3. High-priority staffing recommendations
SELECT
    date,
    restaurant_id,
    staffing_gap_hours,
    priority,
    recommendation
FROM recommendations
WHERE priority = 'High'
ORDER BY ABS(staffing_gap_hours) DESC;
