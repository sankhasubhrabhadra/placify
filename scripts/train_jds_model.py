import pandas as pd
import json
import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'data'))
TSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jds_data.tsv'))

def train_jds_model():
    df = pd.read_csv(TSV_FILE, sep='\t')
    
    # Target and Features
    target = 'salary_hike_high_or_low'
    features = [
        'big_data_skills',
        'maths-stats_skills',
        'coding_skills',
        'ai_and_ml_skills',
        'dashboard_and_storytelling_skills'
    ]
    
    X = df[features]
    y = df[target]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = LogisticRegression()
    model.fit(X_scaled, y)
    
    # Cross Validation
    cv_scores = cross_val_score(LogisticRegression(), X_scaled, y, cv=5)
    cv_accuracy = np.mean(cv_scores)
    
    # Export parameters
    jds_model = {
        'features': features,
        'means': scaler.mean_.tolist(),
        'stds': scaler.scale_.tolist(),
        'coefficients': model.coef_[0].tolist(),
        'intercept': float(model.intercept_[0]),
        'cv_accuracy': float(cv_accuracy)
    }
    
    # Ensure frontend/data exists
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    
    with open(os.path.join(FRONTEND_DIR, 'jds_model.json'), 'w') as f:
        json.dump(jds_model, f, indent=2)
        
    print(f"JDS Model trained. CV Accuracy: {cv_accuracy:.2%}")
    print("Coefficients:")
    for feat, coef in zip(features, model.coef_[0]):
        print(f"  {feat}: {coef:.2f}")

if __name__ == '__main__':
    train_jds_model()
