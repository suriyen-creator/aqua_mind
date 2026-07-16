import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import json

def train_bloom_model(data_path='mock_data.csv'):
    df = pd.read_csv(data_path)
    X = df.drop('is_bloom', axis=1)
    y = df['is_bloom']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Handle imbalance with SMOTE (8.1.6)
    sm = SMOTE(random_state=42)
    X_resampled, y_resampled = sm.fit_resample(X_train, y_train)
    
    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        objective='binary:logistic',
        random_state=42
    )
    model.fit(X_resampled, y_resampled)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("Model Evaluation:")
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC: {roc_auc_score(y_test, y_prob):.4f}")
    
    # Save model
    model.save_model('xgboost_model.json')
    print("Model saved to xgboost_model.json")

if __name__ == '__main__':
    train_bloom_model()
