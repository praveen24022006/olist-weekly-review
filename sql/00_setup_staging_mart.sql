
-- Olist Weekly Business Review
-- Database setup verification
-- Run in the olist_analytics database.

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Verify that all required staging and mart tables exist.
DO $$
DECLARE
    required_table TEXT;
BEGIN
    FOREACH required_table IN ARRAY ARRAY[
        'staging.orders',
        'staging.customers',
        'staging.order_items',
        'staging.payments',
        'staging.reviews',
        'analytics.order_mart'
    ]
    LOOP
        IF to_regclass(required_table) IS NULL THEN
            RAISE EXCEPTION 'Required table is missing: %',
                required_table;
        END IF;
    END LOOP;

    RAISE NOTICE
        'All required staging tables and analytics.order_mart exist.';
END $$;

-- Mart row-count and uniqueness verification.
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(*) FILTER (
        WHERE avg_review_score IS NOT NULL
    ) AS orders_with_reviews
FROM analytics.order_mart;
