from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from models.db import query_db
from utils.helpers import student_required, save_uploaded_image, add_notification

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session['user_id']
    
    # Query statistics
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN Status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN Status = 'Under Review' THEN 1 ELSE 0 END) as under_review,
            SUM(CASE WHEN Status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM Complaints 
        WHERE StudentID = %s
    """, (student_id,), one=True)
    
    # In case there are no complaints, SUM returns None. We clean it up:
    stats_cleaned = {
        'total': stats['total'] if stats else 0,
        'pending': stats['pending'] if stats and stats['pending'] else 0,
        'under_review': stats['under_review'] if stats and stats['under_review'] else 0,
        'in_progress': stats['in_progress'] if stats and stats['in_progress'] else 0,
        'resolved': stats['resolved'] if stats and stats['resolved'] else 0,
        'rejected': stats['rejected'] if stats and stats['rejected'] else 0
    }
    
    # Get recent complaints (up to 3)
    recent = query_db("""
        SELECT * FROM Complaints 
        WHERE StudentID = %s 
        ORDER BY CreatedDate DESC LIMIT 3
    """, (student_id,))
    
    # Fetch recent unread notifications count
    unread_notifs = query_db("""
        SELECT COUNT(*) as count FROM Notifications 
        WHERE StudentID = %s AND (IsRead = FALSE OR IsRead = 0)
    """, (student_id,), one=True)
    
    unread_count = unread_notifs['count'] if unread_notifs else 0
    
    return render_template('student/dashboard.html', stats=stats_cleaned, recent=recent, unread_count=unread_count)

@student_bp.route('/submit', methods=['GET', 'POST'])
@student_required
def submit_complaint():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        image = request.files.get('image')
        student_id = session['user_id']
        
        # Form Validation
        if not title or not category or not description:
            flash("Please fill in all required fields (Title, Category, Description).", "danger")
            return render_template('student/submit.html')
            
        # Process optional file upload
        image_path = None
        if image and image.filename != '':
            image_path = save_uploaded_image(image)
            if not image_path:
                flash("Invalid image type. Allowed: PNG, JPG, JPEG, GIF", "danger")
                return render_template('student/submit.html')

        try:
            # Insert Complaint
            insert_query = """
                INSERT INTO Complaints (StudentID, Title, Category, Description, Status, ImagePath, CreatedDate)
                VALUES (%s, %s, %s, %s, 'Pending', %s, CURRENT_TIMESTAMP)
            """
            query_db(insert_query, (student_id, title, category, description, image_path), commit=True)
            
            # Fetch the inserted complaint's ID
            new_complaint = query_db("""
                SELECT ComplaintID FROM Complaints 
                WHERE StudentID = %s AND Title = %s ORDER BY CreatedDate DESC LIMIT 1
            """, (student_id, title), one=True)
            
            complaint_id = new_complaint['ComplaintID']
            
            # Add ComplaintHistory record
            query_db("""
                INSERT INTO ComplaintHistory (ComplaintID, OldStatus, NewStatus, UpdatedBy, Remarks, UpdatedDate)
                VALUES (%s, NULL, 'Pending', %s, %s, CURRENT_TIMESTAMP)
            """, (complaint_id, session['user_name'], "Complaint submitted by student."), commit=True)
            
            # Create Notification
            add_notification(student_id, f"Your complaint '{title}' (ID: #{complaint_id}) has been successfully submitted.")
            
            flash("Your complaint has been submitted successfully!", "success")
            return redirect(url_for('student.history'))
            
        except Exception as e:
            print(f"Complaint Submission DB Error: {e}")
            flash("An error occurred during submission. Please try again.", "danger")
            
    return render_template('student/submit.html')

@student_bp.route('/history')
@student_required
def history():
    student_id = session['user_id']
    
    # Query categories and statuses for template filters
    complaints = query_db("""
        SELECT * FROM Complaints 
        WHERE StudentID = %s 
        ORDER BY CreatedDate DESC
    """, (student_id,))
    
    return render_template('student/history.html', complaints=complaints)

@student_bp.route('/complaints/<int:complaint_id>')
@student_required
def details(complaint_id):
    student_id = session['user_id']
    
    # Verify owner of complaint
    complaint = query_db("""
        SELECT * FROM Complaints 
        WHERE ComplaintID = %s AND StudentID = %s
    """, (complaint_id, student_id), one=True)
    
    if not complaint:
        flash("Complaint not found or unauthorized.", "danger")
        return redirect(url_for('student.history'))
        
    # Get status timeline history
    history_logs = query_db("""
        SELECT * FROM ComplaintHistory 
        WHERE ComplaintID = %s 
        ORDER BY UpdatedDate ASC
    """, (complaint_id,))
    
    return render_template('student/details.html', complaint=complaint, history_logs=history_logs)

@student_bp.route('/notifications')
@student_required
def notifications():
    student_id = session['user_id']
    
    # Fetch notifications
    notifs = query_db("""
        SELECT * FROM Notifications 
        WHERE StudentID = %s 
        ORDER BY CreatedDate DESC
    """, (student_id,))
    
    # Mark all as read
    query_db("""
        UPDATE Notifications 
        SET IsRead = TRUE 
        WHERE StudentID = %s AND (IsRead = FALSE OR IsRead = 0)
    """, (student_id,), commit=True)
    
    return render_template('student/notifications.html', notifications=notifs)

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not department or not email:
            flash("Name, Email, and Department are required.", "danger")
            return redirect(url_for('student.profile'))
            
        # Check email uniqueness (excluding current student)
        existing = query_db("""
            SELECT * FROM Students 
            WHERE Email = %s AND StudentID != %s
        """, (email, student_id), one=True)
        
        if existing:
            flash("That email is already registered by another user.", "danger")
            return redirect(url_for('student.profile'))
            
        try:
            if password and password.strip() != "":
                hashed = generate_password_hash(password)
                query_db("""
                    UPDATE Students 
                    SET Name = %s, Department = %s, Email = %s, Password = %s
                    WHERE StudentID = %s
                """, (name, department, email, hashed, student_id), commit=True)
            else:
                query_db("""
                    UPDATE Students 
                    SET Name = %s, Department = %s, Email = %s
                    WHERE StudentID = %s
                """, (name, department, email, student_id), commit=True)
                
            session['user_name'] = name
            session['user_email'] = email
            flash("Profile updated successfully!", "success")
            
        except Exception as e:
            print(f"Profile Update Error: {e}")
            flash("Database error during profile update.", "danger")
            
        return redirect(url_for('student.profile'))
        
    student = query_db("SELECT * FROM Students WHERE StudentID = %s", (student_id,), one=True)
    return render_template('student/profile.html', student=student)
