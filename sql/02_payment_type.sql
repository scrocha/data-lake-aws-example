SELECT
    payment_type,
    SUM(total_trips) AS total_trips,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(AVG(avg_tip), 2) AS avg_tip
FROM {database}.taxi_monthly_metrics
GROUP BY payment_type
ORDER BY total_revenue DESC;
