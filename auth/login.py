import sqlite3

def verify_login(username, password):

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