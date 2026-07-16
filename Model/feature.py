import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# โหลดโมเดล
model = joblib.load(BASE_DIR / "models" / "random_forest.pkl")

# โหลด Dataset
df = pd.read_csv(BASE_DIR / "data" / "dataset.csv")

# เตรียม Feature
X = df.drop(columns=[
    "date",
    "latitude",
    "longitude",
    "Bloom"
])

# ตรวจสอบว่าโมเดลมี feature_importances_
if not hasattr(model, "feature_importances_"):
    print("Model นี้ไม่รองรับ Feature Importance")
    exit()

importance = model.feature_importances_

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importance
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=True
)

output_dir = BASE_DIR / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(10,6))
plt.barh(
    importance_df["Feature"],
    importance_df["Importance"]
)

plt.xlabel("Importance")
plt.title("Random Forest Feature Importance")

plt.tight_layout()

plt.savefig(output_dir / "feature_importance.png", dpi=300)

plt.show()

print("บันทึกไฟล์ outputs/feature_importance.png เรียบร้อย")
