# # ═════════════════════════════════════════════════════════════════════════════
# # Database Module - Prediction Storage
# # ═════════════════════════════════════════════════════════════════════════════

# """
# Database operations for storing credit risk predictions.
# Handles prediction logging and data persistence.
# """

# # Standard Library Imports
# # ─────────────────────────────────────────────────────────────────────────────
# import sqlite3
# from datetime import datetime


# # ═════════════════════════════════════════════════════════════════════════════
# # PREDICTION STORAGE
# # ═════════════════════════════════════════════════════════════════════════════

# def save_prediction(data: dict, risk: str, fraud: str) -> None:
#     """
#     Save credit risk prediction to database.
    
#     Args:
#         data (dict): Customer application data with keys:
#             - age, MonthlyIncome, DebtRatio, RevolvingUtilizationOfUnsecuredLines
#         risk (str): Risk classification (High Risk, Medium Risk, Low Risk)
#         fraud (str): Fraud detection result (Possible Fraud, Suspicious, No Fraud)
#     """
#     conn = sqlite3.connect("credit_predictions.db")
#     cursor = conn.cursor()

#     # Create predictions table if not exists
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS predictions (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         age INTEGER,
#         MonthlyIncome REAL,
#         DebtRatio REAL,
#         RevolvingUtilizationOfUnsecuredLines REAL,
#         risk TEXT,
#         fraud TEXT,
#         timestamp TEXT
#     )
#     """)

#     # Extract values from input data
#     age = data.get("age", 0)
#     income = data.get("MonthlyIncome", 0)
#     debt_ratio = data.get("DebtRatio", 0)
#     credit_util = data.get("RevolvingUtilizationOfUnsecuredLines", 0)
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Insert prediction record
#     cursor.execute("""
#     INSERT INTO predictions 
#     (age, MonthlyIncome, DebtRatio, RevolvingUtilizationOfUnsecuredLines, risk, fraud, timestamp)
#     VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (
#         age,
#         income,
#         debt_ratio,
#         credit_util,
#         risk,
#         fraud,
#         timestamp
#     ))

#     conn.commit()
#     conn.close()


# ═════════════════════════════════════════════════════════════════════════════
# Database Module - Prediction Storage (PostgreSQL Version)
# ═════════════════════════════════════════════════════════════════════════════

"""
Database operations for storing credit risk predictions.
Handles prediction logging and data persistence.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════════════
# Database Module - PostgreSQL (Render)
# ═════════════════════════════════════════════════════════════════════════════

import os
import psycopg2


# ═════════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═════════════════════════════════════════════════════════════════════════════

def get_connection():
    """
    Connect to PostgreSQL using Render DATABASE_URL
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("❌ DATABASE_URL not set in environment variables")

    return psycopg2.connect(
        database_url,
        sslmode="require"
    )


# ═════════════════════════════════════════════════════════════════════════════
# TABLE INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        age INTEGER,
        MonthlyIncome DOUBLE PRECISION,
        DebtRatio DOUBLE PRECISION,
        RevolvingUtilizationOfUnsecuredLines DOUBLE PRECISION,
        risk TEXT,
        fraud TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        role TEXT
    )
    """)

    # default users
    cursor.execute("""
    INSERT INTO users (username, password, full_name, role)
    VALUES 
    ('admin', 'admin123', 'Admin User', 'employee'),
    ('customer1', 'cust123', 'Customer One', 'customer')
    ON CONFLICT (username) DO NOTHING
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ═════════════════════════════════════════════════════════════════════════════
# SAVE PREDICTION
# ═════════════════════════════════════════════════════════════════════════════

def save_prediction(data: dict, risk: str, fraud: str) -> None:
    """
    Save prediction data into PostgreSQL
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Extract values safely
    age = data.get("age", 0)
    income = data.get("MonthlyIncome", 0)
    debt_ratio = data.get("DebtRatio", 0)
    credit_util = data.get("RevolvingUtilizationOfUnsecuredLines", 0)

    cursor.execute("""
    INSERT INTO predictions 
    (age, MonthlyIncome, DebtRatio, RevolvingUtilizationOfUnsecuredLines, risk, fraud)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        age,
        income,
        debt_ratio,
        credit_util,
        risk,
        fraud
    ))

    conn.commit()
    cursor.close()
    conn.close()