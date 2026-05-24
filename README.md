# 🏦 IndiaFirst Bank — Complete Analytics System
### End-to-End Data Analyst Portfolio Project | 
[![SQL](https://img.shields.io/badge/SQL-Advanced-blue)]()
[![Python](https://img.shields.io/badge/Python-Pandas%20%7C%20Matplotlib-green)]()
[![Excel](https://img.shields.io/badge/Excel-7%20Sheet%20Report-darkgreen)]()
[![Dataset](https://img.shields.io/badge/Dataset-50K%20Transactions%20%7C%207%20Tables-red)]()
[![Period](https://img.shields.io/badge/Period-2020--2024-purple)]()

---

## 📌 Project Overview

**IndiaFirst Bank Analytics System** is a full-stack data analytics project simulating
a real Indian bank's analytics infrastructure. It covers everything from raw data generation
to executive dashboards — exactly what interviewers test for Data Analyst roles at banks,
NBFCs, and fintech companies.

**Why this stands out:**
- 7 interconnected tables (not a single flat file)
- 50,000 transactions + real Indian banking context
- Covers SQL → Python → Excel → Power BI → Tableau in one project
- Advanced analytics: RFM, CLV, Fraud Scoring, NPA Analysis, Churn Prediction

---

##  Dataset

| Table | Rows | Description |
|-------|------|-------------|
| `branches` | 50 | Branch locations across 15 states |
| `customers` | 3,000 | Demographics, income, credit score |
| `accounts` | 4,253 | Savings, Current, FD, NRI accounts |
| `transactions` | 50,000 | 5 years of transactions (2020-2024) |
| `loans` | 2,000 | Home, Personal, Car, Education loans |
| `investments` | 1,500 | MF, FD, SIP, PPF, Stocks |
| `tickets` | 5,000 | Customer support tickets |

**Total Loan Book: ₹526 Crore | Fraud Transactions: 449 | NPA Loans: 218**

---

## 📁 Project Structure

```
banking-analytics/
│
├── data/                          # 7 CSV datasets
│   ├── branches.csv
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   ├── loans.csv
│   ├── investments.csv
│   └── tickets.csv
│
├── sql/
│   └── banking_analysis.sql       # 20+ queries: Beginner → Expert
│
├── python/
│   └── analysis.py                # Full analytics + chart + Excel generator
│
├── outputs/
│   ├── bank_dashboard.png         # 8-panel matplotlib dashboard
│   └── IndiaFirst_Bank_Analytics_Report.xlsx  # 7-sheet Excel report
│
├── powerbi/
│   └── POWERBI_TABLEAU_GUIDE.md  # DAX measures + setup guide
│
├── generate_data.py               # Realistic data generator
└── README.md
```

---

## 🎯 Analytics Modules

### 1️⃣ SQL Analytics 
| Level | Queries |
|-------|---------|
| Beginner | Account distribution, State-wise deposits, Channel analysis |
| Intermediate | MoM growth with LAG(), Customer 360, Branch scorecard, NPA analysis |
| Advanced | RFM Segmentation, Fraud scoring model, Churn prediction, CLV, Rolling averages |
| Expert | Zone profitability, Cross-sell matrix, Full P&L view |

### 2️⃣ Python Analysis
- Pandas data manipulation across 7 tables
- Matplotlib 8-panel executive dashboard
- RFM segmentation implementation
- Fraud signal scoring

### 3️⃣ Excel Report (7 Sheets)
-  Executive Summary — KPI cards + monthly trend
- Customer Analytics — Segments + State + RFM
-  Loan Analytics — Book + NPA + Vintage
- Transactions — Channel + Category + Fraud
-  Investments — Risk-Return + Zone
-  Branch Performance — Scorecard + Zone
-  Support Analytics — SLA + CSAT

### 4️⃣ Power BI (5 Dashboard Pages)
- Executive Overview with DAX KPI cards
- Loan & Risk (GNPA gauge, NPA waterfall)
- Customer Analytics (RFM treemap, MAU trend)
- Fraud Detection (hour heatmap, risk table)
- Branch Performance (map + scorecard)

### 5️⃣ Tableau (7 Sheets → 3 Dashboards)
- Monthly volume trend
- State deposit heatmap
- Fraud hour heatmap
- Investment risk-return scatter

---

## 🔑 Key Business Insights

- **GNPA:** Home Loans have lowest NPA (good collateral); Personal Loans highest risk
- **Fraud:** 8%+ fraud rate at 2-3 AM; Mobile Banking + large amounts = high risk
- **Customers:** Premium segment (3%) contributes 40%+ of deposits
- **Channels:** UPI highest volume; Branch highest avg transaction value
- **Investments:** Self-study investors outperform; volatility drives returns
- **Churn:** 180+ day inactive customers with no loans = highest churn risk

---

## 💻 SQL Concepts Used

```
✅ CTEs (multiple levels)           ✅ LAG() / LEAD()
✅ NTILE() — RFM scoring            ✅ PERCENT_RANK()
✅ SUM() OVER (running totals)      ✅ Rolling 30-day average
✅ DATEDIFF for recency             ✅ CASE-based fraud scoring
✅ Multi-table JOINs (7 tables)     ✅ COALESCE / NULLIF
✅ Subqueries in SELECT             ✅ STRING_AGG
✅ Statistical outlier detection    ✅ PIVOT with CASE WHEN
```

---

##  How to Run

```bash
# 1. Install dependencies
pip install duckdb pandas numpy matplotlib openpyxl xlsxwriter scipy

# 2. Generate dataset
python generate_data.py

# 3. Run Python analysis + Excel + Charts
python python/analysis.py

# 4. Run SQL queries (DuckDB — zero setup)
python run_queries.py

# 5. For Power BI / Tableau — import CSVs from data/ folder
# See powerbi/POWERBI_TABLEAU_GUIDE.md for full setup
```

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| SQL (DuckDB/PostgreSQL) | 20+ analytical queries |
| Python (Pandas, Matplotlib) | Data processing + 8-panel dashboard |
| Excel (xlsxwriter) | 7-sheet formatted report |
| Power BI | Interactive dashboards + DAX |
| Tableau | Visual analytics dashboards |
| GitHub | Portfolio hosting |

---

## 👤 Author
**[Mehak pandey ]** —  Data Analyst
pandeymehak.217@gmail.com 

---

