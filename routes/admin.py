import datetime
from collections import Counter
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash
from models.db import query_db
from utils.helpers import admin_required, add_notification

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # 1. Summary Cards
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN Status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN Status = 'Under Review' THEN 1 ELSE 0 END) as under_review,
            SUM(CASE WHEN Status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM Complaints
    """, one=True)
    
    stats_cleaned = {
        'total': stats['total'] if stats else 0,
        'pending': stats['pending'] if stats and stats['pending'] else 0,
        'under_review': stats['under_review'] if stats and stats['under_review'] else 0,
        'in_progress': stats['in_progress'] if stats and stats['in_progress'] else 0,
        'resolved': stats['resolved'] if stats and stats['resolved'] else 0,
        'rejected': stats['rejected'] if stats and stats['rejected'] else 0
    }
    
    # 2. Recent Complaints (Limit 5)
    recent = query_db("""
        SELECT c.*, s.Name as StudentName 
        FROM Complaints c 
        JOIN Students s ON c.StudentID = s.StudentID 
        ORDER BY c.CreatedDate DESC LIMIT 5
    """)
    
    # 3. Category-wise statistics
    category_raw = query_db("SELECT Category, COUNT(*) as count FROM Complaints GROUP BY Category")
    category_stats = {row['Category']: row['count'] for row in category_raw} if category_raw else {}
    
    # 4. Status statistics
    status_raw = query_db("SELECT Status, COUNT(*) as count FROM Complaints GROUP BY Status")
    status_stats = {row['Status']: row['count'] for row in status_raw} if status_raw else {}

    return render_template('admin/dashboard.html', 
                           stats=stats_cleaned, 
                           recent=recent, 
                           category_stats=category_stats,
                           status_stats=status_stats)

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """
    JSON API endpoint for live dashboard polling.
    Returns current complaint counts, category stats, and status stats.
    """
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN Status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN Status = 'Under Review' THEN 1 ELSE 0 END) as under_review,
            SUM(CASE WHEN Status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN Status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM Complaints
    """, one=True)

    stats_data = {
        'total': int(stats['total']) if stats and stats['total'] else 0,
        'pending': int(stats['pending']) if stats and stats['pending'] else 0,
        'under_review': int(stats['under_review']) if stats and stats['under_review'] else 0,
        'in_progress': int(stats['in_progress']) if stats and stats['in_progress'] else 0,
        'resolved': int(stats['resolved']) if stats and stats['resolved'] else 0,
        'rejected': int(stats['rejected']) if stats and stats['rejected'] else 0,
    }

    category_raw = query_db("SELECT Category, COUNT(*) as count FROM Complaints GROUP BY Category")
    category_stats = {row['Category']: row['count'] for row in category_raw} if category_raw else {}

    status_raw = query_db("SELECT Status, COUNT(*) as count FROM Complaints GROUP BY Status")
    status_stats = {row['Status']: row['count'] for row in status_raw} if status_raw else {}

    return jsonify({
        'stats': stats_data,
        'category_stats': category_stats,
        'status_stats': status_stats
    })

@admin_bp.route('/complaints')
@admin_required
def manage_complaints():
    # Load all complaints for the admin view table
    complaints = query_db("""
        SELECT c.*, s.Name as StudentName, s.Department as StudentDept
        FROM Complaints c
        JOIN Students s ON c.StudentID = s.StudentID
        ORDER BY c.CreatedDate DESC
    """)
    return render_template('admin/manage.html', complaints=complaints)

@admin_bp.route('/complaints/<int:complaint_id>', methods=['GET', 'POST'])
@admin_required
def details(complaint_id):
    # Fetch complaint and student info
    complaint = query_db("""
        SELECT c.*, s.Name as StudentName, s.Email as StudentEmail, s.Department as StudentDept
        FROM Complaints c
        JOIN Students s ON c.StudentID = s.StudentID
        WHERE c.ComplaintID = %s
    """, (complaint_id,), one=True)
    
    if not complaint:
        flash("Complaint not found.", "danger")
        return redirect(url_for('admin.manage_complaints'))
        
    if request.method == 'POST':
        new_status = request.form.get('status')
        remarks = request.form.get('remarks')
        assignee = request.form.get('assignee', '')
        old_status = complaint['Status']
        admin_name = session['user_name']
        
        if not new_status:
            flash("Please choose a valid status.", "danger")
            return redirect(url_for('admin.details', complaint_id=complaint_id))
            
        try:
            # Update complaint status
            query_db("""
                UPDATE Complaints 
                SET Status = %s 
                WHERE ComplaintID = %s
            """, (new_status, complaint_id), commit=True)
            
            # Write History Log
            log_msg = f"Status updated to '{new_status}' by Admin {admin_name}."
            if assignee:
                log_msg += f" Assigned to: {assignee}."
            if remarks:
                log_msg += f" Remarks: {remarks}."
                
            query_db("""
                INSERT INTO ComplaintHistory (ComplaintID, OldStatus, NewStatus, UpdatedBy, Remarks, UpdatedDate)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (complaint_id, old_status, new_status, f"Admin {admin_name}", log_msg), commit=True)
            
            # Notify Student
            notif_msg = f"Your complaint '{complaint['Title']}' (ID: #{complaint_id}) status was updated to '{new_status}'."
            if remarks:
                notif_msg += f" Remarks: {remarks}"
            add_notification(complaint['StudentID'], notif_msg)
            
            flash(f"Complaint #{complaint_id} status updated successfully to '{new_status}'.", "success")
            return redirect(url_for('admin.details', complaint_id=complaint_id))
            
        except Exception as e:
            print(f"Admin Update DB Error: {e}")
            flash("Failed to update status in database.", "danger")
            
    # GET: Retrieve status history
    history_logs = query_db("""
        SELECT * FROM ComplaintHistory 
        WHERE ComplaintID = %s 
        ORDER BY UpdatedDate ASC
    """, (complaint_id,))
    
    return render_template('admin/details.html', complaint=complaint, history_logs=history_logs)

@admin_bp.route('/students', methods=['GET', 'POST'])
@admin_required
def students():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            department = request.form.get('department')
            password = request.form.get('password')
            
            if not name or not email or not department or not password:
                flash("All student fields are required.", "danger")
                return redirect(url_for('admin.students'))
                
            # Email uniqueness check
            existing = query_db("SELECT * FROM Students WHERE Email = %s", (email,), one=True)
            if existing:
                flash("Email already registered.", "danger")
                return redirect(url_for('admin.students'))
                
            hashed = generate_password_hash(password)
            try:
                query_db("""
                    INSERT INTO Students (Name, Email, Department, Password) 
                    VALUES (%s, %s, %s, %s)
                """, (name, email, department, hashed), commit=True)
                flash(f"Student '{name}' added successfully.", "success")
            except Exception as e:
                print(f"Error adding student: {e}")
                flash("Database error adding student.", "danger")
                
        elif action == 'delete':
            student_id = request.form.get('student_id')
            if student_id:
                try:
                    query_db("DELETE FROM Students WHERE StudentID = %s", (student_id,), commit=True)
                    flash("Student account and associated complaints deleted.", "success")
                except Exception as e:
                    print(f"Error deleting student: {e}")
                    flash("Database error deleting student.", "danger")
                    
        return redirect(url_for('admin.students'))
        
    # GET: Load all students
    all_students = query_db("SELECT StudentID, Name, Email, Department FROM Students ORDER BY Name ASC")
    return render_template('admin/students.html', students=all_students)

@admin_bp.route('/reports')
@admin_required
def reports():
    # Gather reports metrics. Fully database-independent by processing in Python
    all_complaints = query_db("""
        SELECT Status, Category, CreatedDate 
        FROM Complaints
    """)
    
    total = len(all_complaints)
    resolved = sum(1 for c in all_complaints if c['Status'] == 'Resolved')
    pending = sum(1 for c in all_complaints if c['Status'] == 'Pending')
    under_review = sum(1 for c in all_complaints if c['Status'] == 'Under Review')
    in_progress = sum(1 for c in all_complaints if c['Status'] == 'In Progress')
    rejected = sum(1 for c in all_complaints if c['Status'] == 'Rejected')
    
    res_percentage = round((resolved / total) * 100, 2) if total > 0 else 0.0
    
    # 1. Category Distribution
    category_counts = Counter(c['Category'] for c in all_complaints)
    
    # 2. Monthly Distribution
    monthly_counts = {}
    for c in all_complaints:
        dt = c['CreatedDate']
        # Handle string or datetime objects gracefully
        if isinstance(dt, str):
            # Parse 'YYYY-MM-DD HH:MM:SS'
            try:
                date_obj = datetime.datetime.strptime(dt.split('.')[0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    date_obj = datetime.datetime.strptime(dt, "%Y-%m-%d")
                except ValueError:
                    date_obj = datetime.datetime.now()
        else:
            date_obj = dt
            
        month_str = date_obj.strftime("%B %Y") # e.g. "July 2026"
        monthly_counts[month_str] = monthly_counts.get(month_str, 0) + 1
        
    # Order monthly counts (could sort keys or leave as encountered)
    # Let's sort by date parsing
    def sort_month(m_str):
        try:
            return datetime.datetime.strptime(m_str, "%B %Y")
        except ValueError:
            return datetime.datetime.now()
            
    sorted_months = sorted(monthly_counts.keys(), key=sort_month)
    monthly_data = {m: monthly_counts[m] for m in sorted_months}

    return render_template('admin/reports.html',
                           total=total,
                           resolved=resolved,
                           pending=pending,
                           under_review=under_review,
                           in_progress=in_progress,
                           rejected=rejected,
                           res_percentage=res_percentage,
                           category_counts=dict(category_counts),
                           monthly_data=monthly_data)
