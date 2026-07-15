import os
from flask import Flask, redirect, url_for, session
from config import Config
from models.db import init_db, query_db
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Register blueprint routes
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    """
    Landing index page. Redirects to dashboards if logged in,
    otherwise redirects to login page.
    """
    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@app.context_processor
def inject_unread_notifications_count():
    """
    Global context processor to inject current unread notifications
    count for students on all pages.
    """
    if 'user_id' in session and session.get('user_type') == 'student':
        student_id = session['user_id']
        try:
            unread_notifs = query_db("""
                SELECT COUNT(*) as count FROM Notifications 
                WHERE StudentID = %s AND (IsRead = FALSE OR IsRead = 0)
            """, (student_id,), one=True)
            count = unread_notifs['count'] if unread_notifs else 0
            session['unread_count'] = count
            return dict(unread_count=count)
        except Exception:
            return dict(unread_count=0)
    return dict(unread_count=0)

# Create folders for uploads on startup
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    # Automatically initialize database schema and seed records
    init_db()
    
    # Run the web development server
    print("\n-----------------------------------------------------------")
    print("Digital Complaint Management System (ShaktiCMS) Started.")
    print("Open http://127.0.0.1:5000 in your browser to view the system.")
    print("-----------------------------------------------------------\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
