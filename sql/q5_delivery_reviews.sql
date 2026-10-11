SELECT ROUND(avg_review_score)::integer AS review_score,
       COUNT(*) AS order_count,
       ROUND(AVG(delivery_delay_days)::numeric, 2) AS avg_delay_days,
       COUNT(*) FILTER (WHERE delivery_delay_days > 0) AS late_orders,
       COUNT(*) FILTER (WHERE delivery_delay_days <= 0)
           AS on_time_or_early_orders
FROM analytics.order_mart
WHERE delivered_date IS NOT NULL
  AND estimated_delivery_date IS NOT NULL
  AND avg_review_score IS NOT NULL
GROUP BY ROUND(avg_review_score)::integer
ORDER BY review_score;