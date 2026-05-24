"""
IndiaFirst Bank Analytics — Unique Dataset Generator
7 interconnected tables | 2020-2024 | Real Indian banking context
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, date

random.seed(42)
np.random.seed(42)

BASE = '/Users/mehekpandey/banking_project/data'

# ── Reference Data ────────────────────────────────────────────
STATES = ['Maharashtra','Karnataka','Delhi','Tamil Nadu','Telangana',
          'Gujarat','Rajasthan','West Bengal','Uttar Pradesh','Kerala',
          'Punjab','Haryana','Madhya Pradesh','Bihar','Andhra Pradesh']

CITIES = {
    'Maharashtra':['Mumbai','Pune','Nagpur','Thane','Nashik'],
    'Karnataka':['Bengaluru','Mysuru','Hubli','Mangaluru','Belgaum'],
    'Delhi':['New Delhi','Dwarka','Noida','Gurgaon','Faridabad'],
    'Tamil Nadu':['Chennai','Coimbatore','Madurai','Salem','Trichy'],
    'Telangana':['Hyderabad','Warangal','Karimnagar','Nizamabad','Khammam'],
    'Gujarat':['Ahmedabad','Surat','Vadodara','Rajkot','Gandhinagar'],
    'Rajasthan':['Jaipur','Jodhpur','Udaipur','Kota','Ajmer'],
    'West Bengal':['Kolkata','Howrah','Durgapur','Siliguri','Asansol'],
    'Uttar Pradesh':['Lucknow','Kanpur','Agra','Varanasi','Allahabad'],
    'Kerala':['Kochi','Thiruvananthapuram','Kozhikode','Thrissur','Kollam'],
    'Punjab':['Chandigarh','Ludhiana','Amritsar','Jalandhar','Patiala'],
    'Haryana':['Gurugram','Faridabad','Hisar','Rohtak','Panipat'],
    'Madhya Pradesh':['Bhopal','Indore','Gwalior','Jabalpur','Ujjain'],
    'Bihar':['Patna','Gaya','Muzaffarpur','Bhagalpur','Darbhanga'],
    'Andhra Pradesh':['Vijayawada','Visakhapatnam','Guntur','Tirupati','Nellore'],
}

OCCUPATIONS = ['Salaried','Self-Employed','Business Owner','Student',
               'Retired','Homemaker','Freelancer','Government Employee']
OCC_WEIGHTS  = [35,20,15,10,8,5,4,3]

BANKS = ['IndiaFirst Bank']  # Our bank

ACCOUNT_TYPES = ['Savings','Current','Salary','Fixed Deposit','NRI']
ACC_WEIGHTS    = [45,20,15,15,5]

LOAN_TYPES = ['Home Loan','Personal Loan','Car Loan','Education Loan',
              'Business Loan','Gold Loan','Credit Card Loan']

TRANSACTION_CHANNELS = ['Mobile Banking','Net Banking','ATM','Branch','UPI','NEFT','RTGS','IMPS']

TRANSACTION_CATEGORIES = [
    'Salary Credit','EMI Debit','Utility Bills','Shopping','Food & Dining',
    'Travel','Entertainment','Medical','Education','Insurance Premium',
    'Investment','Rent','Cash Withdrawal','Cash Deposit','Fund Transfer',
    'Interest Credit','Dividend','Tax Payment','Government Services','Refund'
]

INVESTMENT_TYPES = ['Mutual Fund','Fixed Deposit','Recurring Deposit',
                    'SIP','PPF','NPS','Stocks','Gold Bond']

BRANCH_ZONES = ['North Zone','South Zone','East Zone','West Zone','Central Zone']

first_names = ['Aarav','Aditi','Aditya','Akash','Ananya','Anjali','Arjun','Deepika',
               'Divya','Ishaan','Isha','Karan','Kavya','Meera','Mihir','Nisha',
               'Priya','Rahul','Riya','Rohit','Sanjay','Shreya','Siddharth','Sneha',
               'Tanvi','Utkarsh','Varun','Vikram','Yash','Zara','Amit','Pooja',
               'Rajesh','Sunita','Manoj','Deepak','Suresh','Rekha','Vijay','Rina',
               'Ajay','Neha','Sunil','Anita','Ravi','Seema','Anil','Monika','Sachin','Priyanka']

last_names = ['Sharma','Patel','Singh','Gupta','Kumar','Verma','Joshi','Nair',
              'Reddy','Mehta','Shah','Iyer','Pillai','Rao','Malhotra','Agarwal',
              'Banerjee','Chatterjee','Mishra','Pandey','Trivedi','Desai','Kapoor',
              'Saxena','Tiwari','Yadav','Bose','Das','Menon','Krishnan']

def rand_date(start_str, end_str):
    s = datetime.strptime(start_str, '%Y-%m-%d')
    e = datetime.strptime(end_str,   '%Y-%m-%d')
    return s + timedelta(seconds=random.randint(0, int((e-s).total_seconds())))

# ════════════════════════════════════════════════════════════════
# TABLE 1: BRANCHES (50 branches across India)
# ════════════════════════════════════════════════════════════════
branches = []
bid = 1
for state in STATES:
    n = random.randint(2, 5)
    for _ in range(n):
        city = random.choice(CITIES[state])
        zone = {'Maharashtra':'West Zone','Karnataka':'South Zone',
                'Tamil Nadu':'South Zone','Telangana':'South Zone',
                'Andhra Pradesh':'South Zone','Delhi':'North Zone',
                'Uttar Pradesh':'North Zone','Punjab':'North Zone',
                'Haryana':'North Zone','Rajasthan':'North Zone',
                'West Bengal':'East Zone','Bihar':'East Zone',
                'Gujarat':'West Zone','Madhya Pradesh':'Central Zone',
                'Kerala':'South Zone'}.get(state,'Central Zone')
        branches.append({
            'branch_id':     f'BR{bid:03d}',
            'branch_name':   f'{city} {random.choice(["Main","Central","North","South","East","West"])} Branch',
            'city':          city,
            'state':         state,
            'zone':          zone,
            'branch_type':   random.choices(['Urban','Semi-Urban','Rural'],weights=[60,30,10])[0],
            'established_year': random.randint(2005,2020),
            'manager_name':  f'{random.choice(first_names)} {random.choice(last_names)}',
            'atm_count':     random.randint(1,5),
            'staff_count':   random.randint(8,45),
        })
        bid += 1
branches_df = pd.DataFrame(branches[:50])

# ════════════════════════════════════════════════════════════════
# TABLE 2: CUSTOMERS (3000 customers)
# ════════════════════════════════════════════════════════════════
N_CUSTOMERS = 3000
customers = []
for cid in range(1, N_CUSTOMERS+1):
    state  = random.choice(STATES)
    city   = random.choice(CITIES[state])
    branch = random.choice(branches_df['branch_id'].tolist())
    occ    = random.choices(OCCUPATIONS, weights=OCC_WEIGHTS)[0]
    age    = random.randint(18, 70)

    # Income based on occupation & age
    income_map = {
        'Salaried':          (25000, 200000),
        'Self-Employed':     (15000, 300000),
        'Business Owner':    (50000, 1000000),
        'Student':           (0,     10000),
        'Retired':           (15000, 80000),
        'Homemaker':         (0,     5000),
        'Freelancer':        (20000, 150000),
        'Government Employee':(30000,120000),
    }
    lo, hi = income_map[occ]
    monthly_income = round(random.uniform(lo, hi), 0)

    credit_score = min(900, max(300, int(np.random.normal(
        680 + (monthly_income/10000)*2, 60))))

    reg_date = rand_date('2015-01-01', '2023-12-31')

    customers.append({
        'customer_id':       f'CUST{cid:05d}',
        'customer_name':     f'{random.choice(first_names)} {random.choice(last_names)}',
        'age':               age,
        'gender':            random.choices(['M','F','Other'],weights=[52,47,1])[0],
        'occupation':        occ,
        'state':             state,
        'city':              city,
        'branch_id':         branch,
        'monthly_income':    monthly_income,
        'credit_score':      credit_score,
        'kyc_status':        random.choices(['Verified','Pending','Expired'],weights=[85,10,5])[0],
        'registration_date': reg_date.strftime('%Y-%m-%d'),
        'customer_segment':  ('Premium' if monthly_income>100000 else
                              'Gold'    if monthly_income>50000  else
                              'Silver'  if monthly_income>20000  else 'Basic'),
        'is_nri':            random.choices([0,1],weights=[95,5])[0],
        'referral_source':   random.choices(
            ['Branch Walk-in','Online','Referral','Agent','Camp'],
            weights=[30,35,20,10,5])[0],
    })
customers_df = pd.DataFrame(customers)

# ════════════════════════════════════════════════════════════════
# TABLE 3: ACCOUNTS (4500 accounts — some customers have multiple)
# ════════════════════════════════════════════════════════════════
accounts = []
aid = 1
for _, cust in customers_df.iterrows():
    n_accounts = random.choices([1,2,3],weights=[65,28,7])[0]
    used_types = []
    for _ in range(n_accounts):
        remaining = [t for t in ACCOUNT_TYPES if t not in used_types]
        if not remaining:
            break
        acc_type = random.choices(remaining,
            weights=[w for t,w in zip(ACCOUNT_TYPES,ACC_WEIGHTS) if t in remaining][:len(remaining)])[0]
        used_types.append(acc_type)

        open_date = rand_date(cust['registration_date'], '2024-01-01')

        balance_map = {
            'Savings':        (1000,   500000),
            'Current':        (10000,  5000000),
            'Salary':         (5000,   300000),
            'Fixed Deposit':  (50000,  10000000),
            'NRI':            (100000, 20000000),
        }
        lo, hi = balance_map[acc_type]
        balance = round(random.uniform(lo, hi), 2)

        accounts.append({
            'account_id':     f'ACC{aid:06d}',
            'customer_id':    cust['customer_id'],
            'account_type':   acc_type,
            'account_status': random.choices(['Active','Dormant','Closed'],weights=[88,8,4])[0],
            'open_date':      open_date.strftime('%Y-%m-%d'),
            'branch_id':      cust['branch_id'],
            'current_balance':balance,
            'min_balance':    (1000 if acc_type=='Savings' else
                               10000 if acc_type=='Current' else 0),
            'interest_rate':  round(random.uniform(2.5, 7.5), 2),
            'nomination_set': random.choices([1,0],weights=[75,25])[0],
            'overdraft_limit':round(random.uniform(0,50000),0) if acc_type=='Current' else 0,
        })
        aid += 1
accounts_df = pd.DataFrame(accounts)

# ════════════════════════════════════════════════════════════════
# TABLE 4: TRANSACTIONS (50,000 transactions — 2020-2024)
# ════════════════════════════════════════════════════════════════
N_TXN = 50000
transactions = []
acc_list = accounts_df[accounts_df['account_status']=='Active']['account_id'].tolist()

for tid in range(1, N_TXN+1):
    acc_id   = random.choice(acc_list)
    acc_row  = accounts_df[accounts_df['account_id']==acc_id].iloc[0]
    cust_row = customers_df[customers_df['customer_id']==acc_row['customer_id']].iloc[0]

    txn_dt   = rand_date('2020-01-01','2024-12-31')
    category = random.choice(TRANSACTION_CATEGORIES)
    channel  = random.choice(TRANSACTION_CHANNELS)

    # Amount based on category
    amt_map = {
        'Salary Credit':     (20000, 500000),
        'EMI Debit':         (5000,  150000),
        'Utility Bills':     (500,   10000),
        'Shopping':          (200,   50000),
        'Food & Dining':     (100,   5000),
        'Travel':            (500,   100000),
        'Entertainment':     (100,   5000),
        'Medical':           (500,   200000),
        'Education':         (1000,  200000),
        'Insurance Premium': (2000,  50000),
        'Investment':        (1000,  500000),
        'Rent':              (5000,  100000),
        'Cash Withdrawal':   (500,   50000),
        'Cash Deposit':      (500,   200000),
        'Fund Transfer':     (1000,  1000000),
        'Interest Credit':   (100,   50000),
        'Dividend':          (500,   100000),
        'Tax Payment':       (1000,  500000),
        'Government Services':(100,  10000),
        'Refund':            (100,   50000),
    }
    lo, hi = amt_map.get(category,(100,100000))
    amount  = round(random.uniform(lo, hi), 2)

    # Debit/Credit
    credit_cats = {'Salary Credit','Interest Credit','Dividend','Cash Deposit','Refund'}
    txn_type    = 'Credit' if category in credit_cats else 'Debit'

    # Fraud logic
    is_fraud = 0
    hour = txn_dt.hour
    if amount > 500000 and hour in range(1,5):
        is_fraud = random.choices([0,1],weights=[50,50])[0]
    elif amount > 200000 and channel == 'Mobile Banking':
        is_fraud = random.choices([0,1],weights=[80,20])[0]
    elif category == 'Fund Transfer' and amount > 100000:
        is_fraud = random.choices([0,1],weights=[90,10])[0]

    status = ('Failed' if is_fraud and random.random()<0.3
              else random.choices(['Success','Failed','Pending'],weights=[91,6,3])[0])

    transactions.append({
        'txn_id':        f'TXN{tid:07d}',
        'account_id':    acc_id,
        'customer_id':   acc_row['customer_id'],
        'txn_date':      txn_dt.strftime('%Y-%m-%d'),
        'txn_month':     txn_dt.strftime('%Y-%m'),
        'txn_year':      txn_dt.year,
        'txn_quarter':   f'Q{(txn_dt.month-1)//3+1}',
        'txn_hour':      txn_dt.hour,
        'txn_day_of_week':txn_dt.strftime('%A'),
        'txn_type':      txn_type,
        'category':      category,
        'amount':        amount,
        'channel':       channel,
        'status':        status,
        'is_fraud':      is_fraud,
        'balance_after': round(max(0, acc_row['current_balance'] +
                         (amount if txn_type=='Credit' else -amount) +
                         random.uniform(-1000,1000)), 2),
        'description':   f'{category} via {channel}',
        'reference_no':  f'REF{random.randint(100000000,999999999)}',
    })

transactions_df = pd.DataFrame(transactions)

# ════════════════════════════════════════════════════════════════
# TABLE 5: LOANS (2000 loans)
# ════════════════════════════════════════════════════════════════
N_LOANS = 2000
loans = []
eligible_custs = customers_df[
    (customers_df['credit_score']>=600) &
    (customers_df['monthly_income']>15000)
]['customer_id'].tolist()

for lid in range(1, N_LOANS+1):
    cust_id  = random.choice(eligible_custs)
    cust_row = customers_df[customers_df['customer_id']==cust_id].iloc[0]
    loan_type = random.choice(LOAN_TYPES)

    amt_map = {
        'Home Loan':         (1000000, 15000000),
        'Personal Loan':     (50000,   1500000),
        'Car Loan':          (300000,  3000000),
        'Education Loan':    (100000,  2000000),
        'Business Loan':     (500000,  10000000),
        'Gold Loan':         (50000,   500000),
        'Credit Card Loan':  (10000,   200000),
    }
    lo, hi      = amt_map[loan_type]
    loan_amt    = round(random.uniform(lo, hi), 0)
    rate_map    = {'Home Loan':8.5,'Personal Loan':13.5,'Car Loan':9.5,
                   'Education Loan':10.5,'Business Loan':12.0,
                   'Gold Loan':10.0,'Credit Card Loan':18.0}
    int_rate    = rate_map[loan_type] + random.uniform(-1.5, 2.5)
    tenure_yrs  = random.choice([1,2,3,5,7,10,15,20,30] if loan_type=='Home Loan'
                                else [1,2,3,5,7])
    disburse_dt = rand_date('2020-01-01','2024-06-01')
    emi         = round(loan_amt * (int_rate/1200) /
                        (1-(1+int_rate/1200)**(-tenure_yrs*12)), 0)

    paid_emis   = random.randint(0, min(tenure_yrs*12, 48))
    outstanding = round(max(0, loan_amt - paid_emis*emi*0.7), 0)

    dpd         = (0 if paid_emis==tenure_yrs*12
                   else random.choices([0,30,60,90,180,365],weights=[70,10,8,5,4,3])[0])

    loans.append({
        'loan_id':          f'LN{lid:06d}',
        'customer_id':      cust_id,
        'loan_type':        loan_type,
        'loan_amount':      loan_amt,
        'interest_rate':    round(int_rate,2),
        'tenure_years':     tenure_yrs,
        'emi_amount':       emi,
        'disbursement_date':disburse_dt.strftime('%Y-%m-%d'),
        'maturity_date':    (disburse_dt + timedelta(days=tenure_yrs*365)).strftime('%Y-%m-%d'),
        'outstanding_amount':outstanding,
        'paid_emis':        paid_emis,
        'total_emis':       tenure_yrs*12,
        'days_past_due':    dpd,
        'loan_status':      ('Closed' if outstanding==0
                             else 'NPA' if dpd>=90
                             else 'Special Mention' if dpd>=30
                             else 'Active'),
        'collateral_type':  ('Property' if loan_type=='Home Loan'
                             else 'Vehicle' if loan_type=='Car Loan'
                             else 'Gold' if loan_type=='Gold Loan'
                             else 'None'),
        'branch_id':        cust_row['branch_id'],
        'credit_score_at_sanction': cust_row['credit_score'],
    })
loans_df = pd.DataFrame(loans)

# ════════════════════════════════════════════════════════════════
# TABLE 6: INVESTMENTS (1500 investment records)
# ════════════════════════════════════════════════════════════════
investments = []
inv_custs = customers_df[
    customers_df['monthly_income']>30000
]['customer_id'].tolist()

for iid in range(1, 1501):
    cust_id  = random.choice(inv_custs)
    inv_type = random.choice(INVESTMENT_TYPES)
    start_dt = rand_date('2020-01-01','2024-01-01')

    amt_map  = {
        'Mutual Fund':    (5000, 500000),
        'Fixed Deposit':  (10000,5000000),
        'Recurring Deposit':(1000,50000),
        'SIP':            (500,  50000),
        'PPF':            (500,  150000),
        'NPS':            (1000, 200000),
        'Stocks':         (5000, 1000000),
        'Gold Bond':      (5000, 500000),
    }
    lo, hi   = amt_map[inv_type]
    inv_amt  = round(random.uniform(lo, hi), 0)
    ret_rate = round(random.uniform(6.0, 18.0), 2)
    duration = random.choice([1,2,3,5,7,10])

    current_val = round(inv_amt * (1 + ret_rate/100) **
                        ((datetime(2024,12,31) - start_dt).days/365), 0)

    investments.append({
        'investment_id':    f'INV{iid:05d}',
        'customer_id':      cust_id,
        'investment_type':  inv_type,
        'invested_amount':  inv_amt,
        'current_value':    current_val,
        'returns_pct':      round((current_val-inv_amt)/inv_amt*100,2),
        'start_date':       start_dt.strftime('%Y-%m-%d'),
        'duration_years':   duration,
        'maturity_date':    (start_dt + timedelta(days=duration*365)).strftime('%Y-%m-%d'),
        'annual_return_rate':ret_rate,
        'status':           random.choices(['Active','Matured','Withdrawn'],weights=[70,20,10])[0],
        'risk_category':    ('High' if inv_type in ['Stocks','Mutual Fund']
                             else 'Medium' if inv_type in ['SIP','Gold Bond','NPS']
                             else 'Low'),
        'branch_id':        customers_df[customers_df['customer_id']==cust_id]['branch_id'].values[0],
    })
investments_df = pd.DataFrame(investments)

# ════════════════════════════════════════════════════════════════
# TABLE 7: CUSTOMER SUPPORT TICKETS (5000 tickets)
# ════════════════════════════════════════════════════════════════
TICKET_CATEGORIES = ['Transaction Dispute','Card Issue','Loan Query',
                     'Account Opening','KYC Update','Net Banking Issue',
                     'ATM Issue','Interest Query','Fraud Report','General Query']
PRIORITIES = ['Low','Medium','High','Critical']

tickets = []
for tid in range(1, 5001):
    cust_id  = random.choice(customers_df['customer_id'].tolist())
    cat      = random.choice(TICKET_CATEGORIES)
    priority = ('Critical' if cat=='Fraud Report'
                else random.choices(PRIORITIES,weights=[30,40,20,10])[0])
    created  = rand_date('2020-01-01','2024-12-31')
    resolved = (created + timedelta(hours=random.randint(1,168))
                if random.random()<0.85 else None)

    tickets.append({
        'ticket_id':     f'TKT{tid:06d}',
        'customer_id':   cust_id,
        'category':      cat,
        'priority':      priority,
        'status':        'Resolved' if resolved else random.choice(['Open','In Progress']),
        'created_date':  created.strftime('%Y-%m-%d'),
        'resolved_date': resolved.strftime('%Y-%m-%d') if resolved else None,
        'resolution_hours': round((resolved-created).total_seconds()/3600,1) if resolved else None,
        'channel':       random.choice(['Phone','Email','Chat','Branch','App']),
        'satisfaction_score': random.randint(1,5) if resolved else None,
        'agent_id':      f'AGT{random.randint(1,50):03d}',
    })
tickets_df = pd.DataFrame(tickets)

# ── Save all ─────────────────────────────────────────────────
dfs = {
    'branches':     branches_df,
    'customers':    customers_df,
    'accounts':     accounts_df,
    'transactions': transactions_df,
    'loans':        loans_df,
    'investments':  investments_df,
    'tickets':      tickets_df,
}
for name, df in dfs.items():
    df.to_csv(f'{BASE}/{name}.csv', index=False)
    print(f"✅ {name:15s}: {len(df):6,} rows × {len(df.columns)} cols")

print(f"\n{'─'*45}")
print(f"💰 Total Loan Book:   ₹{loans_df['loan_amount'].sum()/1e7:.1f} Crore")
print(f"💳 Total Transactions: {len(transactions_df):,}")
print(f"🏦 NPA Loans:          {(loans_df['loan_status']=='NPA').sum()}")
print(f"🚨 Fraud Transactions: {transactions_df['is_fraud'].sum()}")
print(f"📊 Active Investments: {(investments_df['status']=='Active').sum()}")
print(f"🎫 Support Tickets:    {len(tickets_df):,}")
