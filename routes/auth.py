from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models.db import query_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to correct dashboard
    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
        
    if request.method == 'POST':
        role = request.form.get('role') # 'student' or 'admin'
        
        if role == 'student':
            email = request.form.get('email')
            password = request.form.get('password')
            
            student = query_db("SELECT * FROM Students WHERE Email = %s", (email,), one=True)
            if student and check_password_hash(student['Password'], password):
                session['user_id'] = student['StudentID']
                session['user_type'] = 'student'
                session['user_name'] = student['Name']
                session['user_email'] = student['Email']
                flash(f"Welcome back, {student['Name']}!", "success")
                return redirect(url_for('student.dashboard'))
            else:
                flash("Invalid email or password. Please try again.", "danger")
                
        elif role == 'admin':
            username = request.form.get('username')
            password = request.form.get('password')
            
            admin = query_db("SELECT * FROM Admins WHERE Username = %s", (username,), one=True)
            if admin and check_password_hash(admin['Password'], password):
                session['user_id'] = admin['AdminID']
                session['user_type'] = 'admin'
                session['user_name'] = admin['Username']
                flash(f"Logged in successfully as Admin '{admin['Username']}'.", "success")
                return redirect(url_for('admin.dashboard'))
            else:
                flash("Invalid administrative credentials.", "danger")
                
    return render_template('login.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    department = request.form.get('department')
    password = request.form.get('password')
    
    if not name or not email or not department or not password:
        flash("All registration fields are required.", "danger")
        return redirect(url_for('auth.login'))
        
    # Check if student exists
    existing = query_db("SELECT * FROM Students WHERE Email = %s", (email,), one=True)
    if existing:
        flash("An account with this email already exists.", "danger")
        return redirect(url_for('auth.login'))
        
    hashed_pwd = generate_password_hash(password)
    try:
        query_db("INSERT INTO Students (Name, Email, Department, Password) VALUES (%s, %s, %s, %s);", 
                 (name, email, department, hashed_pwd), commit=True)
        flash("Registration successful! You can now log in.", "success")
    except Exception as e:
        print(f"Registration DB Error: {e}")
        flash("Database error during registration.", "danger")
        
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
