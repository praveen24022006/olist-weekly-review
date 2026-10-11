WITH monthly_revenue AS (
    SELECT DATE_TRUNC('month', purchase_timestamp)::date AS month,
           SUM(payment_total) AS revenue
    FROM analytics.order_mart
    WHERE order_status <> 'unavailable'
    GROUP BY 1
),
comparison AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS previous_revenue
    FROM monthly_revenue
)
SELECT month,
       ROUND(revenue::numeric, 2) AS revenue,
       ROUND(previous_revenue::numeric, 2) AS previous_month_revenue,
       ROUND(100.0 * (revenue - previous_revenue)
             / NULLIF(previous_revenue, 0), 2) AS growth_percentage
FROM comparison
ORDER BY month;