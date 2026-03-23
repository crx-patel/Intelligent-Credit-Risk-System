
import joblib
import numpy as np
import pandas as pd
import os

# ── Lazy loader for XGBoost model ────────────────────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        _model = joblib.load("models/model.pkl")
    return _model

scaler = joblib.load("models/scaler.pkl")

threshold_path = "models/threshold.pkl"
THRESHOLD = joblib.load(threshold_path) if os.path.exists(threshold_path) else 0.5


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


def _get_label(prob: float) -> str:
    score = prob * 100
    if score < 8:
        return "Low Risk"
    elif score < 14:
        return "Medium Risk"
    else:
        return "High Risk"


def predict_risk(data: dict) -> str:
    model         = get_model()          # ← fix: get_model() call karo
    sample        = _build_sample(data)
    sample_scaled = scaler.transform(sample)
    prob          = model.predict_proba(sample_scaled)[:, 1][0]
    return _get_label(prob)


def predict_risk_score(data: dict) -> tuple:
    model         = get_model()          # ← fix: get_model() call karo
    sample        = _build_sample(data)
    sample_scaled = scaler.transform(sample)
    prob          = model.predict_proba(sample_scaled)[:, 1][0]
    risk_score    = round(prob * 100, 2)
    display_score = min(risk_score, 20.0)
    label         = _get_label(prob)
    return display_score, label