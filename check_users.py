import sqlite3

conn = sqlite3.connect('database/students.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print("🔐 Existing users:")
for row in rows:
    print(row)

conn.close()
