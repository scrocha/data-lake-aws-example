SELECT
    year,
    month,
    COUNT(*) AS total_trips
FROM {database}.taxi_trips_clean
WHERE year = '2024'
  AND month = '1'
GROUP BY year, month;
