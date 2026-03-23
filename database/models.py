# ═════════════════════════════════════════════════════════════════════════════
# Database Models - Database Initialization
# ═════════════════════════════════════════════════════════════════════════════

"""
Database initialization and user table management.
Sets up SQLite database with default user accounts.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3


# ═════════════════════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

def init_db():
    """
    Initialize the credit predictions database.
    Creates users table and inserts default users if not already present.
    """
    conn = sqlite3.connect("credit_predictions.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        created_at TEXT
    )
    """)

    # Insert default users
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
    VALUES 
        ('admin', 'admin123', 'employee', 'Bank Manager', '2026-01-01'),
        ('customer1', 'cust123', 'customer', 'Rahul Sharma', '2026-01-01')
    """)

    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")


if __name__ == "__main__":
    init_db()

# python database/models.py