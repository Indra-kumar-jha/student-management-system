from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random
import string


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # already should be there
app.config['SESSION_PERMANENT'] = False


# 🔌 Connect to DB function
def get_db_connection():
    conn = sqlite3.connect('database/students.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🏠 Home route -> redirects to index
@app.route('/')
def index():
    return render_template('index.html')


# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))
    return render_template('dashboard.html')


# ➕ Add student (GET = form, POST = insert to DB)
# Helper functions
def generate_username(name):
    return name.lower().replace(" ", "") + str(random.randint(100, 999))

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # your existing POST logic
        name = request.form['name']
        roll = request.form['roll']
        class_name = request.form['class']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        username = generate_username(name)
        password = generate_password()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO students (name, roll, class, email, phone, address, username)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, roll, class_name, email, phone, address, username))

            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, 'student')
            ''', (username, password))

            conn.commit()
           
        except Exception as e:
            conn.rollback()
            flash(f"❌ Error adding student: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect(url_for('view_students', username=username, password=password))


    # For GET request → show the form
    return render_template('add_student.html')
   

   

        
        

# 📋 View all students

@app.route('/students')
def view_students():
    # 🔐 Only allow if admin is logged in
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))

    # ✅ Get credentials from URL if present
    username = request.args.get('username')
    password = request.args.get('password')

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return render_template('view_students.html', students=students, username=username, password=password)


# ✏️ Edit student (load form with data)
@app.route('/edit/<int:student_id>', methods=['GET'])
def edit_student(student_id):
    # 🔐 Only allow admin to access this route
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    return render_template('edit_student.html', student=student)


# 🔁 Update student (from edit form)
@app.route('/update/<int:student_id>', methods=['POST'])
def update_student(student_id):
    # 🔐 Only allow admin to perform update
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))

    name = request.form['name']
    roll = request.form['roll']
    class_name = request.form['class']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']

    conn = get_db_connection()
    conn.execute('''
        UPDATE students
        SET name = ?, roll = ?, class = ?, email = ?, phone = ?, address = ?
        WHERE id = ?
    ''', (name, roll, class_name, email, phone, address, student_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_students'))


# ❌ Delete student
@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    # 🔐 Only allow admin to delete
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))

    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_students'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'student')  # Default is student

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', (username, password, role))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']

            if user['role'] == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('student_profile'))

        else:
            return render_template('login.html', error='Invalid username or password', role=role)

    return render_template('login.html', role=role)



    


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/student')
def student_profile():
    if 'username' not in session or session['role'] != 'student':
        return "Access Denied", 403

    username = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE username = ?", (username,))
    student = cursor.fetchone()
    conn.close()

    if student:
        return render_template('student_profile.html', student=student)
    else:
        return "No student record found.", 404
    
@app.route('/student/profile')
def view_student_profile():
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE username = ?", (session['username'],)).fetchone()
    conn.close()

    return render_template('student_profile.html', student=student)




@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    role = session['role']

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check current password
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, current_password))
        user = cursor.fetchone()

        if user:
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
            conn.commit()
            conn.close()
            return render_template('change_password.html', success="✅ Password updated successfully")
        else:
            conn.close()
            return render_template('change_password.html', error="❌ Incorrect current password")

    return render_template('change_password.html')

   




# ▶️ Run the app
if __name__ == '__main__':
    app.run(debug=True)
