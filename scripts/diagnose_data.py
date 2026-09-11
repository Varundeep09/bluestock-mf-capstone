import pandas as pd
import numpy as np

# Load transactions
tx = pd.read_csv('data/processed/clean_transactions.csv')

print("=" * 70)
print("1. FULL TRANSACTION DATE RANGE CHECK")
print("=" * 70)
print(f"Total Transactions in dataset: {len(tx):,}")
print(f"Earliest Transaction Date:     {tx['transaction_date'].min()}")
print(f"Latest Transaction Date:       {tx['transaction_date'].max()}")
print("\nTransactions by Calendar Year:")
tx['year'] = pd.to_datetime(tx['transaction_date']).dt.year
print(tx['year'].value_counts().sort_index().to_string())

print("\nTransactions by Month:")
tx['month'] = pd.to_datetime(tx['transaction_date']).dt.strftime('%Y-%m')
print(tx['month'].value_counts().sort_index().to_string())

print("\n" + "=" * 70)
print("2. SIP GAP DISTRIBUTION ANALYSIS")
print("=" * 70)
# Strictly filter SIPs
sip_only = tx[tx['transaction_type'] == 'SIP'].copy()
sip_only['tx_date'] = pd.to_datetime(sip_only['transaction_date'])
print(f"Total SIP Transactions:     {len(sip_only):,}")
print(f"Total Non-SIP Transactions: {len(tx) - len(sip_only):,}")

investor_gaps = []
for inv_id, grp in sip_only.groupby('investor_id'):
    grp = grp.sort_values('tx_date')
    count = len(grp)
    if count >= 6:
        diffs = grp['tx_date'].diff().dt.days.dropna()
        avg_gap = float(diffs.mean())
        investor_gaps.append({
            'investor_id': inv_id,
            'sip_count': count,
            'avg_gap': avg_gap,
            'min_gap': float(diffs.min()),
            'max_gap': float(diffs.max())
        })

df_gaps = pd.DataFrame(investor_gaps)
n = len(df_gaps)
print(f"\nTotal Investors with 6+ SIPs: {n:,}")
print("\nAverage Gap Summary Statistics:")
print(df_gaps['avg_gap'].describe().to_string())

# Detailed Gap Buckets
b_under_30 = int((df_gaps['avg_gap'] < 30).sum())
b_30_35 = int(((df_gaps['avg_gap'] >= 30) & (df_gaps['avg_gap'] <= 35)).sum())
b_35_40 = int(((df_gaps['avg_gap'] > 35) & (df_gaps['avg_gap'] <= 40)).sum())
b_40_50 = int(((df_gaps['avg_gap'] > 40) & (df_gaps['avg_gap'] <= 50)).sum())
b_50_plus = int((df_gaps['avg_gap'] > 50).sum())

print("\nDistribution of Average SIP Gaps (Days):")
print(f"  < 30 days    : {b_under_30:5d} ({b_under_30/n*100:5.2f}%)")
print(f"  30 - 35 days : {b_30_35:5d} ({b_30_35/n*100:5.2f}%)")
print(f"  35 - 40 days : {b_35_40:5d} ({b_35_40/n*100:5.2f}%)")
print(f"  40 - 50 days : {b_40_50:5d} ({b_40_50/n*100:5.2f}%)")
print(f"  > 50 days    : {b_50_plus:5d} ({b_50_plus/n*100:5.2f}%)")

print("\nInspection of Sample Investors with >= 6 SIPs:")
for _, row in df_gaps.head(5).iterrows():
    inv = row['investor_id']
    dates = sip_only[sip_only['investor_id'] == inv].sort_values('tx_date')['transaction_date'].tolist()
    print(f"\nInvestor: {inv} | SIP Count: {row['sip_count']} | Avg Gap: {row['avg_gap']:.1f} days")
    print(f"Dates: {dates}")
