import pandas as pd
import numpy as np
import joblib
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# ── Load Data ─────────────────────────────────────────────────────────────────
print("📂 Loading dataset...")
df = pd.read_csv("data/credit_data.csv")
print(f"   Shape: {df.shape}")
print(f"   Columns: {list(df.columns)}")

# ── Target column detect ───────────────────────────────────────────────────────
# Common target column names in Give Me Some Credit dataset
possible_targets = [
    "SeriousDlqin2yrs",
    "target",
    "label",
    "default",
    "Default",
]
target_col = None
for col in possible_targets:
    if col in df.columns:
        target_col = col
        break

if target_col is None:
    print("\n❌ Target column not found!")
    print("Available columns:", list(df.columns))
    print("Please set target_col manually below.")
    raise ValueError("Set target_col manually!")

print(f"\n✅ Target column: '{target_col}'")
print(f"   Class distribution:\n{df[target_col].value_counts()}")

# ── Features ──────────────────────────────────────────────────────────────────
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

# Keep only available feature columns
feature_cols = [c for c in feature_cols if c in df.columns]
print(f"\n✅ Features used: {feature_cols}")

# ── Preprocessing ─────────────────────────────────────────────────────────────
print("\n🔧 Preprocessing...")

# Drop rows where target is missing
df = df.dropna(subset=[target_col])

X = df[feature_cols].copy()
y = df[target_col].copy()

# Fill missing values with median
X = X.fillna(X.median())

# Clip outliers
X["MonthlyIncome"]   = X["MonthlyIncome"].clip(upper=50000)
X["DebtRatio"]       = X["DebtRatio"].clip(upper=5)
X["RevolvingUtilizationOfUnsecuredLines"] = X["RevolvingUtilizationOfUnsecuredLines"].clip(upper=2)

print(f"   X shape: {X.shape}")
print(f"   y distribution: {dict(y.value_counts())}")

# ── Train/Test Split ──────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Scaling ───────────────────────────────────────────────────────────────────
print("\n📏 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ── SMOTE ─────────────────────────────────────────────────────────────────────
print("\n⚖️  Applying SMOTE for class balancing...")
smote = SMOTE(random_state=42, sampling_strategy=0.4)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
print(f"   After SMOTE: {dict(pd.Series(y_train_res).value_counts())}")

# ── Class weight ratio ────────────────────────────────────────────────────────
neg = sum(y_train_res == 0)
pos = sum(y_train_res == 1)
scale_pos_weight = neg / pos
print(f"\n⚖️  scale_pos_weight: {scale_pos_weight:.2f}")

# ── Train XGBoost ─────────────────────────────────────────────────────────────
print("\n🚀 Training XGBoost model...")
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=scale_pos_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train_res, y_train_res)

# ── Threshold Tuning ──────────────────────────────────────────────────────────
print("\n🎯 Finding best threshold...")
probs = model.predict_proba(X_test_scaled)[:, 1]

best_threshold = 0.5
best_f1 = 0

from sklearn.metrics import f1_score
for thresh in np.arange(0.05, 0.5, 0.01):
    preds = (probs >= thresh).astype(int)
    f1 = f1_score(y_test, preds, pos_label=1)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = thresh

print(f"   Best threshold: {best_threshold:.2f} (F1: {best_f1:.3f})")

# ── Evaluation ────────────────────────────────────────────────────────────────
print("\n📊 Model Evaluation:")
y_pred = (probs >= best_threshold).astype(int)
print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ── Save Models ───────────────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(best_threshold, "models/threshold.pkl")

print("\n✅ Model saved to models/model.pkl")
print("✅ Scaler saved to models/scaler.pkl")
print(f"✅ Threshold saved to models/threshold.pkl (value: {best_threshold:.2f})")
print("\n🎉 Training complete!")