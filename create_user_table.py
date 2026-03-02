import sqlite3

conn = sqlite3.connect('database/students.db')
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    student_id INTEGER
)
''')

conn.commit()
conn.close()
print("✅ Users table ready.")
