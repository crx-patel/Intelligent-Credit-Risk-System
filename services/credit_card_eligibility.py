# # ============================================================
# # services/credit_card_eligibility.py
# # ============================================================

# import joblib
# import numpy as np
# import pandas as pd

# # ── Load artifacts once at import time ─────────────────────
# import pickle

# # PEHLE (yeh hata do)
# # _model = joblib.load("models/credit_card_model.pkl")

# # BAAD (yeh lagao)
# with open("models/credit_card_model.pkl", "rb") as f:
#     _model = pickle.load(f)
# _features  = joblib.load("models/credit_card_features.pkl")
# _THRESHOLD = 0.43


# def predict_credit_card_eligibility(data: dict) -> tuple[bool, float, str]:
#     """
#     Parameters
#     ----------
#     data : dict with keys:
#         gender, age, family_status, cnt_children, cnt_fam_members,
#         income_type, amt_income, education_type, housing_type,
#         employment_yrs, owns_car, owns_realty

#     Returns
#     -------
#     eligible   : bool   — True = eligible for credit card
#     prob       : float  — P(default), 0–1
#     risk_label : str    — "Low Risk" / "Medium Risk" / "High Risk"
#     """

#     # ── Build raw feature dict (mirror notebook get_dummies) ───
#     row = {
#         "CNT_CHILDREN":      data["cnt_children"],
#         "AMT_INCOME_TOTAL":  np.log1p(data["amt_income"]),   # log1p — same as notebook
#         "CNT_FAM_MEMBERS":   data["cnt_fam_members"],
#         "AGE":               data["age"],
#         "EMPLOYMENT_YEARS":  data["employment_yrs"],

#         # One-hot encoded columns (drop_first=True → base category omitted)
#         # CODE_GENDER — base = F
#         "CODE_GENDER_M": 1 if data["gender"] == "Male" else 0,

#         # FLAG_OWN_CAR — base = N
#         "FLAG_OWN_CAR_Y": 1 if data["owns_car"] == "Yes" else 0,

#         # FLAG_OWN_REALTY — base = N
#         "FLAG_OWN_REALTY_Y": 1 if data["owns_realty"] == "Yes" else 0,

#         # NAME_INCOME_TYPE — base = Pensioner
#         "NAME_INCOME_TYPE_Working": 1 if data["income_type"] == "Working" else 0,

#         # NAME_EDUCATION_TYPE — base = Higher
#         "NAME_EDUCATION_TYPE_Secondary": 1 if data["education_type"] == "Secondary" else 0,

#         # NAME_HOUSING_TYPE — base = Apartment
#         "NAME_HOUSING_TYPE_House / apartment": 1 if data["housing_type"] == "House / apartment" else 0,
#         "NAME_HOUSING_TYPE_Other":             1 if data["housing_type"] == "Other" else 0,

#         # NAME_FAMILY_STATUS — base = Married
#         "NAME_FAMILY_STATUS_Single": 1 if data["family_status"] == "Single" else 0,
#     }

#     # ── Align to exact training columns (fill any extra with 0) ─
#     df = pd.DataFrame([row])
#     df = df.reindex(columns=_features, fill_value=0)

#     # ── Predict ─────────────────────────────────────────────────
#     prob     = float(_model.predict_proba(df)[0][1])   # P(BAD / default)
#     eligible = prob < _THRESHOLD

#     # ── Risk label ──────────────────────────────────────────────
#     if prob < 0.20:
#         risk_label = "Low Risk"
#     elif prob < 0.43:
#         risk_label = "Medium Risk"
#     else:
#         risk_label = "High Risk"

#     return eligible, prob, risk_label



# ============================================================
# services/credit_card_eligibility.py
# ============================================================

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

# ── Load artifacts once at import time ─────────────────────
_model = XGBClassifier()
_model.load_model("models/credit_card_model.json")
_features  = joblib.load("models/credit_card_features.pkl")
_THRESHOLD = 0.43


def predict_credit_card_eligibility(data: dict) -> tuple[bool, float, str]:

    row = {
        "CNT_CHILDREN":      data["cnt_children"],
        "AMT_INCOME_TOTAL":  np.log1p(data["amt_income"]),
        "CNT_FAM_MEMBERS":   data["cnt_fam_members"],
        "AGE":               data["age"],
        "EMPLOYMENT_YEARS":  data["employment_yrs"],
        "CODE_GENDER_M":     1 if data["gender"] == "Male" else 0,
        "FLAG_OWN_CAR_Y":    1 if data["owns_car"] == "Yes" else 0,
        "FLAG_OWN_REALTY_Y": 1 if data["owns_realty"] == "Yes" else 0,
        "NAME_INCOME_TYPE_Working":           1 if data["income_type"] == "Working" else 0,
        "NAME_EDUCATION_TYPE_Secondary":      1 if data["education_type"] == "Secondary" else 0,
        "NAME_HOUSING_TYPE_House / apartment": 1 if data["housing_type"] == "House / apartment" else 0,
        "NAME_HOUSING_TYPE_Other":            1 if data["housing_type"] == "Other" else 0,
        "NAME_FAMILY_STATUS_Single":          1 if data["family_status"] == "Single" else 0,
    }

    df = pd.DataFrame([row])
    df = df.reindex(columns=_features, fill_value=0)

    prob     = float(_model.predict_proba(df)[0][1])
    eligible = prob < _THRESHOLD

    if prob < 0.20:
        risk_label = "Low Risk"
    elif prob < 0.43:
        risk_label = "Medium Risk"
    else:
        risk_label = "High Risk"

    return eligible, prob, risk_label