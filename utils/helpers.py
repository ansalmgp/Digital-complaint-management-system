import os
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models.db import query_db

def student_required(f):
    """
    Decorator to ensure the current session has a student logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'student':
            flash("Please log in as a student to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure the current session has an admin logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash("Please log in as an administrator to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def add_notification(student_id, message):
    """
    Insert a notification for a student in the database.
    """
    query = "INSERT INTO Notifications (StudentID, Message, IsRead, CreatedDate) VALUES (%s, %s, FALSE, CURRENT_TIMESTAMP);"
    query_db(query, (student_id, message), commit=True)

def allowed_file(filename):
    """
    Check if the uploaded file has a valid image extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_uploaded_image(file):
    """
    Saves an uploaded image file with a unique name to prevent naming collisions.
    Returns the relative path under the static folder.
    """
    if not file or file.filename == '':
        return None
        
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Append unique uuid part to ensure filename is unique
        name, ext = os.path.splitext(filename)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        file.save(os.path.join(upload_dir, unique_name))
        return unique_name
        
    return None
