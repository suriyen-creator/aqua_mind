import os
import joblib
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from imblearn.over_sampling import SMOTE


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_DIR = BASE_DIR / "models"


# ==========================
# Load Dataset
# ==========================

df = pd.read_csv(DATA_PATH)

print("Dataset Shape :", df.shape)
print(df.head())


# ==========================
# Prepare Features
# ==========================

drop_columns = [
    "date",
    "latitude",
    "longitude",
    "Bloom"
]

X = df.drop(columns=drop_columns)

y = df["Bloom"]


# ==========================
# Train Test Split
# ==========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("\nBefore SMOTE")
print(y_train.value_counts())


# ==========================
# SMOTE
# ==========================

smote = SMOTE(random_state=42)

X_train, y_train = smote.fit_resample(
    X_train,
    y_train
)


print("\nAfter SMOTE")
print(y_train.value_counts())


# ==========================
# Random Forest
# ==========================

rf = RandomForestClassifier(

    n_estimators=300,

    max_depth=12,

    random_state=42,

    n_jobs=-1

)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

rf_prob = rf.predict_proba(X_test)[:,1]


print("\n==============================")
print("Random Forest")
print("==============================")

print("Accuracy :", accuracy_score(y_test, rf_pred))

print("Precision :", precision_score(y_test, rf_pred))

print("Recall :", recall_score(y_test, rf_pred))

print("F1 :", f1_score(y_test, rf_pred))

print("ROC AUC :", roc_auc_score(y_test, rf_prob))

print()

print(confusion_matrix(y_test, rf_pred))

print()

print(classification_report(y_test, rf_pred))


# ==========================
# XGBoost
# ==========================

xgb = XGBClassifier(

    n_estimators=400,

    learning_rate=0.05,

    max_depth=6,

    subsample=0.8,

    colsample_bytree=0.8,

    eval_metric="logloss",

    random_state=42

)

xgb.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)

xgb_prob = xgb.predict_proba(X_test)[:,1]


print("\n==============================")
print("XGBoost")
print("==============================")

print("Accuracy :", accuracy_score(y_test, xgb_pred))

print("Precision :", precision_score(y_test, xgb_pred))

print("Recall :", recall_score(y_test, xgb_pred))

print("F1 :", f1_score(y_test, xgb_pred))

print("ROC AUC :", roc_auc_score(y_test, xgb_prob))

print()

print(confusion_matrix(y_test, xgb_pred))

print()

print(classification_report(y_test, xgb_pred))


# ==========================
# Save All Models
# ==========================

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Save ทุกโมเดล
joblib.dump(
    rf,
    MODEL_DIR / "random_forest.pkl"
)

joblib.dump(
    xgb,
    MODEL_DIR / "xgboost.pkl"
)

# JSON is the portable artifact used by the Streamlit technical demo.
xgb.get_booster().save_model(MODEL_DIR / "xgboost_model.json")

print("\n==============================")
print("Models Saved")
print("==============================")
print("✓ models/random_forest.pkl")
print("✓ models/xgboost.pkl")
print("✓ models/xgboost_model.json")


# ==========================
# Compare Models
# ==========================

results = pd.DataFrame({
    "Model": ["Random Forest", "XGBoost"],
    "Accuracy": [
        accuracy_score(y_test, rf_pred),
        accuracy_score(y_test, xgb_pred)
    ],
    "Precision": [
        precision_score(y_test, rf_pred),
        precision_score(y_test, xgb_pred)
    ],
    "Recall": [
        recall_score(y_test, rf_pred),
        recall_score(y_test, xgb_pred)
    ],
    "F1": [
        f1_score(y_test, rf_pred),
        f1_score(y_test, xgb_pred)
    ],
    "ROC AUC": [
        roc_auc_score(y_test, rf_prob),
        roc_auc_score(y_test, xgb_prob)
    ]
})

print("\n==============================")
print("Model Comparison")
print("==============================")
print(results.round(4))


# ==========================
# Best Model
# ==========================

best_idx = results["ROC AUC"].idxmax()
best_model = results.loc[best_idx]

print("\n==============================")
print("Best Model")
print("==============================")
print(f"Model      : {best_model['Model']}")
print(f"Accuracy   : {best_model['Accuracy']:.4f}")
print(f"Precision  : {best_model['Precision']:.4f}")
print(f"Recall     : {best_model['Recall']:.4f}")
print(f"F1 Score   : {best_model['F1']:.4f}")
print(f"ROC AUC    : {best_model['ROC AUC']:.4f}")
