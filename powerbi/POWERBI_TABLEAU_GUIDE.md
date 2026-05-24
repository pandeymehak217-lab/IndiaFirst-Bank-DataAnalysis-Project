# 📊 Power BI & Tableau Setup Guide
## IndiaFirst Bank Analytics Dashboard

---

## POWER BI SETUP

### Step 1 — Import Data
1. Open Power BI Desktop
2. Click **Get Data → Text/CSV**
3. Import all 7 files from the `data/` folder:
   - `branches.csv`
   - `customers.csv`
   - `accounts.csv`
   - `transactions.csv`
   - `loans.csv`
   - `investments.csv`
   - `tickets.csv`

### Step 2 — Build Relationships (Model View)
Go to **Model View** and create these relationships:

```
customers.customer_id  → accounts.customer_id      (1:Many)
customers.customer_id  → transactions.customer_id  (1:Many)
customers.customer_id  → loans.customer_id         (1:Many)
customers.customer_id  → investments.customer_id   (1:Many)
customers.customer_id  → tickets.customer_id       (1:Many)
customers.branch_id    → branches.branch_id        (Many:1)
accounts.account_id    → transactions.account_id   (1:Many)
branches.branch_id     → loans.branch_id           (1:Many)
```

### Step 3 — Key DAX Measures (copy these!)

```dax
// Total Deposits
Total Deposits = CALCULATE(SUM(accounts[current_balance]),
                           accounts[account_status] = "Active")

// Total Loan Book
Loan Book = SUM(loans[loan_amount])

// GNPA %
GNPA % = DIVIDE(
    CALCULATE(SUM(loans[outstanding_amount]),
              loans[loan_status] = "NPA"),
    SUM(loans[loan_amount])
) * 100

// Transaction Success Rate
Success Rate = DIVIDE(
    CALCULATE(COUNT(transactions[txn_id]),
              transactions[status] = "Success"),
    COUNT(transactions[txn_id])
) * 100

// Fraud Rate
Fraud Rate % = DIVIDE(
    SUM(transactions[is_fraud]),
    COUNT(transactions[txn_id])
) * 100

// Monthly Active Users
MAU = CALCULATE(
    DISTINCTCOUNT(transactions[customer_id]),
    transactions[status] = "Success"
)

// MoM Volume Growth
Volume Growth MoM =
VAR CurrentMonth = SUM(transactions[amount])
VAR PrevMonth = CALCULATE(SUM(transactions[amount]),
                DATEADD(transactions[txn_date], -1, MONTH))
RETURN DIVIDE(CurrentMonth - PrevMonth, PrevMonth) * 100

// Customer CLV (simplified)
CLV Score = [Total Deposits] * 0.001 +
            [Loan Book] * 0.025 +
            SUM(investments[invested_amount]) * 0.01

// NPA Recovery Potential
Recovery Potential =
CALCULATE(
    SUM(loans[outstanding_amount]) * 0.7,
    loans[loan_status] = "NPA",
    loans[collateral_type] <> "None"
) +
CALCULATE(
    SUM(loans[outstanding_amount]) * 0.3,
    loans[loan_status] = "NPA",
    loans[collateral_type] = "None"
)
```

### Step 4 — Recommended Visuals

**Page 1: Executive Dashboard**
- Card visuals: Total Deposits, Loan Book, GNPA%, Customers
- Line chart: Monthly Volume Trend (txn_date vs amount)
- Donut: Customer Segment split
- Map: State-wise deposit concentration
- KPI: Success Rate with target = 95%

**Page 2: Loan Analytics**
- Clustered bar: Loan Book by Type
- Gauge: GNPA% (target < 3%)
- Matrix: Loan Status × Loan Type with amounts
- Waterfall: Loan disbursement by year
- Scatter: Credit Score vs Loan Amount

**Page 3: Fraud Detection**
- Line: Fraud Rate by Hour (txn_hour)
- Heatmap: Fraud by Channel × Category
- Table: Top 20 High-Risk Transactions
- Card: Total Fraud Amount flagged

**Page 4: Customer Analytics**
- Treemap: RFM Segments by customer count
- Bar: Occupation vs Avg Credit Score
- Funnel: Customer Acquisition Sources
- Line: MAU trend by month

**Page 5: Branch Performance**
- Map: Branch locations with deposit bubble size
- Bar: Top 10 Branches by Business Volume
- Matrix: Zone × Metric scorecard
- Gauge: Branch target achievement

---

## TABLEAU SETUP

### Step 1 — Connect Data
1. Open Tableau Desktop
2. **Connect → Text File → Select transactions.csv**
3. Go to **Data Source** tab
4. Drag other tables and create relationships

### Step 2 — Key Calculated Fields

```tableau
// Fraud Rate
[is_fraud] / COUNT([txn_id]) * 100

// Transaction Month
DATETRUNC('month', [txn_date])

// Customer Tier
IF [monthly_income] > 100000 THEN "Premium"
ELSEIF [monthly_income] > 50000 THEN "Gold"
ELSEIF [monthly_income] > 20000 THEN "Silver"
ELSE "Basic" END

// Days Inactive
DATEDIFF('day', [last_txn_date], TODAY())

// GNPA Flag
IF [loan_status] = "NPA" THEN [outstanding_amount] ELSE 0 END
```

### Step 3 — Recommended Tableau Sheets
1. **Monthly Volume Trend** — Line chart
2. **State Heatmap** — Filled map of deposits
3. **Fraud Hour Heatmap** — Hour × Day heatmap
4. **Loan Type Bubble Chart** — Size=Book, Color=NPA%
5. **Customer RFM Scatter** — Frequency vs Monetary, Color=Recency
6. **Branch Performance** — Bar race / sorted bar
7. **Investment Risk-Return** — Scatter plot

### Step 4 — Dashboard Assembly
Combine sheets into 3 dashboards:
- 🏦 Executive Overview
- 💰 Loan & Risk
- 👥 Customer Insights

---

## EXCEL DASHBOARD TIPS

The Excel file `IndiaFirst_Bank_Analytics_Report.xlsx` has 7 sheets.

**To add Pivot Charts:**
1. Select any data table
2. Insert → PivotChart
3. Place on a new "Dashboard" sheet

**Recommended Slicers:**
- Year slicer (2020-2024)
- State slicer
- Customer Segment slicer
- Loan Type slicer

**Conditional Formatting applied to:**
- GNPA% — Red if > 5%
- Success Rate — Green if > 90%
- Fraud Rate — Red gradient

---

## SCREENSHOT YOUR DASHBOARDS!

Once built, take screenshots and add them to:
1. Your GitHub README
2. Your LinkedIn post
3. Your resume projects section

This project demonstrates:
✅ SQL (7 tables, 50K records, window functions)
✅ Python (pandas, matplotlib, xlsxwriter)
✅ Excel (multi-sheet, formatted reports)
✅ Power BI (DAX, relationships, 5 pages)
✅ Tableau (calculated fields, dashboards)
