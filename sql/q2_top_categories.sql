WITH category_revenue AS (
    SELECT c.customer_state,
           COALESCE(t.product_category_name_english,
                    p.product_category_name, 'unknown') AS category,
           SUM(oi.price + oi.freight_value) AS revenue
    FROM staging.order_items oi
    JOIN staging.orders o ON oi.order_id = o.order_id
    JOIN staging.customers c ON o.customer_id = c.customer_id
    JOIN raw_products p ON oi.product_id = p.product_id
    LEFT JOIN raw_category_translation t
      ON p.product_category_name = t.product_category_name
    WHERE o.order_status <> 'unavailable'
    GROUP BY 1, 2
),
ranked AS (
    SELECT *,
           DENSE_RANK() OVER (
               PARTITION BY customer_state ORDER BY revenue DESC
           ) AS category_rank
    FROM category_revenue
)
SELECT customer_state, category, ROUND(revenue::numeric, 2) AS revenue,
       category_rank
FROM ranked
WHERE category_rank <= 3
ORDER BY customer_state, category_rank, category;