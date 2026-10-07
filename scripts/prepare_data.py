import pandas as pd
import numpy as np
import json
import re
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

# Configuration
UPLOAD_DIR = "/mnt/user-data/uploads"
DATA_DIR = "frontend/data"  # Store in frontend so JS can fetch it

os.makedirs(DATA_DIR, exist_ok=True)

def parse_experience(exp_str):
    if pd.isna(exp_str): return None, None
    m = re.findall(r'(\d+)', str(exp_str))
    if len(m) >= 2: return int(m[0]), int(m[1])
    if len(m) == 1: return int(m[0]), int(m[0])
    return None, None

def map_salary_bucket(sal_str):
    if pd.isna(sal_str): return None
    sal_str = str(sal_str).lower().replace(' ', '')
    mapping = {
        '0to3': 1.5, '3to6': 4.5, '6to10': 8.0, 
        '10to15': 12.5, '15to25': 20.0, '25to50': 37.5
    }
    for k, v in mapping.items():
        if k in sal_str: return v
    return None

def clean_skills(skills_str):
    if pd.isna(skills_str): return []
    skills = [s.strip().lower() for s in str(skills_str).split(',')]
    clean = []
    for s in skills:
        if not s or s == '...': continue
        if s in ['ml', 'machinelearning']: s = 'machine learning'
        if s in ['powerbi', 'power bi']: s = 'power bi'
        clean.append(s)
    return list(set(clean))

def clean_locations(loc_str):
    if pd.isna(loc_str): return []
    locs = [l.strip() for l in str(loc_str).split(',')]
    clean = []
    for l in locs:
        if 'delhi' in l.lower() or 'ncr' in l.lower() or 'noida' in l.lower() or 'gurgaon' in l.lower():
            clean.append('Delhi NCR')
        else:
            clean.append(l)
    return list(set(clean))

def is_data_role(desig):
    if pd.isna(desig): return False
    desig = str(desig).lower()
    keywords = ['data scien', 'analyst', 'analytics', 'machine learning', 'ml', 'ai', 'business intelligence']
    return any(k in desig for k in keywords)

# --- 1. Analytics Jobs ---
print("Processing Analytics Jobs...")
analytics_file = os.path.join(UPLOAD_DIR, "Analytics_Jobs.csv")
if os.path.exists(analytics_file):
    df_an = pd.read_csv(analytics_file)
    df_an['job_type'] = df_an['job_type'].astype(str).str.lower().str.strip()
    df_an.loc[df_an['job_type'] == 'analytic', 'job_type'] = 'analytics'
    
    df_an['exp_min'], df_an['exp_max'] = zip(*df_an['experience'].apply(parse_experience))
    df_an['salary_mid'] = df_an['salary'].apply(map_salary_bucket)
    df_an['skills_list'] = df_an['key_skills'].apply(clean_skills)
    df_an['locations_list'] = df_an['location'].apply(clean_locations)
    df_an['is_data_role'] = df_an['job_desig'].apply(is_data_role)
    
    df_an['job_description'] = df_an['job_description'].fillna('')
    df_an['key_skills_str'] = df_an['skills_list'].apply(lambda x: ','.join(x))
    df_an['locations_str'] = df_an['locations_list'].apply(lambda x: ','.join(x))
    
    # Drop duplicates
    df_an = df_an.drop_duplicates(subset=['job_desig', 'key_skills_str', 'locations_str', 'experience'])
    
    # Export aggregations
    data_roles = df_an[df_an['is_data_role']]
    
    # Skill demand
    all_skills = [s for skills in data_roles['skills_list'] for s in skills]
    skill_counts = pd.Series(all_skills).value_counts().head(50).to_dict()
    with open(f"{DATA_DIR}/skill_demand.json", 'w') as f: json.dump(skill_counts, f)
    
    # Location demand
    all_locs = [l for locs in data_roles['locations_list'] for l in locs]
    loc_counts = pd.Series(all_locs).value_counts().head(20).to_dict()
    with open(f"{DATA_DIR}/location_demand.json", 'w') as f: json.dump(loc_counts, f)
    
    # Jobs Index for resume scanner
    jobs_index = data_roles[['job_desig', 'skills_list', 'locations_list', 'exp_min', 'exp_max', 'salary_mid']].dropna(subset=['job_desig']).to_dict(orient='records')
    with open(f"{DATA_DIR}/jobs_index.json", 'w') as f: json.dump(jobs_index, f)
else:
    print(f"Warning: {analytics_file} not found.")

# --- 2. Data Science Jobs ---
print("Processing Data Science Jobs...")
ds_file = os.path.join(UPLOAD_DIR, "DataScience_Jobs.csv")
if os.path.exists(ds_file):
    df_ds = pd.read_csv(ds_file)
    def parse_lpa(val):
        if pd.isna(val): return None
        m = re.search(r'([\d\.]+)', str(val))
        return float(m.group(1)) if m else None
    
    df_ds['avg_salary'] = df_ds['avg_salary'].apply(parse_lpa)
    df_ds['min_salary'] = df_ds['min_salary'].apply(parse_lpa)
    df_ds['max_salary'] = df_ds['max_salary'].apply(parse_lpa)
    
    company_hiring = df_ds.groupby('company_name')['num_of_jobs'].sum().sort_values(ascending=False).head(50).to_dict()
    with open(f"{DATA_DIR}/company_hiring.json", 'w') as f: json.dump(company_hiring, f)
    
    roles = df_ds[['company_name', 'job_title', 'min_experience', 'min_salary', 'avg_salary', 'max_salary', 'num_of_jobs']].dropna(subset=['company_name', 'job_title']).to_dict(orient='records')
    with open(f"{DATA_DIR}/salary_by_role.json", 'w') as f: json.dump(roles, f)
else:
    print(f"Warning: {ds_file} not found.")


# --- 3. JDS & SDS Models ---
def train_and_export_model(df, feature_cols, target_col, outfile):
    # Clean columns
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    target_col = [c for c in df.columns if target_col in c][0]
    feature_cols = [c for c in df.columns if any(f in c for f in feature_cols)]
    
    X = df[feature_cols].values
    y = df[target_col].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression()
    cv_scores = cross_val_score(model, X_scaled, y, cv=5)
    model.fit(X_scaled, y)
    
    percentiles = {}
    for i, col in enumerate(feature_cols):
        percentiles[col] = np.percentile(X[:, i], [10, 25, 50, 75, 90]).tolist()
    
    out_data = {
        "features": feature_cols,
        "means": scaler.mean_.tolist(),
        "stds": scaler.scale_.tolist(),
        "coefficients": model.coef_[0].tolist(),
        "intercept": model.intercept_[0],
        "cv_accuracy": float(np.mean(cv_scores)),
        "percentiles": percentiles
    }
    with open(outfile, 'w') as f: json.dump(out_data, f)
    print(f"Exported {outfile} with CV Acc: {np.mean(cv_scores):.2f}")

print("Processing JDS Traits...")
jds_file = os.path.join(UPLOAD_DIR, "JDS_Skill_Traits.xlsx")
if os.path.exists(jds_file):
    df_jds = pd.read_excel(jds_file)
    train_and_export_model(df_jds, 
        ['big_data', 'maths_stats', 'coding', 'ai_and_ml', 'dashboard'], 
        'salary_hike', f"{DATA_DIR}/jds_model.json")
else:
    print(f"Warning: {jds_file} not found.")

print("Processing SDS Traits...")
sds_file = os.path.join(UPLOAD_DIR, "SDS_Personality_Traits.xlsx")
if sds_file and os.path.exists(sds_file):
    df_sds = pd.read_excel(sds_file)
    train_and_export_model(df_sds, 
        ['neuroticism', 'extraversion', 'openness', 'agreeableness', 'conscientiousness'], 
        'success', f"{DATA_DIR}/sds_model.json")
else:
    print(f"Warning: {sds_file} not found.")

print("Done! Data prepared in frontend/data/")
