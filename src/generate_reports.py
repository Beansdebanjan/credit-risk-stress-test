import pandas as pd
import os
import sys

# Add src to path so we can import utils
sys.path.append(os.path.abspath("src"))
from utils import load_config

def main():
    config = load_config()
    output_dir = config.get("output_dir", "outputs")
    df = pd.read_csv(f'{output_dir}/stressed_full.csv')
    
    # Top 5% by Stress Score
    top_5pct_idx = int(len(df) * 0.05)
    top_risk_df = df.sort_values(by='StressScore', ascending=False).head(top_5pct_idx)
    top_risk_df.to_csv(f'{output_dir}/top_risk_5pct.csv', index=False)
    
    # Top 20 memos
    top20 = df.sort_values(by='StressScore', ascending=False).head(20)
    memos = []
    for _, row in top20.iterrows():
        drivers = []
        if row['StressedMonthlySavings'] < 0:
            drivers.append("Negative savings")
        if row['StressedCreditUtilization'] >= 90:
            drivers.append(f"Utilization {row['StressedCreditUtilization']}%")
        if row['StressedDTI'] >= 40:
            drivers.append("High DTI")
            
        driver_str = "; ".join(drivers) if drivers else "Elevated metrics"
        memos.append({
            'Customer_ID': row['Customer_ID'],
            'StressScore': row['StressScore'],
            'StressLevel': row['StressLevel'],
            'Default_Risk': row['Default_Risk'],
            'KeyDrivers': driver_str,
            'RecommendedAction': "Immediate RM outreach; request updated income docs; consider temporary limit reduction"
        })
    pd.DataFrame(memos).to_csv(f'{output_dir}/top20_memos.csv', index=False)
    
    # Summary report
    with open(f'{output_dir}/summary_report.txt', 'w') as f:
        f.write(f"Rows processed: {len(df)}\n")
        f.write(f"Mean StressScore: {df['StressScore'].mean():.2f}\n")
        counts = df['StressLevel'].value_counts()
        f.write(f"StressLevel counts: Low {counts.get('Low', 0)}, Medium {counts.get('Medium', 0)}, High {counts.get('High', 0)}\n")
        f.write(f"Default_Risk flagged: {(df['Default_Risk'] == 'Yes').mean() * 100:.2f}%\n")
        f.write(f"Percent with negative stressed savings: {(df['StressedMonthlySavings'] <= 0).mean() * 100:.2f}%\n")
        
    print("Reports generated.")

if __name__ == "__main__":
    main()
