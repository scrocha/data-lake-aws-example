SELECT
    year,
    month,
    SUM(total_trips) AS total_trips,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM {database}.taxi_monthly_metrics
GROUP BY year, month
ORDER BY year, month;
