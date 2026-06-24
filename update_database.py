import sqlite3

conn = sqlite3.connect("tickets.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE tickets
        ADD COLUMN created_at TEXT
    """)

    cursor.execute("""
        UPDATE tickets
        SET created_at = date('now')
        WHERE created_at IS NULL
    """)

    conn.commit()

    print("created_at column added and Database updated successfully!")

except Exception as e:
    print(e)

finally:
    conn.close()