import sqlite3

conn = sqlite3.connect("tickets.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE tickets
ADD COLUMN employee_email TEXT
""")

conn.commit()
conn.close()

print("Email column added!")