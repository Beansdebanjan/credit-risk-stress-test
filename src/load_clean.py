import pandas as pd
import os
import sys

# Add src to path so we can import utils
sys.path.append(os.path.abspath("src"))
from utils import load_config

def main():
    config = load_config()
    input_file = config.get("input_file", "data/credit_loan_stress_test_dataset_1k.xlsx")
    sheet_name = config.get("sheet_name", "Stress_Test_Dataset")
    
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    numeric_cols = ['Monthly_Income', 'Monthly_Expenditure', 'Monthly_Savings', 'Monthly_EMI', 'Credit_Utilization_%', 'Age']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'Monthly_EMI' in df.columns:
        df['Monthly_EMI'] = df['Monthly_EMI'].fillna(0)
    
    # Drop PII if present
    pii = ['Name', 'Phone', 'Email', 'SSN', 'Address']
    df = df.drop(columns=[c for c in pii if c in df.columns])
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/clean_loans.csv', index=False)
    print("Data cleaned and saved to data/clean_loans.csv")

if __name__ == "__main__":
    main()
