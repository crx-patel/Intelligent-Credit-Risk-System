# ═════════════════════════════════════════════════════════════════════════════
# Risk Prediction Service - XGBoost Credit Risk Model
# ═════════════════════════════════════════════════════════════════════════════

"""
Credit risk prediction service using XGBoost model.
Provides risk scoring and classification for customer credit assessments.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
import os

# Third-Party Imports
# ─────────────────────────────────────────────────────────────────────────────
import joblib
import numpy as np
import pandas as pd


# ═════════════════════════════════════════════════════════════════════════════
# MODEL LOADING & CACHING  (lazy load — no crash at import time)
# ═════════════════════════════════════════════════════════════════════════════

_model   = None
_scaler  = None
_threshold = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load("models/model.pkl")
    return _model


def get_scaler():
    global _scaler
    if _scaler is None:
        _scaler = joblib.load("models/scaler.pkl")
    return _scaler


def get_threshold():
    global _threshold
    if _threshold is None:
        path = "models/threshold.pkl"
        _threshold = joblib.load(path) if os.path.exists(path) else 0.5
    return _threshold


# ═════════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═════════════════════════════════════════════════════════════════════════════

def _build_sample(data: dict) -> pd.DataFrame:
    """
    Build feature DataFrame from customer data.

    Args:
        data (dict): Customer financial data

    Returns:
        pd.DataFrame: Feature matrix with expected columns
    """
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


# ═════════════════════════════════════════════════════════════════════════════
# RISK CLASSIFICATION
# ═════════════════════════════════════════════════════════════════════════════

def _get_label(prob: float) -> str:
    """
    Convert probability to risk classification.

    Args:
        prob (float): Risk probability (0-1)

    Returns:
        str: Risk classification (Low/Medium/High)
    """
    score = prob * 100
    if score < 8:
        return "Low Risk"
    elif score < 14:
        return "Medium Risk"
    else:
        return "High Risk"


# ═════════════════════════════════════════════════════════════════════════════
# PREDICTION FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def predict_risk(data: dict) -> str:
    """
    Predict risk classification for customer.

    Args:
        data (dict): Customer financial data

    Returns:
        str: Risk classification (Low/Medium/High Risk)
    """
    model         = get_model()
    scaler        = get_scaler()
    sample        = _build_sample(data)
    sample_scaled = scaler.transform(sample)
    prob          = model.predict_proba(sample_scaled)[:, 1][0]
    return _get_label(prob)


def predict_risk_score(data: dict) -> tuple:
    """
    Predict risk score with classification.

    Args:
        data (dict): Customer financial data

    Returns:
        tuple: (display_score, risk_label)
            - display_score (float): Risk percentage (capped at 20%)
            - risk_label (str): Risk classification
    """
    model         = get_model()
    scaler        = get_scaler()
    sample        = _build_sample(data)
    sample_scaled = scaler.transform(sample)
    prob          = model.predict_proba(sample_scaled)[:, 1][0]
    risk_score    = round(prob * 100, 2)
    display_score = min(risk_score, 20.0)
    label         = _get_label(prob)
    return display_score, label