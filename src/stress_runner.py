import pandas as pd
import numpy as np
import os
import sys

# Add src to path so we can import utils
sys.path.append(os.path.abspath("src"))
from utils import load_config

def main():
    config = load_config()
    df = pd.read_csv('data/clean_loans.csv')
    
    inc_shock = config.get("income_shock_pct", -0.30)
    exp_shock = config.get("expenditure_shock_pct", 0.20)
    util_shock = config.get("utilization_shock_pp", 10)
    min_income = config.get("min_income_floor", 1.0)
    
    df['NewMonthlyIncome'] = df['Monthly_Income'] * (1 + inc_shock)
    df['NewMonthlyIncome'] = df['NewMonthlyIncome'].clip(lower=min_income)
    
    df['NewMonthlyExpenditure'] = df['Monthly_Expenditure'] * (1 + exp_shock)
    df['StressedMonthlySavings'] = df['NewMonthlyIncome'] - df['NewMonthlyExpenditure']
    
    df['StressedCreditUtilization'] = df['Credit_Utilization_%'] + util_shock
    if config.get("cap_utilization_at_100", True):
        df['StressedCreditUtilization'] = df['StressedCreditUtilization'].clip(upper=100)
        
    df['StressedDTI'] = (df['Monthly_EMI'] / df['NewMonthlyIncome']) * 100
    
    # Components
    cashflow_penalty = np.where(df['StressedMonthlySavings'] <= 0, 40, 
        40 * np.maximum(0, df['Monthly_Savings'] - df['StressedMonthlySavings']) / (df['Monthly_Savings'] + 1) + 1)
        
    utilization_penalty = 30 * (df['StressedCreditUtilization'] / 100)
    debt_penalty = 30 * np.minimum(df['StressedDTI'] / 100, 1.0)
    
    df['StressScore'] = np.round(cashflow_penalty + utilization_penalty + debt_penalty, 2)
    
    conditions = [
        (df['StressScore'] <= 33.3),
        (df['StressScore'] > 33.3) & (df['StressScore'] < 66.6),
        (df['StressScore'] >= 66.6)
    ]
    choices = ['Low', 'Medium', 'High']
    df['StressLevel'] = np.select(conditions, choices, default='High')
    
    df['Default_Risk'] = np.where((df['StressScore'] >= 66.6) | 
        ((df['StressedMonthlySavings'] <= 0) & (df['StressedDTI'] >= 40)), 'Yes', 'No')
        
    output_dir = config.get("output_dir", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(f'{output_dir}/stressed_full.csv', index=False)
    df.to_parquet(f'{output_dir}/dashboard_data.parquet', index=False)
    print("Stress test completed. Output saved.")

if __name__ == "__main__":
    main()
