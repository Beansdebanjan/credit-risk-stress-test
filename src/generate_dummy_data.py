import pandas as pd
import numpy as np
import os

def generate_data(n=1000):
    np.random.seed(42)
    
    # Generate ID
    customer_id = [f"CUST{str(i).zfill(4)}" for i in range(1, n+1)]
    
    # Generate Income (30k to 150k)
    income = np.random.randint(30000, 150000, n)
    
    # Generate Expenditure (40% to 80% of income)
    exp_ratio = np.random.uniform(0.4, 0.8, n)
    expenditure = (income * exp_ratio).astype(int)
    
    # Generate Savings
    savings = income - expenditure
    
    # Generate EMI (10% to 40% of income)
    emi_ratio = np.random.uniform(0.1, 0.4, n)
    emi = (income * emi_ratio).astype(int)
    
    # Generate Credit Utilization (10% to 90%)
    utilization = np.random.randint(10, 90, n)
    
    # Generate Age (22 to 60)
    age = np.random.randint(22, 60, n)
    
    # Generate FirstTimeUser (Yes/No)
    first_time = np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7])
    
    df = pd.DataFrame({
        'Customer_ID': customer_id,
        'Monthly_Income': income,
        'Monthly_Expenditure': expenditure,
        'Monthly_Savings': savings,
        'Monthly_EMI': emi,
        'Credit_Utilization_%': utilization,
        'Age': age,
        'FirstTimeUser': first_time
    })
    
    os.makedirs('data', exist_ok=True)
    df.to_excel('data/credit_loan_stress_test_dataset_1k.xlsx', sheet_name='Stress_Test_Dataset', index=False)
    print("Generated 1000 rows of dummy data at data/credit_loan_stress_test_dataset_1k.xlsx")

if __name__ == "__main__":
    generate_data()
