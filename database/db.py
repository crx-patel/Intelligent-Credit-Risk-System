# ═════════════════════════════════════════════════════════════════════════════
# Database Module - Prediction Storage
# ═════════════════════════════════════════════════════════════════════════════

"""
Database operations for storing credit risk predictions.
Handles prediction logging and data persistence.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3
from datetime import datetime


# ═════════════════════════════════════════════════════════════════════════════
# PREDICTION STORAGE
# ═════════════════════════════════════════════════════════════════════════════

def save_prediction(data: dict, risk: str, fraud: str) -> None:
    """
    Save credit risk prediction to database.
    
    Args:
        data (dict): Customer application data with keys:
            - age, MonthlyIncome, DebtRatio, RevolvingUtilizationOfUnsecuredLines
        risk (str): Risk classification (High Risk, Medium Risk, Low Risk)
        fraud (str): Fraud detection result (Possible Fraud, Suspicious, No Fraud)
    """
    conn = sqlite3.connect("credit_predictions.db")
    cursor = conn.cursor()

    # Create predictions table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        MonthlyIncome REAL,
        DebtRatio REAL,
        RevolvingUtilizationOfUnsecuredLines REAL,
        risk TEXT,
        fraud TEXT,
        timestamp TEXT
    )
    """)

    # Extract values from input data
    age = data.get("age", 0)
    income = data.get("MonthlyIncome", 0)
    debt_ratio = data.get("DebtRatio", 0)
    credit_util = data.get("RevolvingUtilizationOfUnsecuredLines", 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert prediction record
    cursor.execute("""
    INSERT INTO predictions 
    (age, MonthlyIncome, DebtRatio, RevolvingUtilizationOfUnsecuredLines, risk, fraud, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        age,
        income,
        debt_ratio,
        credit_util,
        risk,
        fraud,
        timestamp
    ))

    conn.commit()
    conn.close()