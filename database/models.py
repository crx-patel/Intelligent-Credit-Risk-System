import sqlite3

def init_db():

    conn = sqlite3.connect("credit_predictions.db")
    cursor = conn.cursor()

    # Users table
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

    # Default users insert
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
    VALUES 
        ('admin', 'admin123', 'employee', 'Bank Manager', '2026-01-01'),
        ('customer1', 'cust123', 'customer', 'Rahul Sharma', '2026-01-01')
    """)

    conn.commit()
    conn.close()
    print("Database initialized!")

if __name__ == "__main__":
    init_db()






# python database/models.py