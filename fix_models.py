"""
fix_models.py
─────────────
Re-trains and saves all .pkl files with protocol=2.
Compatible with Python 3.10 + NumPy 2.2.6 (Render environment).
Run this ONCE locally, then push models/ to GitHub.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import f1_score, classification_report

print("=" * 55)
print("🔧 fix_models.py — Rebuilding all pkl files")
print(f"   NumPy:   {np.__version__}")
print(f"   Joblib:  {joblib.__version__}")
print("=" * 55)

# ── Load Data ──────────────────────────────────────────────────────────────────
print("\n📂 Loading data...")
df = pd.read_csv("data/credit_data.csv")
df = df.drop(columns=["Unnamed: 0"], errors="ignore")
print(f"   Shape: {df.shape}")

# ── Target Column ──────────────────────────────────────────────────────────────
possible_targets = ["SeriousDlqin2yrs", "target", "label", "default", "Default"]
target_col = next((c for c in possible_targets if c in df.columns), None)
if target_col is None:
    raise ValueError(f"❌ Target column not found! Columns: {list(df.columns)}")
print(f"   Target: '{target_col}'")
print(f"   Class distribution:\n{df[target_col].value_counts()}")

# ── Features ───────────────────────────────────────────────────────────────────
feature_cols = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30-59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse",
    "NumberOfDependents",
]
feature_cols = [c for c in feature_cols if c in df.columns]
print(f"\n✅ Features used ({len(feature_cols)}): {feature_cols}")

# ── Preprocessing ──────────────────────────────────────────────────────────────
print("\n🔧 Preprocessing...")
df = df.dropna(subset=[target_col])

X = df[feature_cols].copy()
y = df[target_col].copy()

X = X.fillna(X.median())
X["MonthlyIncome"]                        = X["MonthlyIncome"].clip(upper=50000)
X["DebtRatio"]                            = X["DebtRatio"].clip(upper=5)
X["RevolvingUtilizationOfUnsecuredLines"] = X["RevolvingUtilizationOfUnsecuredLines"].clip(upper=2)

print(f"   X shape: {X.shape}")
print(f"   y distribution: {dict(y.value_counts())}")

# ── Train/Test Split ───────────────────────────────────────────────────────────
print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train: {X_train.shape} | Test: {X_test.shape}")

# ── Scaling ────────────────────────────────────────────────────────────────────
print("\n📏 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ── SMOTE ──────────────────────────────────────────────────────────────────────
print("\n⚖️  Applying SMOTE...")
smote = SMOTE(random_state=42, sampling_strategy=0.4)
X_res, y_res = smote.fit_resample(X_train_scaled, y_train)
print(f"   After SMOTE: {dict(pd.Series(y_res).value_counts())}")

# ── Class Weight ───────────────────────────────────────────────────────────────
neg = sum(y_res == 0)
pos = sum(y_res == 1)
scale_pos_weight = neg / pos
print(f"\n⚖️  scale_pos_weight: {scale_pos_weight:.2f}")

# ── Train XGBoost ──────────────────────────────────────────────────────────────
print("\n🚀 Training XGBoost model...")
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=scale_pos_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
)
model.fit(X_res, y_res)
print("   Training complete!")

# ── Best Threshold ─────────────────────────────────────────────────────────────
print("\n🎯 Finding best threshold...")
probs = model.predict_proba(X_test_scaled)[:, 1]

best_threshold = 0.5
best_f1 = 0
for thresh in np.arange(0.05, 0.5, 0.01):
    preds = (probs >= thresh).astype(int)
    f1 = f1_score(y_test, preds, pos_label=1)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = thresh

print(f"   Best threshold: {best_threshold:.2f} (F1: {best_f1:.3f})")

# ── Evaluation ─────────────────────────────────────────────────────────────────
print("\n📊 Model Evaluation:")
y_pred = (probs >= best_threshold).astype(int)
print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))

# ── Save with protocol=2 ───────────────────────────────────────────────────────
print("\n💾 Saving models with protocol=2...")
os.makedirs("models", exist_ok=True)

joblib.dump(model,          "models/model.pkl",     protocol=2)
joblib.dump(scaler,         "models/scaler.pkl",    protocol=2)
joblib.dump(best_threshold, "models/threshold.pkl", protocol=2)

for fname in ["models/model.pkl", "models/scaler.pkl", "models/threshold.pkl"]:
    size = os.path.getsize(fname)
    print(f"✅ {fname:30s} → {size/1024:.1f} KB  (protocol=2)")

print("\n" + "=" * 55)
print("🎉 Done! Ab ye commands run karo:")
print("=" * 55)
print("   git add models/")
print('   git commit -m "Fix: retrain pkl protocol=2 for Python 3.10"')
print("   git push origin main --force")
print("=" * 55)