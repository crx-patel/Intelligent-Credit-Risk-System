# ═════════════════════════════════════════════════════════════════════════════
# Credit Card Eligibility Service - XGBoost Classification
# ═════════════════════════════════════════════════════════════════════════════

"""
Credit card eligibility prediction service.
Determines card eligibility and risk classification using XGBoost model.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────

# Third-Party Imports
# ─────────────────────────────────────────────────────────────────────────────
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier


# ═════════════════════════════════════════════════════════════════════════════
# MODEL LOADING & ARTIFACTS
# ═════════════════════════════════════════════════════════════════════════════

# Load XGBoost model
_model = XGBClassifier()
_model.load_model("models/credit_card_model.json")

# Load feature list and threshold
_features = joblib.load("models/credit_card_features.pkl")
_THRESHOLD = 0.43


# ═════════════════════════════════════════════════════════════════════════════
# CREDIT CARD ELIGIBILITY PREDICTION
# ═════════════════════════════════════════════════════════════════════════════

def predict_credit_card_eligibility(data: dict) -> tuple:
    """
    Predict credit card eligibility for applicant.
    
    Args:
        data (dict): Customer profile with keys:
            - gender, age, family_status, cnt_children, cnt_fam_members
            - income_type, amt_income, education_type, housing_type
            - employment_yrs, owns_car, owns_realty
    
    Returns:
        tuple: (eligible, prob, risk_label)
            - eligible (bool): True if eligible for credit card
            - prob (float): Default probability (0-1)
            - risk_label (str): Risk classification
    """
    # Build feature dictionary with one-hot encoding
    row = {
        "CNT_CHILDREN":                     data["cnt_children"],
        "AMT_INCOME_TOTAL":                 np.log1p(data["amt_income"]),
        "CNT_FAM_MEMBERS":                  data["cnt_fam_members"],
        "AGE":                              data["age"],
        "EMPLOYMENT_YEARS":                 data["employment_yrs"],
        "CODE_GENDER_M":                    1 if data["gender"] == "Male" else 0,
        "FLAG_OWN_CAR_Y":                   1 if data["owns_car"] == "Yes" else 0,
        "FLAG_OWN_REALTY_Y":                1 if data["owns_realty"] == "Yes" else 0,
        "NAME_INCOME_TYPE_Working":         1 if data["income_type"] == "Working" else 0,
        "NAME_EDUCATION_TYPE_Secondary":    1 if data["education_type"] == "Secondary" else 0,
        "NAME_HOUSING_TYPE_House / apartment": 1 if data["housing_type"] == "House / apartment" else 0,
        "NAME_HOUSING_TYPE_Other":          1 if data["housing_type"] == "Other" else 0,
        "NAME_FAMILY_STATUS_Single":        1 if data["family_status"] == "Single" else 0,
    }

    # Create DataFrame and align with training features
    df = pd.DataFrame([row])
    df = df.reindex(columns=_features, fill_value=0)

    # Predict default probability
    prob = float(_model.predict_proba(df)[0][1])
    eligible = prob < _THRESHOLD

    # Classify risk level
    if prob < 0.20:
        risk_label = "Low Risk"
    elif prob < 0.43:
        risk_label = "Medium Risk"
    else:
        risk_label = "High Risk"

    return eligible, prob, risk_label