from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Course, Attendance, LeaveRequest, Section
from datetime import datetime
from utils.export import export_to_excel, export_to_pdf

admin_bp = Blueprint('admin', __name__)

# Admin dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get counts for dashboard
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_courses = Course.query.count()
    total_sections = Section.query.count()

    # Get recent attendance records
    try:
        # Use the ORM to get the records with relationships
        recent_attendance = Attendance.query\
            .order_by(Attendance.marked_at.desc())\
            .limit(10)\
            .all()

        # Debug print
        print(f"Recent attendance records: {len(recent_attendance)}")
        for record in recent_attendance:
            print(f"Student: {record.user.name if record.user else 'Unknown'}, Course: {record.course.name if record.course else 'Unknown'}, Date: {record.date}, Status: {record.status}")
    except Exception as e:
        print(f"Error getting attendance records: {e}")
        recent_attendance = []

    # Get pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()

    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_students=total_students,
                          total_faculty=total_faculty,
                          total_courses=total_courses,
                          total_sections=total_sections,
                          recent_attendance=recent_attendance,
                          pending_leaves=pending_leaves)

# Manage users
@admin_bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

# Add user
@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.add_user'))

        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html')

# Edit user
@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.department = request.form.get('department')

        # Update password if provided
        password = request.form.get('password')
        if password:
            user.password = generate_password_hash(password)

        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', user=user)

# Delete user
@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.manage_users'))

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

# Manage courses
@admin_bp.route('/courses')
@login_required
def manage_courses():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    courses = Course.query.all()
    faculty = User.query.filter_by(role='faculty').all()

    return render_template('admin/manage_courses.html', courses=courses, faculty=faculty)

# Add course
@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    faculty = User.query.filter_by(role='faculty').all()

    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        faculty_id = request.form.get('faculty_id')

        # Check if course code already exists
        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            flash('Course code already exists', 'danger')
            return redirect(url_for('admin.add_course'))

        # Create new course
        new_course = Course(
            name=name,
            code=code,
            faculty_id=faculty_id
        )

        db.session.add(new_course)
        db.session.commit()

        flash('Course added successfully', 'success')
        return redirect(url_for('admin.manage_courses'))

    return render_template('admin/add_course.html', faculty=faculty)

# Delete course
@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Delete all attendance records for this course
    Attendance.query.filter_by(course_id=course_id).delete()

    # Delete the course
    db.session.delete(course)
    db.session.commit()

    flash('Course deleted successfully', 'success')
    return redirect(url_for('admin.manage_courses'))

# Manage sections
@admin_bp.route('/sections')
@login_required
def manage_sections():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    sections = Section.query.all()
    return render_template('admin/manage_sections.html', sections=sections)

# Add section
@admin_bp.route('/sections/add', methods=['GET', 'POST'])
@login_required
def add_section():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        # Check if section already exists
        existing_section = Section.query.filter_by(name=name).first()
        if existing_section:
            flash('Section with this name already exists', 'danger')
            return redirect(url_for('admin.add_section'))

        # Create new section
        new_section = Section(
            name=name,
            description=description,
            created_by=current_user.id
        )

        db.session.add(new_section)
        db.session.commit()

        flash('Section added successfully', 'success')
        return redirect(url_for('admin.manage_sections'))

    return render_template('admin/add_section.html')

# Edit section
@admin_bp.route('/sections/edit/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    section = Section.query.get_or_404(section_id)

    if request.method == 'POST':
        section.name = request.form.get('name')
        section.description = request.form.get('description')

        db.session.commit()
        flash('Section updated successfully', 'success')
        return redirect(url_for('admin.manage_sections'))

    return render_template('admin/edit_section.html', section=section)

# Delete section
@admin_bp.route('/sections/delete/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    section = Section.query.get_or_404(section_id)

    db.session.delete(section)
    db.session.commit()

    flash('Section deleted successfully', 'success')
    return redirect(url_for('admin.manage_sections'))

# Manage section members
@admin_bp.route('/sections/<int:section_id>/members', methods=['GET', 'POST'])
@login_required
def manage_section_members(section_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    section = Section.query.get_or_404(section_id)
    students = User.query.filter_by(role='student').all()
    teachers = User.query.filter_by(role='faculty').all()

    # Get current students and teachers in the section
    current_student_ids = [s.id for s in section.students]
    current_teacher_ids = [t.id for t in section.teachers]

    if request.method == 'POST':
        # Get current students and teachers
        current_students = list(section.students)
        current_teachers = list(section.teachers)

        # Remove all current students and teachers
        for student in current_students:
            section.students.remove(student)

        for teacher in current_teachers:
            section.teachers.remove(teacher)

        # Add selected students
        student_ids = request.form.getlist('students')
        for student_id in student_ids:
            student = User.query.get(int(student_id))
            if student:
                section.students.append(student)

        # Add selected teachers
        teacher_ids = request.form.getlist('teachers')
        for teacher_id in teacher_ids:
            teacher = User.query.get(int(teacher_id))
            if teacher:
                section.teachers.append(teacher)

        db.session.commit()
        flash('Section members updated successfully', 'success')
        return redirect(url_for('admin.manage_sections'))

    return render_template('admin/manage_section_members.html',
                          section=section,
                          students=students,
                          teachers=teachers,
                          current_student_ids=current_student_ids,
                          current_teacher_ids=current_teacher_ids)

# Manage section courses
@admin_bp.route('/sections/<int:section_id>/courses', methods=['GET', 'POST'])
@login_required
def manage_section_courses(section_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    section = Section.query.get_or_404(section_id)
    courses = Course.query.all()

    # Get current courses in the section
    current_course_ids = [c.id for c in section.courses]

    if request.method == 'POST':
        # Get current courses
        current_courses = list(section.courses)

        # Remove all current courses
        for course in current_courses:
            section.courses.remove(course)

        # Add selected courses
        course_ids = request.form.getlist('courses')
        for course_id in course_ids:
            course = Course.query.get(int(course_id))
            if course:
                section.courses.append(course)

        db.session.commit()
        flash('Section courses updated successfully', 'success')
        return redirect(url_for('admin.manage_sections'))

    return render_template('admin/manage_section_courses.html',
                          section=section,
                          courses=courses,
                          current_course_ids=current_course_ids)

# Reports
@admin_bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('admin/reports.html', courses=courses)

# Generate attendance report
@admin_bp.route('/reports/attendance', methods=['POST'])
@login_required
def attendance_report():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    course_id = request.form.get('course_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get attendance records
    if course_id:
        # Get attendance records for specific course
        attendance_records = db.session.query(
            Attendance.id,
            Attendance.user_id,
            Attendance.course_id,
            Attendance.date,
            Attendance.status,
            Attendance.marked_by,
            Attendance.marked_at,
            User.name.label('user_name'),
            Course.name.label('course_name'),
            Course.code.label('course_code')
        ).join(User, User.id == Attendance.user_id)\
        .join(Course, Course.id == Attendance.course_id)\
        .filter(
            Attendance.course_id == course_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
    else:
        # Get attendance records
        attendance_records = db.session.query(
            Attendance.id,
            Attendance.user_id,
            Attendance.course_id,
            Attendance.date,
            Attendance.status,
            Attendance.marked_by,
            Attendance.marked_at,
            User.name.label('user_name'),
            Course.name.label('course_name'),
            Course.code.label('course_code')
        ).join(User, User.id == Attendance.user_id)\
        .join(Course, Course.id == Attendance.course_id)\
        .filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()

    course = Course.query.get(course_id) if course_id else None

    # Get all users for marked_by lookup
    users = User.query.all()

    return render_template('admin/attendance_report.html',
                          attendance_records=attendance_records,
                          course=course,
                          start_date=start_date,
                          end_date=end_date,
                          users=users)

# Export attendance report to Excel
@admin_bp.route('/reports/export/excel', methods=['POST'])
@login_required
def export_attendance_excel():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    course_id = request.form.get('course_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get attendance records
    if course_id:
        attendance_records = Attendance.query.filter(
            Attendance.course_id == course_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        course = Course.query.get(course_id)
    else:
        attendance_records = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        course = None

    # Export to Excel
    output, filename = export_to_excel(attendance_records, course, start_date, end_date)

    # Return the Excel file as a response
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Export attendance report to PDF
@admin_bp.route('/reports/export/pdf', methods=['POST'])
@login_required
def export_attendance_pdf():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    course_id = request.form.get('course_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get attendance records
    if course_id:
        attendance_records = Attendance.query.filter(
            Attendance.course_id == course_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        course = Course.query.get(course_id)
    else:
        attendance_records = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        course = None

    # Export to PDF
    output, filename = export_to_pdf(attendance_records, course, start_date, end_date)

    # Return the PDF file as a response
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# Manage leave requests
@admin_bp.route('/leaves')
@login_required
def manage_leaves():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    return render_template('admin/manage_leaves.html', leave_requests=leave_requests)

# Approve/reject leave request
@admin_bp.route('/leaves/<int:leave_id>/<action>', methods=['POST'])
@login_required
def process_leave(leave_id, action):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))

    leave_request = LeaveRequest.query.get_or_404(leave_id)

    if action == 'approve':
        leave_request.status = 'approved'
        leave_request.approved_by = current_user.id
        flash('Leave request approved', 'success')
    elif action == 'reject':
        leave_request.status = 'rejected'
        leave_request.approved_by = current_user.id
        flash('Leave request rejected', 'danger')

    db.session.commit()
    return redirect(url_for('admin.manage_leaves'))
