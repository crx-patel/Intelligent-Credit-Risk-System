


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

# def get_connection():
#     """
#     Connect to PostgreSQL using Render DATABASE_URL
#     """
#     database_url = os.getenv("DATABASE_URL")

#     if not database_url:
#         raise ValueError("❌ DATABASE_URL not set in environment variables")

#     return psycopg2.connect(
#         database_url,
#         sslmode="require"
#     )
import os

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(database_url, sslmode="require")


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
    
    # ═════════════════════════════════════════════════════════════════════════════
# USER FUNCTIONS (SIGNUP + LOGIN)
# ═════════════════════════════════════════════════════════════════════════════

def create_user(username, password, full_name, role="customer"):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (%s, %s, %s, %s)
        """, (username, password, full_name, role))

        conn.commit()
        return True

    except Exception as e:
        print("❌ Error creating user:", e)
        return False

    finally:
        cursor.close()
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE username = %s
    """, (username,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user