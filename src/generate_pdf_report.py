
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak
)

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "Olist_Weekly_Business_Review.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=42,
    leftMargin=42,
    topMargin=38,
    bottomMargin=38
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="MainTitle", parent=styles["Title"],
    alignment=TA_CENTER, fontSize=19, leading=23,
    spaceAfter=12
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading2"],
    fontSize=13, leading=16, spaceBefore=8, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="SmallText", parent=styles["BodyText"],
    fontSize=9, leading=12, spaceAfter=5
))

story = []

def heading(text):
    story.append(Paragraph(text, styles["Section"]))

def para(text):
    story.append(Paragraph(text, styles["SmallText"]))

def add_chart(filename, width=6.7*inch, height=3.2*inch):
    path = REPORTS / filename
    if not path.exists():
        para(f"Chart unavailable: {filename}")
        return
    img = Image(str(path))
    scale = min(width / img.imageWidth, height / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    story.append(img)
    story.append(Spacer(1, 8))

# PAGE 1: Overview and data quality
story.append(Paragraph(
    "Weekly Business Review — Olist E-commerce Marketplace",
    styles["MainTitle"]
))
para("<b>Objective:</b> Build a reproducible data-analysis workflow "
     "using Olist marketplace CSV data and PostgreSQL.")
heading("1. Data Pipeline")
para("Nine raw CSV datasets are loaded into PostgreSQL. Staging tables "
     "standardize orders, customers, items, payments and reviews. "
     "The analytics.order_mart provides an order-level view for business "
     "analysis. Python handles ingestion, quality checks and chart generation.")
heading("2. Data Quality Results")

quality_data = [
    ["Check", "Observed failures"],
    ["Duplicate order IDs", "0"],
    ["Null order IDs", "0"],
    ["Delivery before purchase", "0"],
    ["Missing customer records", "0"],
    ["Payment mismatches", "1,022"],
    ["Invalid review scores", "0"],
]
table = Table(quality_data, colWidths=[4.3*inch, 1.5*inch])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 6),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
]))
story.append(table)
story.append(Spacer(1, 8))
para("Payment mismatches were flagged for investigation using a tolerance "
     "of 1.00 between payment totals and item-plus-freight totals. "
     "Flagged records should not be automatically deleted.")
para("The mart contains 99,441 orders and 98,673 orders with review scores.")

story.append(PageBreak())

# PAGE 2: Monthly revenue and category charts
heading("3. Revenue and Product Category Analysis")
para("Monthly recorded payment totals rise across much of the observed "
     "period, with fluctuations in later months. The final months may be "
     "incomplete; therefore, the sharp final decline must not be interpreted "
     "as a confirmed business downturn.")
add_chart("chart1_monthly_revenue.png", height=3.0*inch)

para("The category chart ranks product categories by item price plus "
     "freight value. Health and beauty is the highest-valued category in "
     "the generated chart. This measure is not profit.")
add_chart("chart2_top_categories.png", height=3.0*inch)

story.append(PageBreak())

# PAGE 3: Reviews and delivery
heading("4. Customer Reviews and Delivery Performance")
para("Review scores provide a view of customer feedback. The distribution "
     "chart should be used to identify which scores are most frequent.")
add_chart("chart3_review_distribution.png", height=2.7*inch)

para("Average delivery delay is calculated as actual delivery date minus "
     "estimated delivery date. Negative values indicate delivery before "
     "the estimated date; positive values indicate lateness.")
add_chart("chart4_delivery_vs_review.png", height=2.7*inch)

para("The observed relationship between delivery timing and review score "
     "is associative and does not establish causation.")

story.append(PageBreak())

# PAGE 4: SQL analysis and business recommendations
heading("5. SQL Analysis")
para("<b>Monthly revenue:</b> Uses LAG to compare monthly payment totals "
     "and calculate month-over-month growth.")
para("<b>Category performance by state:</b> Uses DENSE_RANK to rank "
     "product categories within each customer state.")
para("<b>Order trend:</b> Calculates a seven-day rolling average of daily "
     "order counts. Calendar-day gaps should be considered when interpreting "
     "a row-based rolling window.")
para("<b>Repeat purchases:</b> Uses customer_unique_id to identify customers "
     "with more than one order. The observed repeat-purchase rate is "
     "2,997 / 96,096 = 3.12%.")
para("<b>Delivery and reviews:</b> Compares average delivery delay with "
     "review scores to explore a possible relationship.")

heading("6. VP Memo")
para("<b>To:</b> Marketplace Leadership")
para("<b>Subject:</b> Customer retention, delivery experience and payment quality")
para("The analysis highlights three areas for action. First, the repeat-purchase "
     "rate is 3.12%, so customer retention merits further investigation. "
     "Second, review scores and delivery timing should be monitored together "
     "to identify service improvements. Third, 1,022 payment mismatches require "
     "reconciliation and investigation.")
para("<b>Recommendations</b>")
para("1. Investigate payment mismatches by order status and transaction details.")
para("2. Monitor delivery delay and review-score trends together.")
para("3. Explore customer retention by cohort and purchase frequency.")
para("4. Annotate incomplete months in revenue reports and avoid unsupported "
     "conclusions about recent declines.")
heading("Limitations")
para("The findings depend on the available dataset and implemented checks. "
     "Payment mismatches are flagged, not proven errors. Observational "
     "associations do not prove causation. The pipeline is a local project "
     "implementation, not a scheduled production service.")

doc.build(story)
print(f"PDF report created: {OUTPUT}")
