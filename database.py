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
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")