import sqlite3

conn = sqlite3.connect("tickets.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT,
    employee_id TEXT,
    department TEXT,
    employee_email TEXT,
    ticket_text TEXT,
    category TEXT,
    priority TEXT,
    status TEXT,
    created_at DATE
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.getcwd(), "tickets.db")
    conn = sqlite3.connect(db_path)
    return conn