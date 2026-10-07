import pandas as pd
import json
import os
import math

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'data'))
TSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'user_data.tsv'))

def clean_salary(sal_str):
    if pd.isna(sal_str):
        return None
    sal_str = str(sal_str).strip()
    if sal_str.endswith('L'):
        try:
            return float(sal_str[:-1])
        except ValueError:
            return None
    return None

def process_data():
    df = pd.read_csv(TSV_FILE, sep='\t')
    
    # Process for company_hiring.json
    company_hiring = df.groupby('company_name')['num_of_jobs'].sum().to_dict()
    top_hiring = dict(sorted(company_hiring.items(), key=lambda item: item[1], reverse=True)[:30])
    
    with open(os.path.join(FRONTEND_DIR, 'company_hiring.json'), 'w') as f:
        json.dump(top_hiring, f, indent=2)
        
    # Process for salary_by_role.json
    salary_data = []
    for _, row in df.iterrows():
        min_sal = clean_salary(row['min_salary'])
        max_sal = clean_salary(row['max_salary'])
        avg_sal = clean_salary(row['avg_salary'])
        
        salary_data.append({
            'company_name': row['company_name'],
            'job_title': row['job_title'],
            'min_salary': min_sal,
            'max_salary': max_sal,
            'avg_salary': avg_sal,
            'min_experience': row['min_experience'],
            'num_of_jobs': row['num_of_jobs']
        })
        
    def replace_nan_with_none(obj):
        if isinstance(obj, float) and math.isnan(obj):
            return None
        elif isinstance(obj, dict):
            return {k: replace_nan_with_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_nan_with_none(v) for v in obj]
        return obj
    
    salary_data = replace_nan_with_none(salary_data)
        
    with open(os.path.join(FRONTEND_DIR, 'salary_by_role.json'), 'w') as f:
        json.dump(salary_data, f, indent=2)

if __name__ == '__main__':
    process_data()
    print("Done generating JSON.")
