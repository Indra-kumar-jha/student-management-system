import sqlite3
import os

# Ensure the database folder exists
os.makedirs('database', exist_ok=True)

# Connect to database
conn = sqlite3.connect('database/students.db')
cursor = conn.cursor()

# Create students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll TEXT UNIQUE NOT NULL,
    class TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    username TEXT UNIQUE
)
''')

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'student'))
)
''')

# Insert sample users
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
               ('admin', 'admin123', 'admin'))
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
               ('student1', 'student123', 'student'))

conn.commit()
conn.close()

print("✅ Database and tables created successfully.")
