import pandas as pd
import numpy as np
import json
import os
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'data')
DB_PATH = os.path.join(BASE_DIR, 'database', 'placify.db')

def generate_sds_data():
    np.random.seed(42)
    n_samples = 161
    
    # Ranges ~17-68
    data = {
        'id': range(1, n_samples + 1),
        'neuroticism': np.random.uniform(17, 68, n_samples),
        'extraversion': np.random.uniform(17, 68, n_samples),
        'openness_to_experience': np.random.uniform(17, 68, n_samples),
        'agreeableness': np.random.uniform(17, 68, n_samples),
        'conscientiousness': np.random.uniform(17, 68, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Scale to calculate probability using target weights
    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(df.drop('id', axis=1))
    
    # openness (~2.05) and conscientiousness (~2.10) dominate, extraversion ~0.96, neuroticism ~0.80, agreeableness ~0.63
    weights = np.array([0.80, 0.96, 2.05, 0.63, 2.10])
    
    # Logit
    logits = np.dot(scaled_feats, weights) - 1.5 # Add intercept shift to balance
    probs = 1 / (1 + np.exp(-logits))
    
    # Add noise
    df['success_classification_high_low'] = np.random.binomial(1, probs)
    
    return df

def process_sds():
    print("Generating mock SDS Personality Traits dataset...")
    df = generate_sds_data()
    
    # Save TSV
    tsv_path = os.path.join(BASE_DIR, 'sds_data.tsv')
    df.to_csv(tsv_path, sep='\t', index=False)
    print(f"Saved dataset to {tsv_path}")
    
    # Save to SQLite
    print(f"Adding to SQLite database ({DB_PATH})...")
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('sds_personality_traits', conn, if_exists='replace', index=False)
    conn.close()
    
    # Train Model
    print("Training SDS Logistic Regression Model...")
    features = ['neuroticism', 'extraversion', 'openness_to_experience', 'agreeableness', 'conscientiousness']
    X = df[features]
    y = df['success_classification_high_low']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(C=1.0)
    model.fit(X_scaled, y)
    
    cv_scores = cross_val_score(LogisticRegression(C=1.0), X_scaled, y, cv=5)
    cv_accuracy = np.mean(cv_scores)
    
    print(f"CV Accuracy: {cv_accuracy:.2%}")
    for feat, coef in zip(features, model.coef_[0]):
        print(f"  {feat}: {coef:.2f}")
        
    # Calculate Percentiles (for frontend comparison)
    percentiles = {}
    for feat in features:
        percentiles[feat] = {
            '10': np.percentile(df[feat], 10),
            '25': np.percentile(df[feat], 25),
            '50': np.percentile(df[feat], 50),
            '75': np.percentile(df[feat], 75),
            '90': np.percentile(df[feat], 90)
        }
        
    sds_model = {
        'features': features,
        'means': scaler.mean_.tolist(),
        'stds': scaler.scale_.tolist(),
        'coefficients': model.coef_[0].tolist(),
        'intercept': float(model.intercept_[0]),
        'cv_accuracy': float(cv_accuracy),
        'percentiles': percentiles
    }
    
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    with open(os.path.join(FRONTEND_DIR, 'sds_model.json'), 'w') as f:
        json.dump(sds_model, f, indent=2)
        
    print("Successfully exported sds_model.json")

if __name__ == '__main__':
    process_sds()
