"""Run all SQL queries via DuckDB"""
import duckdb, pandas as pd

BASE = '/Users/mehekpandey/banking_project/data'
con  = duckdb.connect()

for tbl in ['branches','customers','accounts','transactions','loans','investments','tickets']:
    con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{BASE}/{tbl}.csv')")

queries = {
"B1 Customer Segments": """
    SELECT customer_segment, COUNT(*) AS customers,
           ROUND(AVG(monthly_income),0) AS avg_income,
           ROUND(AVG(credit_score),0) AS avg_credit
    FROM customers GROUP BY customer_segment ORDER BY avg_income DESC
""",
"B4 Loan Book by Type": """
    SELECT loan_type, COUNT(*) AS loans,
           ROUND(SUM(loan_amount)/10000000,2) AS book_crore,
           SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END) AS npa_count,
           ROUND(SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS npa_pct
    FROM loans GROUP BY loan_type ORDER BY book_crore DESC
""",
"I1 Monthly MoM Growth": """
    WITH m AS (
        SELECT txn_month, COUNT(*) AS cnt, ROUND(SUM(amount)/10000000,2) AS vol
        FROM transactions WHERE status='Success' GROUP BY txn_month
    )
    SELECT txn_month, cnt, vol,
           ROUND((vol-LAG(vol) OVER (ORDER BY txn_month))*100.0
                 /NULLIF(LAG(vol) OVER (ORDER BY txn_month),0),2) AS mom_pct
    FROM m ORDER BY txn_month LIMIT 12
""",
"A1 RFM Segments": """
    WITH rfm AS (
        SELECT customer_id,
               DATEDIFF('day', MAX(CAST(txn_date AS DATE)), CAST('2024-12-31' AS DATE)) AS recency,
               COUNT(*) AS freq, SUM(amount) AS monetary,
               NTILE(5) OVER (ORDER BY MAX(txn_date) DESC) AS r,
               NTILE(5) OVER (ORDER BY COUNT(*)) AS f,
               NTILE(5) OVER (ORDER BY SUM(amount)) AS m
        FROM transactions WHERE status='Success' AND txn_type='Debit' GROUP BY customer_id
    )
    SELECT CASE WHEN r>=4 AND f>=4 AND m>=4 THEN 'Champions'
                WHEN r>=3 AND f>=3 THEN 'Loyal'
                WHEN r>=4 AND f<=2 THEN 'Potential'
                WHEN r<=2 AND f>=3 THEN 'At Risk'
                WHEN r<=1 AND f<=1 THEN 'Lost'
                ELSE 'Needs Attention' END AS segment,
           COUNT(*) AS customers, ROUND(AVG(monetary),0) AS avg_spend
    FROM rfm GROUP BY 1 ORDER BY customers DESC
""",
"A6 YoY Business Growth": """
    SELECT txn_year,
           COUNT(*) AS txns,
           COUNT(DISTINCT customer_id) AS customers,
           ROUND(SUM(amount)/10000000,2) AS volume_crore,
           SUM(is_fraud) AS frauds,
           ROUND((SUM(amount)-LAG(SUM(amount)) OVER (ORDER BY txn_year))
                 *100.0/NULLIF(LAG(SUM(amount)) OVER (ORDER BY txn_year),0),2) AS yoy_growth
    FROM transactions WHERE status='Success' GROUP BY txn_year ORDER BY txn_year
""",
"E3 Executive KPI": """
    SELECT (SELECT COUNT(*) FROM customers) AS customers,
           (SELECT ROUND(SUM(current_balance)/10000000,2) FROM accounts WHERE account_status='Active') AS deposits_crore,
           (SELECT ROUND(SUM(loan_amount)/10000000,2) FROM loans) AS loan_book_crore,
           (SELECT ROUND(SUM(CASE WHEN loan_status='NPA' THEN outstanding_amount ELSE 0 END)/SUM(loan_amount)*100,2) FROM loans) AS gnpa_pct,
           (SELECT ROUND(SUM(is_fraud)*100.0/COUNT(*),2) FROM transactions) AS fraud_rate,
           (SELECT ROUND(AVG(satisfaction_score),2) FROM tickets WHERE satisfaction_score IS NOT NULL) AS csat
""",
}

print("="*60)
print("  INDIAFIRST BANK — SQL QUERY RESULTS")
print("="*60)
for name, sql in queries.items():
    print(f"\n{'─'*60}\n  {name}\n{'─'*60}")
    print(con.execute(sql).df().to_string(index=False))

print("\n"+"="*60)
print("  ALL QUERIES PASSED ✅")
print("="*60)
con.close()
