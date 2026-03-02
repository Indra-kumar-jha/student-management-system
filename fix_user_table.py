import sqlite3

conn = sqlite3.connect('database/students.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN student_id INTEGER")
    print("✅ student_id column added to users table.")
except Exception as e:
    print("⚠️", e)

conn.commit()
conn.close()
