# ═════════════════════════════════════════════════════════════════════════════
# Authentication Module - User Login Verification (PostgreSQL)
# ═════════════════════════════════════════════════════════════════════════════

"""
User authentication and login verification module.
Handles credential verification against the user database.
"""

# Database Connection
# ─────────────────────────────────────────────────────────────────────────────
from database.db import get_connection


# ═════════════════════════════════════════════════════════════════════════════
# LOGIN VERIFICATION
# ═════════════════════════════════════════════════════════════════════════════

def verify_login(username: str, password: str) -> dict | None:
    """
    Verify user credentials against PostgreSQL database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, role, full_name 
        FROM users 
        WHERE username = %s AND password = %s
    """, (username, password))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "full_name": user[3]
        }

    return None