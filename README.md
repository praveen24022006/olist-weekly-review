
# Olist E-commerce Weekly Business Review

## 1. Project Overview
This project builds a data pipeline for analyzing the Olist Brazilian e-commerce marketplace dataset. Raw CSV files are loaded into PostgreSQL, transformed into staging tables and an analysis-ready order mart, and analyzed using SQL and Python.

## 2. Objectives
- Load raw CSV data into PostgreSQL.
- Transform raw data into staging tables and an order-level analytics mart.
- Perform data quality checks and flag failed checks.
- Analyze monthly revenue, product categories, order trends, repeat purchases, and delivery performance.
- Generate charts and business recommendations for a weekly business review.

## 3. Project Structure

```text
olist-weekly-review/
├── data/                  # Input CSV datasets
├── src/
│   ├── load_data.py       # CSV ingestion
│   ├── quality_checks.py  # Data quality checks
│   └── generate_report.py # Chart generation
├── sql/
│   ├── 00_setup_staging_mart.sql
│   ├── q1_monthly_revenue.sql
│   ├── q2_top_categories.sql
│   ├── q3_rolling_orders.sql
│   ├── q4_repeat_purchase.sql
│   └── q5_delivery_reviews.sql
├── reports/               # Generated charts and report outputs
├── requirements.txt
└── README.md
```

## 4. Technology Stack
- Python
- PostgreSQL
- SQL
- Pandas and NumPy
- SQLAlchemy and Psycopg
- Matplotlib
- pgAdmin

## 5. Setup Instructions

### Prerequisites
- Python 3.12
- PostgreSQL
- pgAdmin (optional, for database management)

### Install Python dependencies
```bash
python -m pip install -r requirements.txt
```

### Database configuration
Create a PostgreSQL database named `olist_analytics`.

Load the provided CSV files using `src/load_data.py`. Configure the database connection using your local PostgreSQL credentials.

Run the staging and mart setup SQL in pgAdmin. Then run the analysis queries in the `sql/` directory.

Do not commit database passwords or other secrets to GitHub.

## 6. Data Quality Results
The pipeline checks for duplicate order IDs, null order IDs, delivery before purchase, missing customer records, payment mismatches, and invalid review scores.

Observed results:
- Duplicate order IDs: 0
- Null order IDs: 0
- Delivery before purchase: 0
- Missing customer records: 0
- Payment mismatches: 1,022
- Invalid review scores: 0

Payment mismatches are flagged for investigation rather than automatically deleted. The mismatch check compares recorded payment totals with item and freight totals using a tolerance of 1.00.

## 7. SQL Analysis
1. Month-over-month payment revenue and growth using `LAG`.
2. Top three product categories by state using `DENSE_RANK`.
3. Seven-day rolling average of daily order counts.
4. Repeat-purchase rate using `customer_unique_id`.
5. Average delivery delay by review score.

## 8. Key Findings
- Total orders in the analytics mart: 99,441.
- Orders with review scores: 98,673.
- Repeat-purchase customers: 2,997 out of 96,096 unique customers (3.12%).
- Payment reconciliation checks identified 1,022 mismatches for further investigation.
- Health and beauty was the highest-valued category in the category chart.

The last months in the dataset may be incomplete, so monthly trends should be interpreted cautiously. Delivery timing and review scores show an association; this does not establish causation.

## 9. Charts
The `reports/` directory contains:
- Monthly recorded payment totals
- Top ten product categories by item and freight value
- Review score distribution
- Delivery delay versus review score

## 10. Limitations
- Payment mismatches require further investigation.
- Incomplete final months can affect month-over-month comparisons.
- Observational relationships do not prove causation.
- The pipeline is a local project implementation and is not configured as a production scheduler.
