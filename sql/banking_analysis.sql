-- ================================================================
--  INDIAFIRST BANK — COMPLETE ANALYTICS SYSTEM
--  Advanced SQL Portfolio Project (Beginner → Expert Level)
--  Author  : [Your Name]
--  Dataset : 7 Tables | 50,000 Transactions | 3,000 Customers
--            2,000 Loans | 1,500 Investments | 2020–2024
-- ================================================================

-- ───────────────────────────────────────────────
--  BEGINNER LEVEL — Core SQL
-- ───────────────────────────────────────────────

-- B1. Total customers by segment
SELECT customer_segment, COUNT(*) AS customers,
       ROUND(AVG(monthly_income),0) AS avg_income,
       ROUND(AVG(credit_score),0)   AS avg_credit_score
FROM customers
GROUP BY customer_segment
ORDER BY avg_income DESC;

-- B2. Account type distribution
SELECT account_type, account_status,
       COUNT(*) AS accounts,
       ROUND(SUM(current_balance),0) AS total_balance,
       ROUND(AVG(current_balance),0) AS avg_balance
FROM accounts
GROUP BY account_type, account_status
ORDER BY account_type, accounts DESC;

-- B3. Transaction volume by channel
SELECT channel,
       COUNT(*) AS total_txns,
       ROUND(SUM(amount),0) AS total_volume,
       ROUND(AVG(amount),0) AS avg_amount,
       SUM(CASE WHEN status='Success' THEN 1 ELSE 0 END) AS success_count,
       ROUND(SUM(CASE WHEN status='Success' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS success_rate
FROM transactions
GROUP BY channel ORDER BY total_volume DESC;

-- B4. Loan book summary by type
SELECT loan_type,
       COUNT(*) AS loan_count,
       ROUND(SUM(loan_amount)/10000000,2) AS total_book_crore,
       ROUND(AVG(loan_amount),0) AS avg_loan,
       ROUND(AVG(interest_rate),2) AS avg_rate,
       SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END) AS npa_count,
       ROUND(SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS npa_rate_pct
FROM loans
GROUP BY loan_type ORDER BY total_book_crore DESC;

-- B5. State-wise customer distribution
SELECT c.state,
       COUNT(DISTINCT c.customer_id) AS customers,
       COUNT(DISTINCT a.account_id) AS accounts,
       ROUND(SUM(a.current_balance)/10000000,2) AS total_deposits_crore
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.state ORDER BY customers DESC;

-- ───────────────────────────────────────────────
--  INTERMEDIATE LEVEL — CTEs, Joins, Subqueries
-- ───────────────────────────────────────────────

-- I1. Monthly transaction trend with MoM growth
WITH monthly AS (
    SELECT txn_month, txn_year,
           COUNT(*) AS txn_count,
           ROUND(SUM(CASE WHEN txn_type='Credit' THEN amount ELSE 0 END),0) AS credits,
           ROUND(SUM(CASE WHEN txn_type='Debit'  THEN amount ELSE 0 END),0) AS debits,
           ROUND(SUM(amount),0) AS total_volume
    FROM transactions WHERE status='Success'
    GROUP BY txn_month, txn_year
)
SELECT txn_month, txn_count, credits, debits, total_volume,
       LAG(total_volume) OVER (ORDER BY txn_month) AS prev_month_volume,
       ROUND((total_volume - LAG(total_volume) OVER (ORDER BY txn_month))*100.0
             / NULLIF(LAG(total_volume) OVER (ORDER BY txn_month),0),2) AS mom_growth_pct
FROM monthly ORDER BY txn_month;

-- I2. Customer 360 — full profile with all products
WITH cust_accounts AS (
    SELECT customer_id, COUNT(*) AS account_count,
           ROUND(SUM(current_balance),0) AS total_balance,
           STRING_AGG(account_type, ', ') AS account_types
    FROM accounts WHERE account_status='Active'
    GROUP BY customer_id
),
cust_loans AS (
    SELECT customer_id, COUNT(*) AS loan_count,
           ROUND(SUM(loan_amount),0) AS total_loans,
           ROUND(SUM(outstanding_amount),0) AS outstanding
    FROM loans WHERE loan_status='Active'
    GROUP BY customer_id
),
cust_investments AS (
    SELECT customer_id, COUNT(*) AS inv_count,
           ROUND(SUM(invested_amount),0) AS total_invested,
           ROUND(SUM(current_value),0) AS current_value
    FROM investments WHERE status='Active'
    GROUP BY customer_id
),
cust_txns AS (
    SELECT customer_id, COUNT(*) AS txn_count,
           ROUND(SUM(amount),0) AS total_txn_volume,
           MAX(txn_date) AS last_txn_date
    FROM transactions WHERE status='Success'
    GROUP BY customer_id
)
SELECT c.customer_id, c.customer_name, c.customer_segment,
       c.monthly_income, c.credit_score, c.occupation,
       COALESCE(ca.account_count,0)   AS accounts,
       COALESCE(ca.total_balance,0)   AS total_balance,
       COALESCE(cl.loan_count,0)      AS active_loans,
       COALESCE(cl.outstanding,0)     AS loan_outstanding,
       COALESCE(ci.inv_count,0)       AS investments,
       COALESCE(ci.current_value,0)   AS investment_value,
       COALESCE(ct.txn_count,0)       AS total_transactions,
       ct.last_txn_date,
       -- Relationship depth score
       COALESCE(ca.account_count,0) +
       COALESCE(cl.loan_count,0)*2 +
       COALESCE(ci.inv_count,0)*2    AS relationship_score
FROM customers c
LEFT JOIN cust_accounts    ca ON c.customer_id = ca.customer_id
LEFT JOIN cust_loans       cl ON c.customer_id = cl.customer_id
LEFT JOIN cust_investments ci ON c.customer_id = ci.customer_id
LEFT JOIN cust_txns        ct ON c.customer_id = ct.customer_id
ORDER BY relationship_score DESC
LIMIT 20;

-- I3. Branch performance scorecard
SELECT b.branch_id, b.branch_name, b.city, b.state, b.zone,
       COUNT(DISTINCT c.customer_id)          AS total_customers,
       COUNT(DISTINCT a.account_id)           AS total_accounts,
       ROUND(SUM(a.current_balance)/10000000,2) AS deposits_crore,
       COUNT(DISTINCT l.loan_id)              AS loans_sanctioned,
       ROUND(SUM(l.loan_amount)/10000000,2)   AS loan_book_crore,
       ROUND(SUM(CASE WHEN l.loan_status='NPA' THEN l.loan_amount ELSE 0 END)
             / NULLIF(SUM(l.loan_amount),0)*100,2) AS gnpa_pct,
       ROUND(SUM(a.current_balance)/10000000 +
             SUM(l.loan_amount)/10000000,2)   AS total_business_crore
FROM branches b
LEFT JOIN customers c   ON b.branch_id = c.branch_id
LEFT JOIN accounts a    ON c.customer_id = a.customer_id
LEFT JOIN loans l       ON b.branch_id = l.branch_id
GROUP BY b.branch_id, b.branch_name, b.city, b.state, b.zone
ORDER BY total_business_crore DESC
LIMIT 20;

-- I4. NPA (Non-Performing Asset) deep dive
SELECT l.loan_type,
       l.loan_status,
       COUNT(*) AS loan_count,
       ROUND(SUM(l.outstanding_amount)/10000000,2) AS npa_amount_crore,
       ROUND(AVG(l.days_past_due),0) AS avg_dpd,
       ROUND(AVG(c.credit_score),0)  AS avg_credit_score,
       ROUND(AVG(c.monthly_income),0) AS avg_income,
       -- Recovery potential (simplified)
       ROUND(SUM(CASE WHEN l.collateral_type!='None'
             THEN l.outstanding_amount*0.7 ELSE l.outstanding_amount*0.3 END)
             /10000000,2) AS estimated_recovery_crore
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE l.loan_status IN ('NPA','Special Mention')
GROUP BY l.loan_type, l.loan_status
ORDER BY npa_amount_crore DESC;

-- ───────────────────────────────────────────────
--  ADVANCED LEVEL — Window Functions + Complex Analytics
-- ───────────────────────────────────────────────

-- A1. Customer RFM (Recency-Frequency-Monetary) Segmentation
--     The most important marketing analytics model
WITH rfm_base AS (
    SELECT customer_id,
           MAX(txn_date)  AS last_txn_date,
           COUNT(*)       AS frequency,
           ROUND(SUM(amount),0) AS monetary
    FROM transactions
    WHERE status='Success' AND txn_type='Debit'
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT customer_id, last_txn_date, frequency, monetary,
           DATEDIFF('2024-12-31', last_txn_date)      AS recency_days,
           NTILE(5) OVER (ORDER BY MAX(last_txn_date) DESC)  AS r_score,
           NTILE(5) OVER (ORDER BY COUNT(*))                  AS f_score,
           NTILE(5) OVER (ORDER BY SUM(amount))               AS m_score
    FROM rfm_base
    GROUP BY customer_id, last_txn_date, frequency, monetary
)
SELECT r.customer_id, c.customer_name, c.customer_segment,
       r.recency_days, r.frequency, r.monetary,
       r.r_score, r.f_score, r.m_score,
       r.r_score + r.f_score + r.m_score AS rfm_total,
       CASE
           WHEN r.r_score>=4 AND r.f_score>=4 AND r.m_score>=4 THEN '💎 Champions'
           WHEN r.r_score>=3 AND r.f_score>=3                  THEN '🥇 Loyal Customers'
           WHEN r.r_score>=4 AND r.f_score<=2                  THEN '🌟 Potential Loyalist'
           WHEN r.r_score>=4 AND r.f_score=1                   THEN '🆕 New Customers'
           WHEN r.r_score<=2 AND r.f_score>=3 AND r.m_score>=3 THEN '😴 At Risk'
           WHEN r.r_score<=2 AND r.f_score>=4 AND r.m_score>=4 THEN '😱 Cant Lose Them'
           WHEN r.r_score<=1 AND r.f_score<=1                  THEN '💀 Lost'
           ELSE '🔮 Needs Attention'
       END AS rfm_segment
FROM rfm_scores r
JOIN customers c ON r.customer_id = c.customer_id
ORDER BY rfm_total DESC;

-- A2. Fraud Detection — Multi-signal scoring model
WITH user_baselines AS (
    SELECT customer_id,
           AVG(amount)    AS avg_amount,
           STDDEV(amount) AS std_amount,
           AVG(txn_hour)  AS avg_hour
    FROM transactions WHERE status='Success' AND is_fraud=0
    GROUP BY customer_id
),
fraud_signals AS (
    SELECT t.txn_id, t.customer_id, t.txn_date, t.amount,
           t.channel, t.category, t.txn_hour, t.is_fraud,
           t.status,
           -- Signal 1: Amount anomaly (z-score)
           ROUND((t.amount - b.avg_amount)/NULLIF(b.std_amount,0),2) AS amount_zscore,
           -- Signal 2: Night transaction
           CASE WHEN t.txn_hour BETWEEN 1 AND 4 THEN 1 ELSE 0 END AS is_night_txn,
           -- Signal 3: Large amount
           CASE WHEN t.amount > 500000 THEN 1 ELSE 0 END AS is_large_txn,
           -- Signal 4: High risk category
           CASE WHEN t.category IN ('Fund Transfer','Cash Withdrawal') THEN 1 ELSE 0 END AS is_high_risk_cat,
           -- Composite fraud score
           CASE WHEN t.txn_hour BETWEEN 1 AND 4 THEN 30 ELSE 0 END +
           CASE WHEN t.amount > 500000 THEN 25 ELSE 0 END +
           CASE WHEN t.amount > b.avg_amount + 3*b.std_amount THEN 25 ELSE 0 END +
           CASE WHEN t.category IN ('Fund Transfer','Cash Withdrawal') THEN 10 ELSE 0 END +
           CASE WHEN t.channel = 'Mobile Banking' AND t.amount>200000 THEN 10 ELSE 0 END
               AS fraud_risk_score
    FROM transactions t
    LEFT JOIN user_baselines b ON t.customer_id = b.customer_id
    WHERE t.status = 'Success'
)
SELECT txn_id, customer_id, txn_date, amount, channel, category,
       txn_hour, amount_zscore, is_night_txn, is_large_txn,
       fraud_risk_score, is_fraud,
       CASE WHEN fraud_risk_score >= 60 THEN '🔴 HIGH RISK'
            WHEN fraud_risk_score >= 30 THEN '🟡 MEDIUM RISK'
            ELSE '🟢 LOW RISK'
       END AS risk_level
FROM fraud_signals
WHERE fraud_risk_score > 0
ORDER BY fraud_risk_score DESC
LIMIT 30;

-- A3. Running Balance & 30-day Rolling Average per account
WITH daily_account AS (
    SELECT account_id, txn_date,
           SUM(CASE WHEN txn_type='Credit' THEN amount ELSE -amount END) AS net_flow
    FROM transactions WHERE status='Success'
    GROUP BY account_id, txn_date
)
SELECT account_id, txn_date, net_flow,
       SUM(net_flow) OVER (
           PARTITION BY account_id ORDER BY txn_date
           ROWS UNBOUNDED PRECEDING
       ) AS running_balance,
       ROUND(AVG(net_flow) OVER (
           PARTITION BY account_id ORDER BY txn_date
           ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
       ),0) AS rolling_30d_avg
FROM daily_account
ORDER BY account_id, txn_date
LIMIT 50;

-- A4. Customer Churn Prediction Features
--     Customers with no transaction in last 90 days = At Risk
WITH last_activity AS (
    SELECT customer_id,
           MAX(txn_date)  AS last_txn_date,
           COUNT(*)       AS total_txns,
           ROUND(SUM(amount),0) AS total_spend,
           DATEDIFF('2024-12-31', MAX(txn_date)) AS days_inactive
    FROM transactions WHERE status='Success'
    GROUP BY customer_id
),
churn_features AS (
    SELECT c.customer_id, c.customer_name, c.customer_segment,
           c.monthly_income, c.credit_score, c.occupation,
           la.last_txn_date, la.total_txns,
           la.total_spend, la.days_inactive,
           COUNT(DISTINCT a.account_id) AS account_count,
           COALESCE(COUNT(DISTINCT l.loan_id),0) AS loan_count,
           COALESCE(COUNT(DISTINCT i.investment_id),0) AS inv_count,
           COALESCE(SUM(tk.ticket_id IS NOT NULL),0) AS support_tickets,
           -- Churn risk score
           CASE WHEN la.days_inactive > 180 THEN 40
                WHEN la.days_inactive > 90  THEN 20
                ELSE 0 END +
           CASE WHEN la.total_txns < 5 THEN 20 ELSE 0 END +
           CASE WHEN c.customer_segment = 'Basic' THEN 15 ELSE 0 END +
           CASE WHEN COUNT(DISTINCT l.loan_id) = 0
                AND COUNT(DISTINCT i.investment_id)=0 THEN 25 ELSE 0 END
               AS churn_risk_score
    FROM customers c
    LEFT JOIN last_activity la ON c.customer_id = la.customer_id
    LEFT JOIN accounts a ON c.customer_id = a.customer_id AND a.account_status='Active'
    LEFT JOIN loans l ON c.customer_id = l.customer_id AND l.loan_status='Active'
    LEFT JOIN investments i ON c.customer_id = i.customer_id AND i.status='Active'
    LEFT JOIN tickets tk ON c.customer_id = tk.customer_id
    GROUP BY c.customer_id, c.customer_name, c.customer_segment,
             c.monthly_income, c.credit_score, c.occupation,
             la.last_txn_date, la.total_txns, la.total_spend, la.days_inactive
)
SELECT *,
       CASE WHEN churn_risk_score >= 60 THEN '🔴 High Churn Risk'
            WHEN churn_risk_score >= 35 THEN '🟡 Medium Risk'
            ELSE '🟢 Retained'
       END AS churn_label
FROM churn_features
ORDER BY churn_risk_score DESC
LIMIT 25;

-- A5. Investment Portfolio Analysis — Returns vs Risk
SELECT i.investment_type, i.risk_category,
       COUNT(*) AS investors,
       ROUND(SUM(i.invested_amount)/10000000,2) AS total_invested_crore,
       ROUND(SUM(i.current_value)/10000000,2)   AS current_value_crore,
       ROUND(AVG(i.returns_pct),2)              AS avg_return_pct,
       ROUND(MAX(i.returns_pct),2)              AS max_return_pct,
       ROUND(MIN(i.returns_pct),2)              AS min_return_pct,
       ROUND(STDDEV(i.returns_pct),2)           AS return_volatility,
       -- Sharpe-like ratio (return/volatility)
       ROUND(AVG(i.returns_pct)/NULLIF(STDDEV(i.returns_pct),0),2) AS risk_adj_return,
       RANK() OVER (ORDER BY AVG(i.returns_pct) DESC) AS return_rank
FROM investments i
GROUP BY i.investment_type, i.risk_category
ORDER BY avg_return_pct DESC;

-- A6. Year-over-Year Business Growth (Full P&L View)
SELECT txn_year,
       COUNT(*) AS total_txns,
       COUNT(DISTINCT customer_id) AS active_customers,
       ROUND(SUM(CASE WHEN txn_type='Credit' THEN amount ELSE 0 END)/10000000,2) AS total_credits_crore,
       ROUND(SUM(CASE WHEN txn_type='Debit'  THEN amount ELSE 0 END)/10000000,2) AS total_debits_crore,
       ROUND(SUM(amount)/10000000,2) AS total_volume_crore,
       SUM(is_fraud) AS fraud_count,
       ROUND(SUM(is_fraud)*100.0/COUNT(*),2) AS fraud_rate_pct,
       -- YoY growth using LAG
       ROUND((SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY txn_year))
             *100.0/NULLIF(LAG(SUM(amount)) OVER (ORDER BY txn_year),0),2) AS yoy_volume_growth
FROM transactions
WHERE status='Success'
GROUP BY txn_year ORDER BY txn_year;

-- A7. Top 10 Customers by CLV (Customer Lifetime Value)
WITH clv AS (
    SELECT t.customer_id,
           ROUND(SUM(t.amount),0)              AS total_txn_value,
           COUNT(t.txn_id)                     AS txn_count,
           COALESCE(SUM(l.loan_amount),0)      AS total_loans,
           COALESCE(SUM(i.invested_amount),0)  AS total_invested,
           COALESCE(SUM(l.loan_amount)*0.025,0)  AS est_loan_revenue,
           COALESCE(SUM(i.invested_amount)*0.01,0) AS est_inv_revenue,
           -- Simple CLV = transaction revenue + loan interest + investment fees
           ROUND(SUM(t.amount)*0.001 +
                 COALESCE(SUM(l.loan_amount)*0.025,0) +
                 COALESCE(SUM(i.invested_amount)*0.01,0), 0) AS estimated_clv
    FROM transactions t
    LEFT JOIN loans l ON t.customer_id=l.customer_id
    LEFT JOIN investments i ON t.customer_id=i.customer_id
    WHERE t.status='Success'
    GROUP BY t.customer_id
)
SELECT clv.customer_id, c.customer_name, c.customer_segment,
       c.occupation, c.monthly_income, c.credit_score,
       clv.txn_count, clv.total_txn_value,
       clv.total_loans, clv.total_invested,
       clv.estimated_clv,
       RANK() OVER (ORDER BY clv.estimated_clv DESC) AS clv_rank
FROM clv
JOIN customers c ON clv.customer_id=c.customer_id
ORDER BY estimated_clv DESC
LIMIT 10;

-- A8. Support Ticket SLA Analysis
SELECT category, priority,
       COUNT(*) AS tickets,
       COUNT(CASE WHEN status='Resolved' THEN 1 END) AS resolved,
       ROUND(COUNT(CASE WHEN status='Resolved' THEN 1 END)*100.0/COUNT(*),1) AS resolution_rate,
       ROUND(AVG(CASE WHEN status='Resolved' THEN resolution_hours END),1) AS avg_resolution_hrs,
       ROUND(AVG(satisfaction_score),2) AS avg_satisfaction,
       -- SLA breach (>24hrs for Critical, >48hrs for High, >72hrs for Medium)
       COUNT(CASE WHEN priority='Critical' AND resolution_hours>24 THEN 1
                  WHEN priority='High'     AND resolution_hours>48 THEN 1
                  WHEN priority='Medium'   AND resolution_hours>72 THEN 1 END) AS sla_breaches
FROM tickets
GROUP BY category, priority
ORDER BY priority, tickets DESC;

-- ───────────────────────────────────────────────
--  EXPERT LEVEL — Complex Multi-table Analytics
-- ───────────────────────────────────────────────

-- E1. Zone-wise Profitability Dashboard
WITH zone_metrics AS (
    SELECT b.zone,
           COUNT(DISTINCT c.customer_id) AS customers,
           ROUND(SUM(a.current_balance)/10000000,2) AS deposits_crore,
           ROUND(SUM(l.loan_amount)/10000000,2) AS loans_crore,
           ROUND(SUM(CASE WHEN l.loan_status='NPA' THEN l.outstanding_amount ELSE 0 END)
                 /10000000,2) AS npa_crore,
           ROUND(SUM(i.invested_amount)/10000000,2) AS aum_crore
    FROM branches b
    JOIN customers c ON b.branch_id=c.branch_id
    LEFT JOIN accounts a ON c.customer_id=a.customer_id AND a.account_status='Active'
    LEFT JOIN loans l ON b.branch_id=l.branch_id
    LEFT JOIN investments i ON c.customer_id=i.customer_id AND i.status='Active'
    GROUP BY b.zone
)
SELECT zone, customers, deposits_crore, loans_crore,
       npa_crore, aum_crore,
       ROUND(deposits_crore + loans_crore + aum_crore,2) AS total_business_crore,
       ROUND(npa_crore/NULLIF(loans_crore,0)*100,2) AS gnpa_pct,
       RANK() OVER (ORDER BY deposits_crore+loans_crore+aum_crore DESC) AS zone_rank
FROM zone_metrics ORDER BY total_business_crore DESC;

-- E2. Cross-sell opportunity matrix
--     Which customers have accounts but NO loans or investments?
SELECT c.customer_segment,
       c.occupation,
       COUNT(DISTINCT c.customer_id) AS total_customers,
       COUNT(DISTINCT CASE WHEN l.loan_id IS NOT NULL THEN c.customer_id END) AS has_loan,
       COUNT(DISTINCT CASE WHEN i.investment_id IS NOT NULL THEN c.customer_id END) AS has_investment,
       COUNT(DISTINCT CASE WHEN l.loan_id IS NULL THEN c.customer_id END) AS loan_cross_sell_oppty,
       COUNT(DISTINCT CASE WHEN i.investment_id IS NULL THEN c.customer_id END) AS inv_cross_sell_oppty,
       ROUND(COUNT(DISTINCT CASE WHEN l.loan_id IS NULL THEN c.customer_id END)*100.0
             /COUNT(DISTINCT c.customer_id),1) AS loan_oppty_pct,
       ROUND(COUNT(DISTINCT CASE WHEN i.investment_id IS NULL THEN c.customer_id END)*100.0
             /COUNT(DISTINCT c.customer_id),1) AS inv_oppty_pct
FROM customers c
LEFT JOIN loans l ON c.customer_id=l.customer_id AND l.loan_status='Active'
LEFT JOIN investments i ON c.customer_id=i.customer_id AND i.status='Active'
GROUP BY c.customer_segment, c.occupation
ORDER BY loan_cross_sell_oppty DESC;

-- E3. Complete Executive KPI Dashboard — Single Query
SELECT
    (SELECT COUNT(*) FROM customers) AS total_customers,
    (SELECT COUNT(*) FROM accounts WHERE account_status='Active') AS active_accounts,
    (SELECT ROUND(SUM(current_balance)/10000000,2) FROM accounts WHERE account_status='Active') AS total_deposits_crore,
    (SELECT ROUND(SUM(loan_amount)/10000000,2) FROM loans) AS total_loan_book_crore,
    (SELECT ROUND(SUM(CASE WHEN loan_status='NPA' THEN outstanding_amount ELSE 0 END)
                  /SUM(loan_amount)*100,2) FROM loans) AS gnpa_pct,
    (SELECT ROUND(SUM(invested_amount)/10000000,2) FROM investments WHERE status='Active') AS aum_crore,
    (SELECT COUNT(*) FROM transactions WHERE status='Success') AS total_transactions,
    (SELECT ROUND(SUM(amount)/10000000,2) FROM transactions WHERE status='Success') AS total_volume_crore,
    (SELECT ROUND(SUM(is_fraud)*100.0/COUNT(*),2) FROM transactions) AS fraud_rate_pct,
    (SELECT ROUND(AVG(credit_score),0) FROM customers) AS avg_credit_score,
    (SELECT ROUND(AVG(satisfaction_score),2) FROM tickets WHERE satisfaction_score IS NOT NULL) AS avg_csat;
