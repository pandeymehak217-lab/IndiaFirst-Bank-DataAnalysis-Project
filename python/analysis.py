"""
IndiaFirst Bank — Python Analytics + Excel Dashboard Generator
Produces a multi-sheet Excel report ready to show recruiters
"""
import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

BASE   = '/Users/mehekpandey/banking_project/data'
OUT    = '/Users/mehekpandey/banking_project/outputs'

# ── Load data ────────────────────────────────────────────────
con = duckdb.connect()
for tbl in ['branches','customers','accounts','transactions','loans','investments','tickets']:
    con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{BASE}/{tbl}.csv')")
print(" All 7 tables loaded")

def q(sql): return con.execute(sql).df()

# ════════════════════════════════════════════════════════════════
# ANALYSIS QUERIES
# ════════════════════════════════════════════════════════════════

kpis = q("""
    SELECT
        (SELECT COUNT(*) FROM customers) AS total_customers,
        (SELECT COUNT(*) FROM accounts WHERE account_status='Active') AS active_accounts,
        (SELECT ROUND(SUM(current_balance)/10000000,2) FROM accounts WHERE account_status='Active') AS deposits_crore,
        (SELECT ROUND(SUM(loan_amount)/10000000,2) FROM loans) AS loan_book_crore,
        (SELECT ROUND(SUM(CASE WHEN loan_status='NPA' THEN outstanding_amount ELSE 0 END)/SUM(loan_amount)*100,2) FROM loans) AS gnpa_pct,
        (SELECT COUNT(*) FROM transactions WHERE status='Success') AS total_txns,
        (SELECT ROUND(SUM(amount)/10000000,2) FROM transactions WHERE status='Success') AS volume_crore,
        (SELECT ROUND(SUM(is_fraud)*100.0/COUNT(*),2) FROM transactions) AS fraud_rate,
        (SELECT ROUND(AVG(credit_score),0) FROM customers) AS avg_credit_score,
        (SELECT ROUND(AVG(satisfaction_score),2) FROM tickets WHERE satisfaction_score IS NOT NULL) AS csat
""")

monthly_trend = q("""
    SELECT txn_month, txn_year,
           COUNT(*) AS txn_count,
           ROUND(SUM(amount)/10000000,2) AS volume_crore,
           COUNT(DISTINCT customer_id) AS active_customers,
           SUM(is_fraud) AS fraud_count
    FROM transactions WHERE status='Success'
    GROUP BY txn_month, txn_year ORDER BY txn_month
""")

segment_analysis = q("""
    SELECT customer_segment,
           COUNT(*) AS customers,
           ROUND(AVG(monthly_income),0) AS avg_income,
           ROUND(AVG(credit_score),0) AS avg_credit_score,
           COUNT(*)*100.0/(SELECT COUNT(*) FROM customers) AS pct
    FROM customers GROUP BY customer_segment ORDER BY avg_income DESC
""")

loan_analysis = q("""
    SELECT loan_type,
           COUNT(*) AS count,
           ROUND(SUM(loan_amount)/10000000,2) AS book_crore,
           ROUND(AVG(interest_rate),2) AS avg_rate,
           SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END) AS npa_count,
           ROUND(SUM(CASE WHEN loan_status='NPA' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS npa_pct
    FROM loans GROUP BY loan_type ORDER BY book_crore DESC
""")

channel_analysis = q("""
    SELECT channel, COUNT(*) AS txns,
           ROUND(SUM(amount)/10000000,2) AS volume_crore,
           ROUND(SUM(CASE WHEN status='Success' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS success_rate
    FROM transactions GROUP BY channel ORDER BY txns DESC
""")

fraud_by_hour = q("""
    SELECT txn_hour,
           COUNT(*) AS total,
           SUM(is_fraud) AS frauds,
           ROUND(SUM(is_fraud)*100.0/COUNT(*),2) AS fraud_rate
    FROM transactions GROUP BY txn_hour ORDER BY txn_hour
""")

state_performance = q("""
    SELECT c.state,
           COUNT(DISTINCT c.customer_id) AS customers,
           ROUND(SUM(a.current_balance)/10000000,2) AS deposits_crore,
           COUNT(DISTINCT l.loan_id) AS loans,
           ROUND(AVG(c.credit_score),0) AS avg_credit_score
    FROM customers c
    LEFT JOIN accounts a ON c.customer_id=a.customer_id AND a.account_status='Active'
    LEFT JOIN loans l ON c.customer_id=l.customer_id
    GROUP BY c.state ORDER BY deposits_crore DESC
""")

investment_analysis = q("""
    SELECT investment_type, risk_category,
           COUNT(*) AS investors,
           ROUND(SUM(invested_amount)/10000000,2) AS invested_crore,
           ROUND(AVG(returns_pct),2) AS avg_return_pct,
           ROUND(STDDEV(returns_pct),2) AS volatility
    FROM investments GROUP BY investment_type, risk_category
    ORDER BY avg_return_pct DESC
""")

rfm_segments = q("""
    WITH rfm AS (
        SELECT customer_id,
               DATEDIFF('day', MAX(CAST(txn_date AS DATE)), CAST('2024-12-31' AS DATE)) AS recency,
               COUNT(*) AS frequency,
               SUM(amount) AS monetary,
               NTILE(5) OVER (ORDER BY MAX(txn_date) DESC) AS r,
               NTILE(5) OVER (ORDER BY COUNT(*))            AS f,
               NTILE(5) OVER (ORDER BY SUM(amount))         AS m
        FROM transactions WHERE status='Success' AND txn_type='Debit'
        GROUP BY customer_id
    )
    SELECT CASE WHEN r>=4 AND f>=4 AND m>=4 THEN 'Champions'
                WHEN r>=3 AND f>=3          THEN 'Loyal'
                WHEN r>=4 AND f<=2          THEN 'Potential Loyalist'
                WHEN r<=2 AND f>=3          THEN 'At Risk'
                WHEN r<=1 AND f<=1          THEN 'Lost'
                ELSE 'Needs Attention' END AS segment,
           COUNT(*) AS customers,
           ROUND(AVG(monetary),0) AS avg_spend
    FROM rfm GROUP BY 1 ORDER BY customers DESC
""")

zone_performance = q("""
    SELECT b.zone,
           COUNT(DISTINCT c.customer_id) AS customers,
           ROUND(SUM(a.current_balance)/10000000,2) AS deposits_crore,
           ROUND(SUM(l.loan_amount)/10000000,2) AS loans_crore
    FROM branches b
    JOIN customers c ON b.branch_id=c.branch_id
    LEFT JOIN accounts a ON c.customer_id=a.customer_id AND a.account_status='Active'
    LEFT JOIN loans l ON b.branch_id=l.branch_id
    GROUP BY b.zone ORDER BY deposits_crore DESC
""")

print(" All analysis queries done")

# ════════════════════════════════════════════════════════════════
# MATPLOTLIB CHARTS
# ════════════════════════════════════════════════════════════════

COLORS = ['#1565C0','#00695C','#E65100','#6A1B9A','#B71C1C','#F57F17','#1B5E20','#880E4F']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})

fig = plt.figure(figsize=(22, 28))
fig.patch.set_facecolor('#F8F9FA')
gs  = GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

# ── KPI Banner ──
ax_kpi = fig.add_subplot(gs[0, :])
ax_kpi.set_facecolor('#1565C0')
ax_kpi.set_xlim(0,10); ax_kpi.set_ylim(0,1)
ax_kpi.axis('off')
kpi_items = [
    (f"₹{kpis['deposits_crore'].iloc[0]:,.1f}Cr", "Total Deposits"),
    (f"₹{kpis['loan_book_crore'].iloc[0]:,.1f}Cr","Loan Book"),
    (f"{kpis['gnpa_pct'].iloc[0]}%",               "GNPA %"),
    (f"{kpis['total_customers'].iloc[0]:,}",        "Customers"),
    (f"{kpis['total_txns'].iloc[0]:,}",             "Transactions"),
    (f"₹{kpis['volume_crore'].iloc[0]:,.1f}Cr",    "Txn Volume"),
    (f"{kpis['fraud_rate'].iloc[0]}%",              "Fraud Rate"),
    (f"{kpis['csat'].iloc[0]}/5",                   "CSAT Score"),
]
ax_kpi.text(5, 0.88, 'IndiaFirst Bank — Executive Dashboard 2020-2024',
            ha='center', va='center', fontsize=16, fontweight='bold', color='white')
for idx,(val,lbl) in enumerate(kpi_items):
    x = 0.6 + idx*1.27
    ax_kpi.text(x, 0.55, val, ha='center', va='center',
                fontsize=13, fontweight='bold', color='#FFD54F')
    ax_kpi.text(x, 0.22, lbl, ha='center', va='center',
                fontsize=8,  color='#B3E5FC')

# ── Monthly Volume Trend ──
ax1 = fig.add_subplot(gs[1, :2])
ax1.set_facecolor('white')
months = monthly_trend['txn_month'].astype(str)
ax1.bar(range(len(months)), monthly_trend['volume_crore'],
        color=COLORS[0], alpha=0.7, label='Volume (Cr)')
ax1_twin = ax1.twinx()
ax1_twin.plot(range(len(months)), monthly_trend['active_customers'],
              color=COLORS[2], linewidth=2, marker='o', markersize=3, label='Active Customers')
ax1.set_title('Monthly Transaction Volume & Active Customers', fontweight='bold', pad=8)
ax1.set_ylabel('Volume (₹ Crore)', color=COLORS[0])
ax1_twin.set_ylabel('Active Customers', color=COLORS[2])
ax1.set_xticks(range(0,len(months),6))
ax1.set_xticklabels([months.iloc[i] for i in range(0,len(months),6)], rotation=45, fontsize=7)
ax1.set_facecolor('#FAFAFA')

# ── RFM Segments ──
ax2 = fig.add_subplot(gs[1, 2])
ax2.set_facecolor('white')
wedge_colors = [COLORS[i%len(COLORS)] for i in range(len(rfm_segments))]
wedges, texts, autotexts = ax2.pie(
    rfm_segments['customers'], labels=rfm_segments['segment'],
    autopct='%1.1f%%', colors=wedge_colors,
    pctdistance=0.75, textprops={'fontsize':7})
ax2.set_title('RFM Customer Segments', fontweight='bold', pad=8)

# ── Loan Book by Type ──
ax3 = fig.add_subplot(gs[2, 0])
ax3.set_facecolor('#FAFAFA')
bars = ax3.barh(loan_analysis['loan_type'], loan_analysis['book_crore'],
                color=COLORS[:len(loan_analysis)])
ax3.set_title('Loan Book by Type (₹ Crore)', fontweight='bold', pad=8)
ax3.set_xlabel('₹ Crore')
for bar, npa in zip(bars, loan_analysis['npa_pct']):
    ax3.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
             f'NPA:{npa}%', va='center', fontsize=7, color='red')

# ── Channel Performance ──
ax4 = fig.add_subplot(gs[2, 1])
ax4.set_facecolor('#FAFAFA')
x = range(len(channel_analysis))
bars1 = ax4.bar(x, channel_analysis['volume_crore'],
                color=COLORS[0], alpha=0.8, label='Volume(Cr)')
ax4_twin = ax4.twinx()
ax4_twin.plot(x, channel_analysis['success_rate'],
              color=COLORS[1], marker='D', linewidth=2, markersize=5, label='Success%')
ax4.set_xticks(x)
ax4.set_xticklabels(channel_analysis['channel'], rotation=35, ha='right', fontsize=7)
ax4.set_title('Channel: Volume vs Success Rate', fontweight='bold', pad=8)
ax4.set_ylabel('₹ Crore', color=COLORS[0])
ax4_twin.set_ylabel('Success Rate %', color=COLORS[1])

# ── Fraud by Hour ──
ax5 = fig.add_subplot(gs[2, 2])
ax5.set_facecolor('#FAFAFA')
hour_colors = ['#B71C1C' if r>6 else '#1565C0' for r in fraud_by_hour['fraud_rate']]
ax5.bar(fraud_by_hour['txn_hour'], fraud_by_hour['fraud_rate'], color=hour_colors)
ax5.axhline(y=fraud_by_hour['fraud_rate'].mean(), color='orange',
            linestyle='--', linewidth=1.5, label='Avg')
ax5.set_title('Fraud Rate by Hour of Day', fontweight='bold', pad=8)
ax5.set_xlabel('Hour')
ax5.set_ylabel('Fraud Rate %')
ax5.legend(fontsize=7)
red_patch = mpatches.Patch(color='#B71C1C', label='High Risk')
blue_patch = mpatches.Patch(color='#1565C0', label='Normal')
ax5.legend(handles=[red_patch, blue_patch], fontsize=7)

# ── Investment Risk-Return ──
ax6 = fig.add_subplot(gs[3, 0])
ax6.set_facecolor('#FAFAFA')
risk_colors = {'High':'#B71C1C','Medium':'#E65100','Low':'#1B5E20'}
for _, row in investment_analysis.iterrows():
    color = risk_colors.get(row['risk_category'],'gray')
    ax6.scatter(row['volatility'], row['avg_return_pct'],
                s=row['invested_crore']*20, color=color, alpha=0.7, edgecolors='white')
    ax6.annotate(row['investment_type'], (row['volatility'], row['avg_return_pct']),
                 fontsize=6.5, ha='center', va='bottom')
ax6.set_xlabel('Volatility (Std Dev of Returns %)')
ax6.set_ylabel('Avg Return %')
ax6.set_title('Investment Risk vs Return (Bubble=AUM)', fontweight='bold', pad=8)
patches = [mpatches.Patch(color=v,label=k) for k,v in risk_colors.items()]
ax6.legend(handles=patches, fontsize=7)

# ── Customer Segment Bar ──
ax7 = fig.add_subplot(gs[3, 1])
ax7.set_facecolor('#FAFAFA')
seg_colors = ['#1565C0','#00695C','#E65100','#6A1B9A']
bars = ax7.bar(segment_analysis['customer_segment'],
               segment_analysis['customers'], color=seg_colors)
ax7_twin = ax7.twinx()
ax7_twin.plot(segment_analysis['customer_segment'],
              segment_analysis['avg_income']/1000,
              color='#E65100', marker='o', linewidth=2, markersize=6)
ax7.set_title('Customer Segments', fontweight='bold', pad=8)
ax7.set_ylabel('Customer Count')
ax7_twin.set_ylabel('Avg Income (₹K)', color='#E65100')
for bar in bars:
    ax7.text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
             f'{int(bar.get_height()):,}', ha='center', fontsize=7)

# ── Zone Performance ──
ax8 = fig.add_subplot(gs[3, 2])
ax8.set_facecolor('#FAFAFA')
x = range(len(zone_performance))
w = 0.35
ax8.bar([i-w/2 for i in x], zone_performance['deposits_crore'],
        w, label='Deposits', color=COLORS[0], alpha=0.8)
ax8.bar([i+w/2 for i in x], zone_performance['loans_crore'],
        w, label='Loans', color=COLORS[2], alpha=0.8)
ax8.set_xticks(x)
ax8.set_xticklabels(zone_performance['zone'], fontsize=7, rotation=15)
ax8.set_title('Zone: Deposits vs Loans (₹ Crore)', fontweight='bold', pad=8)
ax8.set_ylabel('₹ Crore')
ax8.legend(fontsize=7)

plt.suptitle('IndiaFirst Bank — Complete Analytics Dashboard',
             fontsize=18, fontweight='bold', y=0.98, color='#1565C0')

chart_path = f'{OUT}/bank_dashboard.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='#F8F9FA')
plt.close()
print(f" Dashboard chart saved")

# ════════════════════════════════════════════════════════════════
# EXCEL MULTI-SHEET REPORT
# ════════════════════════════════════════════════════════════════

excel_path = f'{OUT}/IndiaFirst_Bank_Analytics_Report.xlsx'
writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
wb = writer.book

# Formats
fmt_title  = wb.add_format({'bold':True,'font_size':14,'font_color':'#FFFFFF',
                             'bg_color':'#1565C0','align':'center','valign':'vcenter'})
fmt_header = wb.add_format({'bold':True,'font_color':'#FFFFFF','bg_color':'#1565C0',
                             'border':1,'align':'center'})
fmt_kpi    = wb.add_format({'bold':True,'font_size':16,'font_color':'#1565C0',
                             'align':'center','valign':'vcenter','border':2,
                             'bg_color':'#E3F2FD'})
fmt_kpi_lbl= wb.add_format({'font_size':9,'font_color':'#757575',
                             'align':'center','bg_color':'#F5F5F5'})
fmt_num    = wb.add_format({'num_format':'#,##0','border':1})
fmt_pct    = wb.add_format({'num_format':'0.00%','border':1})
fmt_money  = wb.add_format({'num_format':'₹#,##0','border':1,'font_color':'#1B5E20'})
fmt_alt1   = wb.add_format({'bg_color':'#E3F2FD','border':1})
fmt_alt2   = wb.add_format({'bg_color':'#FFFFFF','border':1})
fmt_red    = wb.add_format({'font_color':'#B71C1C','bold':True,'border':1,'bg_color':'#FFEBEE'})
fmt_green  = wb.add_format({'font_color':'#1B5E20','bold':True,'border':1,'bg_color':'#E8F5E9'})

def write_df(ws, df, row_start=1, fmt_header=fmt_header, alt1=fmt_alt1, alt2=fmt_alt2):
    for col_num, col_name in enumerate(df.columns):
        ws.write(row_start, col_num, col_name, fmt_header)
    for row_num, row in enumerate(df.itertuples(index=False), row_start+1):
        fmt = alt1 if row_num % 2 == 0 else alt2
        for col_num, val in enumerate(row):
            ws.write(row_num, col_num, val, fmt)

# ── SHEET 1: Executive Summary ──
ws1 = wb.add_worksheet('Executive Summary')
ws1.set_tab_color('#1565C0')
ws1.merge_range('A1:J2', 'IndiaFirst Bank — Executive KPI Dashboard 2020–2024', fmt_title)
ws1.set_row(0, 30); ws1.set_row(1, 30)

kpi_data = [
    ('₹'+str(kpis['deposits_crore'].iloc[0])+'Cr', 'Total Deposits'),
    ('₹'+str(kpis['loan_book_crore'].iloc[0])+'Cr', 'Loan Book'),
    (str(kpis['gnpa_pct'].iloc[0])+'%', 'GNPA %'),
    (str(int(kpis['total_customers'].iloc[0])), 'Total Customers'),
    (str(int(kpis['active_accounts'].iloc[0])), 'Active Accounts'),
    (str(int(kpis['total_txns'].iloc[0])), 'Transactions'),
    ('₹'+str(kpis['volume_crore'].iloc[0])+'Cr', 'Txn Volume'),
    (str(kpis['fraud_rate'].iloc[0])+'%', 'Fraud Rate'),
    (str(kpis['avg_credit_score'].iloc[0]), 'Avg Credit Score'),
    (str(kpis['csat'].iloc[0])+'/5', 'CSAT Score'),
]
for i,(val,lbl) in enumerate(kpi_data):
    col = i % 5
    row = 3 if i < 5 else 6
    ws1.merge_range(row, col*2, row, col*2+1, val, fmt_kpi)
    ws1.merge_range(row+1, col*2, row+1, col*2+1, lbl, fmt_kpi_lbl)
    ws1.set_row(row, 35)

ws1.merge_range('A10:J10', 'Monthly Business Trend', fmt_title)
write_df(ws1, monthly_trend, row_start=10)
for i in range(len(monthly_trend.columns)):
    ws1.set_column(i, i, 16)
ws1.insert_image('A30', chart_path, {'x_scale':0.65,'y_scale':0.65})

# ── SHEET 2: Customer Analytics ──
ws2 = wb.add_worksheet('👥 Customer Analytics')
ws2.set_tab_color('#00695C')
ws2.merge_range('A1:F1', 'Customer Segmentation Analysis', fmt_title)
write_df(ws2, segment_analysis, row_start=1)

ws2.merge_range('A8:F8', 'State-wise Performance', fmt_title)
write_df(ws2, state_performance, row_start=8)

ws2.merge_range('A27:F27', 'RFM Segmentation', fmt_title)
write_df(ws2, rfm_segments, row_start=27)
for i in range(6): ws2.set_column(i, i, 20)

# ── SHEET 3: Loan Analytics ──
ws3 = wb.add_worksheet('Loan Analytics')
ws3.set_tab_color('#E65100')
ws3.merge_range('A1:G1', 'Loan Book Analysis', fmt_title)
write_df(ws3, loan_analysis, row_start=1)

npa_data = q("""
    SELECT loan_type, loan_status, COUNT(*) AS count,
           ROUND(SUM(outstanding_amount)/10000000,2) AS npa_crore,
           ROUND(AVG(days_past_due),0) AS avg_dpd
    FROM loans WHERE loan_status IN ('NPA','Special Mention')
    GROUP BY loan_type, loan_status ORDER BY npa_crore DESC
""")
ws3.merge_range('A12:G12', 'NPA / Special Mention Accounts', fmt_title)
write_df(ws3, npa_data, row_start=12)

loan_vintage = q("""
    SELECT EXTRACT(YEAR FROM CAST(disbursement_date AS DATE)) AS year,
           loan_type, COUNT(*) AS loans,
           ROUND(SUM(loan_amount)/10000000,2) AS disbursed_crore,
           ROUND(AVG(interest_rate),2) AS avg_rate
    FROM loans GROUP BY 1,2 ORDER BY 1,2
""")
ws3.merge_range('A25:G25', 'Vintage Analysis (Year-wise Disbursement)', fmt_title)
write_df(ws3, loan_vintage, row_start=25)
for i in range(7): ws3.set_column(i, i, 20)

# ── SHEET 4: Transaction Analytics ──
ws4 = wb.add_worksheet('Transactions')
ws4.set_tab_color('#6A1B9A')
ws4.merge_range('A1:G1', 'Transaction Channel Analysis', fmt_title)
write_df(ws4, channel_analysis, row_start=1)

category_txns = q("""
    SELECT category, txn_type,
           COUNT(*) AS txns,
           ROUND(SUM(amount)/10000000,2) AS volume_crore,
           ROUND(AVG(amount),0) AS avg_amount
    FROM transactions WHERE status='Success'
    GROUP BY category, txn_type ORDER BY volume_crore DESC LIMIT 25
""")
ws4.merge_range('A12:G12', 'Category-wise Transaction Analysis', fmt_title)
write_df(ws4, category_txns, row_start=12)

ws4.merge_range('A40:G40', 'Fraud by Hour Analysis', fmt_title)
write_df(ws4, fraud_by_hour, row_start=40)
for i in range(7): ws4.set_column(i, i, 18)

# ── SHEET 5: Investment Analytics ──
ws5 = wb.add_worksheet(' Investments')
ws5.set_tab_color('#1B5E20')
ws5.merge_range('A1:G1', 'Investment Portfolio Analysis', fmt_title)
write_df(ws5, investment_analysis, row_start=1)

zone_inv = q("""
    SELECT b.zone, i.investment_type, i.risk_category,
           COUNT(*) AS investors,
           ROUND(SUM(i.invested_amount)/10000000,2) AS invested_crore,
           ROUND(AVG(i.returns_pct),2) AS avg_return
    FROM investments i
    JOIN customers c ON i.customer_id=c.customer_id
    JOIN branches b ON c.branch_id=b.branch_id
    GROUP BY b.zone, i.investment_type, i.risk_category
    ORDER BY invested_crore DESC LIMIT 25
""")
ws5.merge_range('A12:G12', 'Zone-wise Investment Distribution', fmt_title)
write_df(ws5, zone_inv, row_start=12)
for i in range(7): ws5.set_column(i, i, 20)

# ── SHEET 6: Branch Performance ──
ws6 = wb.add_worksheet(' Branch Performance')
ws6.set_tab_color('#880E4F')
branch_perf = q("""
    SELECT b.branch_id, b.branch_name, b.city, b.state, b.zone, b.branch_type,
           COUNT(DISTINCT c.customer_id) AS customers,
           ROUND(SUM(a.current_balance)/10000000,2) AS deposits_crore,
           COUNT(DISTINCT l.loan_id) AS loans,
           ROUND(SUM(l.loan_amount)/10000000,2) AS loan_book_crore,
           ROUND(SUM(CASE WHEN l.loan_status='NPA' THEN l.loan_amount ELSE 0 END)
                 /NULLIF(SUM(l.loan_amount),0)*100,2) AS gnpa_pct
    FROM branches b
    LEFT JOIN customers c ON b.branch_id=c.branch_id
    LEFT JOIN accounts a ON c.customer_id=a.customer_id AND a.account_status='Active'
    LEFT JOIN loans l ON b.branch_id=l.branch_id
    GROUP BY b.branch_id, b.branch_name, b.city, b.state, b.zone, b.branch_type
    ORDER BY deposits_crore DESC
""")
ws6.merge_range('A1:K1', 'Branch Performance Scorecard', fmt_title)
write_df(ws6, branch_perf, row_start=1)

ws6.merge_range('A55:K55', 'Zone Performance Summary', fmt_title)
write_df(ws6, zone_performance, row_start=55)
for i in range(11): ws6.set_column(i, i, 18)

# ── SHEET 7: Support Analytics ──
ws7 = wb.add_worksheet('Support Analytics')
ws7.set_tab_color('#F57F17')
ticket_summary = q("""
    SELECT category, priority,
           COUNT(*) AS tickets,
           COUNT(CASE WHEN status='Resolved' THEN 1 END) AS resolved,
           ROUND(COUNT(CASE WHEN status='Resolved' THEN 1 END)*100.0/COUNT(*),1) AS resolution_rate,
           ROUND(AVG(CASE WHEN status='Resolved' THEN resolution_hours END),1) AS avg_hrs,
           ROUND(AVG(satisfaction_score),2) AS avg_csat
    FROM tickets GROUP BY category, priority ORDER BY priority, tickets DESC
""")
ws7.merge_range('A1:G1', 'Customer Support Analytics', fmt_title)
write_df(ws7, ticket_summary, row_start=1)
for i in range(7): ws7.set_column(i, i, 20)

writer.close()
print(f" Excel report saved: {excel_path}")

con.close()
print("\nALL OUTPUTS COMPLETE!")
print(f"    Dashboard chart : {OUT}/bank_dashboard.png")
print(f"    Excel Report    : {OUT}/IndiaFirst_Bank_Analytics_Report.xlsx")
