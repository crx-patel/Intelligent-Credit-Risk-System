import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

print("📂 Loading dataset...")
df = pd.read_csv("data/credit_data.csv")
print(f"   Shape: {df.shape}")

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

X = df[feature_cols].copy()
X = X.fillna(X.median())

# Clip outliers
X["MonthlyIncome"] = X["MonthlyIncome"].clip(upper=50000)
X["DebtRatio"]     = X["DebtRatio"].clip(upper=5)
X["RevolvingUtilizationOfUnsecuredLines"] = X["RevolvingUtilizationOfUnsecuredLines"].clip(upper=2)

# ── Generate Synthetic Fraud Labels ───────────────────────────────────────────
print("\n🔧 Generating synthetic fraud labels...")

fraud_score = pd.Series(0, index=X.index)

# Rule 1: Income zero or missing
fraud_score += (df["MonthlyIncome"] <= 0).astype(int) * 3

# Rule 2: Extreme debt ratio
fraud_score += (df["DebtRatio"] > 5).astype(int) * 2

# Rule 3: Credit utilization > 1
fraud_score += (df["RevolvingUtilizationOfUnsecuredLines"] > 1).astype(int) * 2

# Rule 4: Many late payments 90 days
fraud_score += (df["NumberOfTimes90DaysLate"] >= 3).astype(int) * 2

# Rule 5: Many late payments 30-59 days
fraud_score += (df["NumberOfTime30-59DaysPastDueNotWorse"] >= 5).astype(int) * 1

# Rule 6: Very high default risk (SeriousDlqin2yrs = 1) + high debt
fraud_score += ((df["SeriousDlqin2yrs"] == 1) & (df["DebtRatio"] > 2)).astype(int) * 2

# Rule 7: Age anomaly
fraud_score += ((df["age"] < 18) | (df["age"] > 100)).astype(int) * 3

# Fraud label: score >= 4 = fraud
y_fraud = (fraud_score >= 4).astype(int)

print(f"   Fraud cases:     {y_fraud.sum()} ({y_fraud.mean()*100:.1f}%)")
print(f"   Non-fraud cases: {(y_fraud==0).sum()} ({(y_fraud==0).mean()*100:.1f}%)")

# ── Scale features ────────────────────────────────────────────────────────────
print("\n📏 Scaling features...")
fraud_scaler = StandardScaler()
X_scaled     = fraud_scaler.fit_transform(X)

# ── Train Isolation Forest ────────────────────────────────────────────────────
print("\n🚀 Training Isolation Forest...")

# contamination = estimated fraud rate
contamination = float(y_fraud.mean())
contamination = max(0.01, min(contamination, 0.5))  # clip between 1%-50%

fraud_model = IsolationForest(
    n_estimators=200,
    contamination=contamination,
    random_state=42,
    n_jobs=-1,
)
fraud_model.fit(X_scaled)

# ── Evaluate ──────────────────────────────────────────────────────────────────
print("\n📊 Evaluating...")
preds_raw = fraud_model.predict(X_scaled)
# IsolationForest: -1 = anomaly (fraud), 1 = normal
y_pred = (preds_raw == -1).astype(int)

print(classification_report(y_fraud, y_pred, target_names=["No Fraud", "Fraud"]))
print("Confusion Matrix:")
print(confusion_matrix(y_fraud, y_pred))

# ── Anomaly score threshold ────────────────────────────────────────────────────
scores = fraud_model.decision_function(X_scaled)
# Lower score = more anomalous
threshold_suspicious = np.percentile(scores, 15)  # bottom 15% = suspicious
threshold_fraud      = np.percentile(scores, 5)   # bottom 5%  = fraud

print(f"\n🎯 Thresholds:")
print(f"   Suspicious threshold: {threshold_suspicious:.4f}")
print(f"   Fraud threshold:      {threshold_fraud:.4f}")

# ── Save Models ───────────────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(fraud_model,        "models/fraud_model.pkl")
joblib.dump(fraud_scaler,       "models/fraud_scaler.pkl")
joblib.dump({
    "suspicious": threshold_suspicious,
    "fraud":      threshold_fraud,
}, "models/fraud_thresholds.pkl")

print("\n✅ fraud_model.pkl saved!")
print("✅ fraud_scaler.pkl saved!")
print("✅ fraud_thresholds.pkl saved!")
print("\n🎉 Fraud Detection Model training complete!")