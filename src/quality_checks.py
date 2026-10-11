
from getpass import getpass
import logging

from sqlalchemy import create_engine, URL, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

CHECKS = {
    "null_order_id": """
        SELECT COUNT(*) FROM staging.orders
        WHERE order_id IS NULL
    """,
    "duplicate_order_id": """
        SELECT COUNT(*) FROM (
            SELECT order_id
            FROM staging.orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) d
    """,
    "delivery_before_purchase": """
        SELECT COUNT(*) FROM staging.orders
        WHERE delivered_date < purchase_timestamp
    """,
    "missing_customer": """
        SELECT COUNT(*)
        FROM staging.orders o
        LEFT JOIN staging.customers c
          ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """,
    "invalid_review_score": """
        SELECT COUNT(*) FROM staging.reviews
        WHERE review_score NOT BETWEEN 1 AND 5
    """,
    "payment_mismatch": """
        SELECT COUNT(*) FROM analytics.order_mart
        WHERE ABS(payment_total - item_total - freight_total) > 1.00
    """,
}


def main():
    password = getpass("PostgreSQL password: ")

    url = URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="olist_analytics",
    )
    engine = create_engine(url)
    failures = []

    try:
        with engine.connect() as conn:
            for name, query in CHECKS.items():
                failed_rows = conn.execute(text(query)).scalar_one()
                logger.info("%s: %s failed rows", name, failed_rows)

                if failed_rows > 0:
                    failures.append((name, failed_rows))

        if failures:
            details = ", ".join(
                f"{name}={count}" for name, count in failures
            )
            raise RuntimeError(
                f"DATA QUALITY ALARM: {details}"
            )

        logger.info("All data-quality checks passed.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
