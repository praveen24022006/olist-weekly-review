
from pathlib import Path
from getpass import getpass
import logging

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, URL, text

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    password = getpass("PostgreSQL postgres password: ")

    url = URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="olist_analytics",
    )
    engine = create_engine(url)

    try:
        # Chart 1: Monthly payment totals
        monthly = pd.read_sql(text("""
            SELECT DATE_TRUNC('month', purchase_timestamp)::date AS month,
                   SUM(payment_total) AS revenue
            FROM analytics.order_mart
            WHERE order_status <> 'unavailable'
            GROUP BY 1
            ORDER BY 1
        """), engine)

        plt.figure(figsize=(10, 5))
        plt.plot(monthly["month"], monthly["revenue"], marker="o")
        plt.title("Monthly Recorded Payment Totals")
        plt.xlabel("Month")
        plt.ylabel("Payment total (dataset currency)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(REPORT_DIR / "chart1_monthly_revenue.png", dpi=150)
        plt.close()

        # Chart 2: Top 10 product categories
        categories = pd.read_sql(text("""
            SELECT COALESCE(t.product_category_name_english,
                            p.product_category_name, 'unknown') AS category,
                   SUM(oi.price + oi.freight_value) AS revenue
            FROM staging.order_items oi
            JOIN staging.orders o ON oi.order_id = o.order_id
            JOIN raw_products p ON oi.product_id = p.product_id
            LEFT JOIN raw_category_translation t
              ON p.product_category_name = t.product_category_name
            WHERE o.order_status <> 'unavailable'
            GROUP BY 1
            ORDER BY revenue DESC
            LIMIT 10
        """), engine)

        categories = categories.sort_values("revenue")
        plt.figure(figsize=(10, 6))
        plt.barh(categories["category"], categories["revenue"])
        plt.title("Top 10 Product Categories by Item + Freight Value")
        plt.xlabel("Value (dataset currency)")
        plt.ylabel("Product category")
        plt.tight_layout()
        plt.savefig(REPORT_DIR / "chart2_top_categories.png", dpi=150)
        plt.close()

        # Chart 3: Review score distribution
        reviews = pd.read_sql(text("""
            SELECT review_score, COUNT(*) AS review_count
            FROM staging.reviews
            WHERE review_score BETWEEN 1 AND 5
            GROUP BY review_score
            ORDER BY review_score
        """), engine)

        plt.figure(figsize=(7, 5))
        plt.bar(reviews["review_score"].astype(str), reviews["review_count"])
        plt.title("Distribution of Review Scores")
        plt.xlabel("Review score")
        plt.ylabel("Number of review records")
        plt.tight_layout()
        plt.savefig(REPORT_DIR / "chart3_review_distribution.png", dpi=150)
        plt.close()

        # Chart 4: Delivery delay versus review score
        delivery = pd.read_sql(text("""
            SELECT ROUND(avg_review_score)::integer AS review_score,
                   AVG(delivery_delay_days) AS avg_delay
            FROM analytics.order_mart
            WHERE delivered_date IS NOT NULL
              AND estimated_delivery_date IS NOT NULL
              AND avg_review_score IS NOT NULL
            GROUP BY 1
            ORDER BY 1
        """), engine)

        plt.figure(figsize=(7, 5))
        plt.bar(delivery["review_score"].astype(str), delivery["avg_delay"])
        plt.axhline(0, linewidth=1)
        plt.title("Average Delivery Delay by Review Score")
        plt.xlabel("Review score")
        plt.ylabel("Delay in days (negative = early)")
        plt.tight_layout()
        plt.savefig(REPORT_DIR / "chart4_delivery_vs_review.png", dpi=150)
        plt.close()

        logger.info("All four charts saved in %s", REPORT_DIR)

    except Exception:
        logger.exception("Chart generation failed.")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
