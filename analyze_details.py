import csv
from collections import defaultdict

def main():
    file_path = 'outputs/stressed_full.csv'
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Age Variations on Credit Utilization
    age_groups = {'<30': [], '30-40': [], '40-50': [], '>50': []}
    
    # Income Barrier on Default Risk
    income_groups = {'<60k': [], '60k-100k': [], '>100k': []}

    for row in data:
        age = int(row['Age'])
        credit_util = float(row['Credit_Utilization_%'])
        stressed_util = float(row['StressedCreditUtilization'])
        income = float(row['Monthly_Income'])
        default_risk = 1 if row['Default_Risk'] == 'Yes' else 0
        stress_score = float(row['StressScore'])

        # Group by age
        if age < 30:
            age_groups['<30'].append((credit_util, stressed_util, stress_score))
        elif age <= 40:
            age_groups['30-40'].append((credit_util, stressed_util, stress_score))
        elif age <= 50:
            age_groups['40-50'].append((credit_util, stressed_util, stress_score))
        else:
            age_groups['>50'].append((credit_util, stressed_util, stress_score))

        # Group by income
        if income < 60000:
            income_groups['<60k'].append((default_risk, stress_score))
        elif income <= 100000:
            income_groups['60k-100k'].append((default_risk, stress_score))
        else:
            income_groups['>100k'].append((default_risk, stress_score))

    print("=== AGE VARIATIONS & CREDIT SPLIT ===")
    for group, metrics in age_groups.items():
        if metrics:
            avg_base_util = sum(m[0] for m in metrics) / len(metrics)
            avg_stress_util = sum(m[1] for m in metrics) / len(metrics)
            avg_stress_score = sum(m[2] for m in metrics) / len(metrics)
            print(f"Age {group}: Base Util: {avg_base_util:.1f}% | Stressed Util: {avg_stress_util:.1f}% | Avg Stress Score: {avg_stress_score:.1f}")

    print("\n=== INCOME BARRIER & DEFAULT RISK ===")
    for group, metrics in income_groups.items():
        if metrics:
            default_rate = (sum(m[0] for m in metrics) / len(metrics)) * 100
            avg_stress_score = sum(m[1] for m in metrics) / len(metrics)
            print(f"Income {group}: Default Risk: {default_rate:.1f}% | Avg Stress Score: {avg_stress_score:.1f}")

if __name__ == '__main__':
    main()
