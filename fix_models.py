"""
fix_models.py
─────────────
Re-saves all .pkl files with protocol=2 for universal compatibility.
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
from sklearn.metrics import f1_score

print("=" * 50)
print("🔧 fix_models.py — Rebuilding all pkl files")
print(f"   NumPy:   {np.__version__}")
print(f"   Joblib:  {joblib.__version__}")
print("=" * 50)

# ── Load Data ──────────────────────────────────────────────────────────────────
print("\n📂 Loading data...")
df = pd.read_csv("data/credit_data.csv")
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# ── Target column ──────────────────────────────────────────────────────────────
possible_targets = ["SeriousDlqin2yrs", "target", "label", "default", "Default"]
target_col = next((c for c in possible_targets if c in df.columns), None)
if target_col is None:
    raise ValueError(f"Target column not found! Columns: {list(df.columns)}")
print(f"   Target: {target_col}")

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

# ── Preprocessing ──────────────────────────────────────────────────────────────
df = df.dropna(subset=[target_col])
X = df[feature_cols].copy()
y = df[target_col].copy()

X = X.fillna(X.median())
X["MonthlyIncome"]   = X["MonthlyIncome"].clip(upper=50000)
X["DebtRatio"]       = X["DebtRatio"].clip(upper=5)
X["RevolvingUtilizationOfUnsecuredLines"] = X["RevolvingUtilizationOfUnsecuredLines"].clip(upper=2)

# ── Split + Scale ──────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ── SMOTE ──────────────────────────────────────────────────────────────────────
smote = SMOTE(random_state=42, sampling_strategy=0.4)
X_res, y_res = smote.fit_resample(X_train_scaled, y_train)

# ── Train ──────────────────────────────────────────────────────────────────────
neg = sum(y_res == 0)
pos = sum(y_res == 1)
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=neg / pos,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
)
print("\n🚀 Training model...")
model.fit(X_res, y_res)

# ── Best Threshold ─────────────────────────────────────────────────────────────
probs = model.predict_proba(X_test_scaled)[:, 1]
best_threshold, best_f1 = 0.5, 0
for thresh in np.arange(0.05, 0.5, 0.01):
    preds = (probs >= thresh).astype(int)
    f1 = f1_score(y_test, preds, pos_label=1)
    if f1 > best_f1:
        best_f1, best_threshold = f1, thresh
print(f"   Best threshold: {best_threshold:.2f} (F1: {best_f1:.3f})")

# ── Save with protocol=2 ───────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(model,          "models/model.pkl",     protocol=2)
joblib.dump(scaler,         "models/scaler.pkl",    protocol=2)
joblib.dump(best_threshold, "models/threshold.pkl", protocol=2)

print("\n✅ models/model.pkl     → saved (protocol=2)")
print("✅ models/scaler.pkl    → saved (protocol=2)")
print(f"✅ models/threshold.pkl → saved (protocol=2) value={best_threshold:.2f}")
print("\n🎉 Done! Ab ye karo:")
print("   git add models/")
print('   git commit -m "Fix: retrain pkl protocol=2"')
print("   git push origin main --force")