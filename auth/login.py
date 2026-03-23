# ═════════════════════════════════════════════════════════════════════════════
# Authentication Module - User Login Verification
# ═════════════════════════════════════════════════════════════════════════════

"""
User authentication and login verification module.
Handles credential verification against the user database.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3


# ═════════════════════════════════════════════════════════════════════════════
# LOGIN VERIFICATION
# ═════════════════════════════════════════════════════════════════════════════

def verify_login(username: str, password: str) -> dict | None:
    """
    Verify user credentials against database.
    
    Args:
        username (str): User's username
        password (str): User's password
        
    Returns:
        dict: User info if credentials valid, None otherwise
            Contains: id, username, role, full_name
        None: If credentials are invalid
    """
    conn = sqlite3.connect("credit_predictions.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, role, full_name 
        FROM users 
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "full_name": user[3]
        }
    return None