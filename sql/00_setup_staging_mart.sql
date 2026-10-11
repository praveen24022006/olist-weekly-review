
-- Olist Weekly Business Review
-- Run after loading raw CSV files into olist_analytics.
-- This script is safe to rerun: existing tables are not overwritten.

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Staging: orders
CREATE TABLE IF NOT EXISTS staging.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    NULLIF(order_purchase_timestamp, '')::timestamp
        AS purchase_timestamp,
    NULLIF(order_approved_at, '')::timestamp
        AS approved_timestamp,
    NULLIF(order_delivered_carrier_date, '')::timestamp
        AS carrier_timestamp,
    NULLIF(order_delivered_customer_date, '')::timestamp
        AS delivered_timestamp,
    NULLIF(order_estimated_delivery_date, '')::timestamp
        AS estimated_delivery_timestamp
FROM raw_orders
WHERE order_id IS NOT NULL;

-- 2. Staging: customers
CREATE TABLE IF NOT EXISTS staging.customers AS
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM raw_customers
WHERE customer_id IS NOT NULL;

-- 3. Staging: order items
CREATE TABLE IF NOT EXISTS staging.order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price::numeric AS price,
    freight_value::numeric AS freight_value
FROM raw_order_items
WHERE order_id IS NOT NULL;

-- 4. Staging: payments
CREATE TABLE IF NOT EXISTS staging.payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments::integer AS payment_installments,
    payment_value::numeric AS payment_value
FROM raw_order_payments
WHERE order_id IS NOT NULL;

-- 5. Staging: reviews
CREATE TABLE IF NOT EXISTS staging.reviews AS
SELECT
    review_id,
    order_id,
    review_score::integer AS review_score
FROM raw_order_reviews
WHERE order_id IS NOT NULL;

-- 6. Analysis-ready mart: one row per order
CREATE TABLE IF NOT EXISTS analytics.order_mart AS
WITH item_totals AS (
    SELECT
        order_id,
        SUM(price) AS item_total,
        SUM(freight_value) AS freight_total,
        COUNT(*) AS item_count
    FROM staging.order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(payment_value) AS payment_total
    FROM staging.payments
    GROUP BY order_id
),
review_totals AS (
    SELECT
        order_id,
        AVG(review_score::numeric) AS avg_review_score,
        COUNT(review_score) AS review_count
    FROM staging.reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.purchase_timestamp,
    o.approved_timestamp,
    o.carrier_timestamp,
    o.delivered_timestamp,
    o.estimated_delivery_timestamp,
    COALESCE(i.item_total, 0) AS item_total,
    COALESCE(i.freight_total, 0) AS freight_total,
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(p.payment_total, 0) AS payment_total,
    r.avg_review_score,
    COALESCE(r.review_count, 0) AS review_count,
    CASE
        WHEN o.delivered_timestamp IS NOT NULL
         AND o.estimated_delivery_timestamp IS NOT NULL
        THEN EXTRACT(
            EPOCH FROM (
                o.delivered_timestamp -
                o.estimated_delivery_timestamp
            )
        ) / 86400.0
        ELSE NULL
    END AS delivery_delay_days
FROM staging.orders o
LEFT JOIN staging.customers c
    ON o.customer_id = c.customer_id
LEFT JOIN item_totals i
    ON o.order_id = i.order_id
LEFT JOIN payment_totals p
    ON o.order_id = p.order_id
LEFT JOIN review_totals r
    ON o.order_id = r.order_id;

-- Ensure the mart has unique order IDs.
CREATE UNIQUE INDEX IF NOT EXISTS uq_order_mart_order_id
ON analytics.order_mart(order_id);

-- Verification
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(*) FILTER (
        WHERE avg_review_score IS NOT NULL
    ) AS orders_with_reviews
FROM analytics.order_mart;
