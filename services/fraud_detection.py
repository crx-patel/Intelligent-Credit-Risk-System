import joblib
import numpy as np
import pandas as pd
import os

# Load fraud model
_fraud_model      = None
_fraud_scaler     = None
_fraud_thresholds = None


def _load_models():
    global _fraud_model, _fraud_scaler, _fraud_thresholds
    if _fraud_model is None:
        _fraud_model      = joblib.load("models/fraud_model.pkl")
        _fraud_scaler     = joblib.load("models/fraud_scaler.pkl")
        _fraud_thresholds = joblib.load("models/fraud_thresholds.pkl")


def _build_sample(data: dict) -> pd.DataFrame:
    return pd.DataFrame({
        "RevolvingUtilizationOfUnsecuredLines": [data.get("RevolvingUtilizationOfUnsecuredLines", 0)],
        "age":                                  [data.get("age", 30)],
        "NumberOfTime30-59DaysPastDueNotWorse": [data.get("late_30", 0)],
        "DebtRatio":                            [data.get("DebtRatio", 0)],
        "MonthlyIncome":                        [data.get("MonthlyIncome", 0)],
        "NumberOfOpenCreditLinesAndLoans":      [data.get("open_loans", 5)],
        "NumberOfTimes90DaysLate":              [data.get("late_90", 0)],
        "NumberRealEstateLoansOrLines":         [data.get("real_estate_loans", 1)],
        "NumberOfTime60-89DaysPastDueNotWorse": [data.get("late_60", 0)],
        "NumberOfDependents":                   [data.get("dependents", 1)],
    })


def detect_fraud(data: dict) -> str:
    """
    Detect fraud using Isolation Forest ML model.
    Returns: "Possible Fraud" / "Suspicious Applicant" / "No Fraud Detected"
    """
    try:
        _load_models()

        sample        = _build_sample(data)
        sample_scaled = _fraud_scaler.transform(sample)

        # Get anomaly score (lower = more anomalous)
        score = _fraud_model.decision_function(sample_scaled)[0]

        if score <= _fraud_thresholds["fraud"]:
            return "Possible Fraud"
        elif score <= _fraud_thresholds["suspicious"]:
            return "Suspicious Applicant"
        else:
            return "No Fraud Detected"

    except Exception:
        # Fallback to rule-based if model not found
        return _rule_based_fraud(data)


def detect_fraud_detailed(data: dict) -> dict:
    """
    Returns detailed fraud analysis for employee dashboard.
    """
    try:
        _load_models()

        sample        = _build_sample(data)
        sample_scaled = _fraud_scaler.transform(sample)

        score      = _fraud_model.decision_function(sample_scaled)[0]
        prediction = _fraud_model.predict(sample_scaled)[0]

        # Normalize score to 0-100 (higher = more suspicious)
        # Decision function: more negative = more anomalous
        fraud_probability = max(0, min(100, (-score + 0.5) * 100))

        status = detect_fraud(data)

        return {
            "status":      status,
            "score":       round(fraud_probability, 1),
            "raw_score":   round(float(score), 4),
            "is_anomaly":  prediction == -1,
        }

    except Exception as e:
        status = _rule_based_fraud(data)
        return {
            "status":     status,
            "score":      50.0,
            "raw_score":  0.0,
            "is_anomaly": False,
        }


def _rule_based_fraud(data: dict) -> str:
    """Fallback rule-based fraud detection."""
    monthly_income = data.get("MonthlyIncome", 0)
    debt_ratio     = data.get("DebtRatio", 0)
    credit_util    = data.get("RevolvingUtilizationOfUnsecuredLines", 0)
    late_30        = data.get("late_30", 0)
    late_90        = data.get("late_90", 0)

    fraud_score = 0
    if monthly_income <= 0:  fraud_score += 3
    if debt_ratio > 5:       fraud_score += 2
    if credit_util > 1:      fraud_score += 2
    if late_90 >= 3:         fraud_score += 2
    if late_30 >= 5:         fraud_score += 1

    if fraud_score >= 5:   return "Possible Fraud"
    elif fraud_score >= 2: return "Suspicious Applicant"
    else:                  return "No Fraud Detected"