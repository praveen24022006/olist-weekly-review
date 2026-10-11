WITH customer_orders AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id) AS order_count
    FROM staging.orders o
    JOIN staging.customers c ON o.customer_id = c.customer_id
    WHERE c.customer_unique_id IS NOT NULL
    GROUP BY c.customer_unique_id
)
SELECT COUNT(*) AS total_customers,
       COUNT(*) FILTER (WHERE order_count > 1) AS repeat_customers,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE order_count > 1)
           / NULLIF(COUNT(*), 0), 2
       ) AS repeat_purchase_rate_pct
FROM customer_orders;