
from pathlib import Path
from getpass import getpass
import logging

import pandas as pd
from sqlalchemy import create_engine, URL, text

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# CSV filenames and PostgreSQL table names
FILES = {
    "olist_orders_dataset.csv": "raw_orders",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_order_payments_dataset.csv": "raw_order_payments",
    "olist_order_reviews_dataset.csv": "raw_order_reviews",
    "olist_customers_dataset.csv": "raw_customers",
    "olist_products_dataset.csv": "raw_products",
    "olist_sellers_dataset.csv": "raw_sellers",
    "olist_geolocation_dataset.csv": "raw_geolocation",
    "product_category_name_translation.csv": "raw_category_translation",
}


def main():
    # Check that all expected CSV files exist
    missing_files = [
        filename for filename in FILES
        if not (DATA_DIR / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing CSV files in {DATA_DIR}: {missing_files}"
        )

    # Connect to PostgreSQL
    password = getpass("Enter PostgreSQL postgres password: ")

    db_url = URL.create(
        drivername="postgresql+psycopg",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="olist_analytics",
    )

    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("PostgreSQL connection successful.")

        # Load each CSV into a raw table
        for filename, table_name in FILES.items():
            csv_path = DATA_DIR / filename

            logger.info("Reading %s", filename)
            df = pd.read_csv(csv_path, low_memory=False)

            if len(df.columns) == 0:
                raise ValueError(f"No columns found in {filename}")

            # Replace table instead of appending duplicate rows
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
                chunksize=2000,
                method="multi",
            )

            logger.info(
                "Loaded %s rows into %s",
                len(df),
                table_name,
            )

        logger.info("All nine CSV files loaded successfully.")

    except Exception:
        logger.exception("Pipeline failed.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
