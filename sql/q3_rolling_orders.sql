WITH daily_orders AS (
    SELECT purchase_timestamp::date AS order_date,
           COUNT(*) AS order_count
    FROM staging.orders
    WHERE purchase_timestamp IS NOT NULL
    GROUP BY 1
)
SELECT order_date, order_count,
       ROUND(AVG(order_count::numeric) OVER (
           ORDER BY order_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 2) AS rolling_7day_avg
FROM daily_orders
ORDER BY order_date;