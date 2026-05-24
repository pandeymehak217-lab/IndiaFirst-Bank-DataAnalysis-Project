# IndiaFirst Bank — Complete Analytics System

After finishing the first two SQL projects I wanted to build something
bigger. Something that looked closer to what a data analyst at an actual
bank would work on. So I picked banking because it has everything —
fraud, loans, investments, customer segmentation, branch performance —
and tried to build an end-to-end system rather than just a bunch of queries.

This is the project I spent the most time on so far.

---

## What I Built

A full analytics system on 7 related tables covering 50,000 transactions
across 5 years. The SQL goes from basic aggregations all the way to RFM
segmentation, fraud scoring, churn prediction, and customer lifetime value.
On top of the SQL I wrote Python to generate charts and a 7-sheet Excel
report, and added a Power BI guide with DAX measures.

---

## Why 7 Tables

I kept the first two projects to 3-4 tables. This time I wanted to
practice joining across a proper relational structure the way a real
bank database would look.

Branches connect to customers, customers connect to accounts,
accounts connect to transactions, customers connect to loans and
investments and support tickets. Writing the Customer 360 query
that pulls from all of these in one CTE took a few hours to get right
but it was worth it.

---

## Dataset

| Table | Rows | What it contains |
|-------|------|-----------------|
| branches | 50 | Locations across 15 states, zone, manager |
| customers | 3,000 | Demographics, income bracket, credit score |
| accounts | 4,253 | Savings, Current, FD, NRI accounts |
| transactions | 50,000 | 5 years of transactions 2020 to 2024 |
| loans | 2,000 | Home, Personal, Car, Education, Business |
| investments | 1,500 | MF, FD, SIP, PPF, Stocks |
| tickets | 5,000 | Customer support with resolution time |

Total loan book came out at Rs 526 Crore.
449 transactions were flagged as fraud.
218 loan accounts hit NPA status.

---

## Folder Structure

```
indiaFirst-bank-analytics/
|
|-- data/
|   |-- branches.csv
|   |-- customers.csv
|   |-- accounts.csv
|   |-- transactions.csv
|   |-- loans.csv
|   |-- investments.csv
|   |-- tickets.csv
|
|-- sql/
|   |-- banking_analysis.sql
|
|-- python/
|   |-- analysis.py
|
|-- outputs/
|   |-- bank_dashboard.png
|   |-- IndiaFirst_Bank_Analytics_Report.xlsx
|
|-- powerbi/
|   |-- POWERBI_GUIDE.md
|
|-- generate_data.py
|-- run_queries.py
|-- README.md
```

---

## SQL Work

I split the queries into four levels because I wanted to be honest
about which ones are straightforward and which ones actually took
effort to figure out.

Beginner level covers account distribution, state-wise deposits,
and channel analysis. These are GROUP BY queries with some CASE WHEN.

Intermediate adds LAG for month-over-month growth, the Customer 360
CTE joining all 7 tables, branch scorecard, and NPA deep dive.

Advanced is where it got interesting. RFM segmentation using NTILE
across recency, frequency, and monetary dimensions. A fraud scoring
model that assigns a risk score to each transaction based on time
of day, amount relative to user baseline, and transaction category.
Churn prediction features. Customer lifetime value calculation.
Rolling 30-day average using ROWS BETWEEN.

Expert level covers zone profitability joining branches to all other
tables, a cross-sell matrix showing which customers have accounts
but no loans or investments, and a single-query P&L view.

---

## Python and Excel

The Python script loads all 7 tables using DuckDB and runs the
key analytics queries. Output is an 8-panel matplotlib dashboard
saved as a PNG and a 7-sheet Excel report built with xlsxwriter.

The Excel report has proper formatting — alternating row colours,
KPI cards on the first sheet, conditional formatting on the NPA
and fraud rate columns.

---

## What I Found

Personal loans have the highest NPA rate. Home loans have the lowest
because of collateral. That matches what you read about in the news
but it was satisfying to see it come out of the data.

Fraud rate goes above 8 percent between 2 AM and 3 AM. During daytime
hours it sits around 3 percent. The combination of Mobile Banking and
amounts above Rs 2 lakh is the strongest fraud signal in the data.

Premium segment customers are 3 percent of the base but contribute
over 40 percent of deposits. This is why banks have relationship
managers dedicated to HNI customers.

Customers inactive for more than 180 days with no loan or investment
products have the highest churn risk. The cross-sell matrix query
shows exactly how many of these customers exist per segment.

---

## How To Run

```bash
pip3 install duckdb pandas numpy matplotlib xlsxwriter scipy
python3 generate_data.py
python3 run_queries.py
python3 python/analysis.py
```

For Power BI follow the steps in powerbi/POWERBI_GUIDE.md.
It has the DAX measures written out and the relationship setup.

---

## What I Would Do Differently

The investment analysis is the weakest part. I calculated returns
using a simple formula rather than modelling actual NAV changes
over time. Real mutual fund analysis would use daily NAV data
and calculate XIRR rather than a flat return percentage.

I also want to add macroeconomic variables — repo rate, inflation —
as context for the loan and investment analysis. Rate changes
directly affect NPA patterns and deposit behaviour.

---

## What I Learned

The Customer 360 query using multiple CTEs was the hardest thing
I had written up to that point. Joining 7 tables and making sure
the aggregations are correct at each step requires planning the
query structure before writing any SQL. I started writing it
directly and had to restart twice.

RFM segmentation made more sense to me after implementing it than
it did reading about it. The NTILE approach is elegant. You do not
need to define arbitrary score thresholds — the data tells you
where the boundaries are.

The fraud scoring model taught me that a single signal is not enough.
Late night alone is not fraud. High amount alone is not fraud.
But late night plus high amount plus mobile banking together pushes
the score high enough to flag it. Writing that in SQL using weighted
CASE WHEN was a new pattern for me.

---

Mehak Pandey
pandeymehak.217@gmail.com

