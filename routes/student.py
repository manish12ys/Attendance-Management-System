from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Course, Attendance, LeaveRequest, Section
from datetime import datetime, date, timedelta

student_bp = Blueprint('student', __name__)

# Student dashboard
@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get sections the student is enrolled in
    sections = current_user.student_sections

    # Get courses from these sections
    courses = []
    for section in sections:
        courses.extend([c for c in section.courses if c not in courses])

    # Get recent attendance records
    recent_attendance = Attendance.query.filter_by(
        user_id=current_user.id
    ).order_by(Attendance.date.desc()).limit(10).all()

    # Calculate attendance statistics
    total_classes = Attendance.query.filter_by(user_id=current_user.id).count()
    present_count = Attendance.query.filter_by(user_id=current_user.id, status='present').count()
    absent_count = Attendance.query.filter_by(user_id=current_user.id, status='absent').count()
    late_count = Attendance.query.filter_by(user_id=current_user.id, status='late').count()

    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    # Get pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).count()

    return render_template('student/dashboard.html',
                          courses=courses,
                          recent_attendance=recent_attendance,
                          total_classes=total_classes,
                          present_count=present_count,
                          absent_count=absent_count,
                          late_count=late_count,
                          attendance_percentage=attendance_percentage,
                          pending_leaves=pending_leaves)

# View attendance
@student_bp.route('/attendance')
@login_required
def view_attendance():
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get all courses
    courses = Course.query.all()

    # Get attendance records for each course
    course_attendance = {}
    for course in courses:
        attendance_records = Attendance.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).order_by(Attendance.date.desc()).all()

        total_classes = len(attendance_records)
        present_count = sum(1 for record in attendance_records if record.status == 'present')
        absent_count = sum(1 for record in attendance_records if record.status == 'absent')
        late_count = sum(1 for record in attendance_records if record.status == 'late')

        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

        course_attendance[course.id] = {
            'records': attendance_records,
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_percentage': attendance_percentage
        }

    return render_template('student/view_attendance.html',
                          courses=courses,
                          course_attendance=course_attendance)

# View course attendance
@student_bp.route('/attendance/<int:course_id>')
@login_required
def view_course_attendance(course_id):
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Get attendance records for this course
    attendance_records = Attendance.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).order_by(Attendance.date.desc()).all()

    # Calculate statistics
    total_classes = len(attendance_records)
    present_count = sum(1 for record in attendance_records if record.status == 'present')
    absent_count = sum(1 for record in attendance_records if record.status == 'absent')
    late_count = sum(1 for record in attendance_records if record.status == 'late')

    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    return render_template('student/course_attendance.html',
                          course=course,
                          attendance_records=attendance_records,
                          total_classes=total_classes,
                          present_count=present_count,
                          absent_count=absent_count,
                          late_count=late_count,
                          attendance_percentage=attendance_percentage)

# Leave requests
@student_bp.route('/leaves')
@login_required
def leave_requests():
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get all leave requests
    leave_requests = LeaveRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(LeaveRequest.created_at.desc()).all()

    return render_template('student/leave_requests.html', leave_requests=leave_requests)

# Submit leave request
@student_bp.route('/leaves/submit', methods=['GET', 'POST'])
@login_required
def submit_leave():
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')

        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Validate dates
        if start_date > end_date:
            flash('Start date cannot be after end date', 'danger')
            return redirect(url_for('student.submit_leave'))

        if start_date < date.today():
            flash('Start date cannot be in the past', 'danger')
            return redirect(url_for('student.submit_leave'))

        # Create leave request
        leave_request = LeaveRequest(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending'
        )

        db.session.add(leave_request)
        db.session.commit()

        flash('Leave request submitted successfully', 'success')
        return redirect(url_for('student.leave_requests'))

    return render_template('student/submit_leave.html')

# Cancel leave request
@student_bp.route('/leaves/cancel/<int:leave_id>', methods=['POST'])
@login_required
def cancel_leave(leave_id):
    if current_user.role != 'student':
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('index'))

    leave_request = LeaveRequest.query.get_or_404(leave_id)

    # Ensure leave request belongs to current user
    if leave_request.user_id != current_user.id:
        flash('You do not have permission to cancel this leave request', 'danger')
        return redirect(url_for('student.leave_requests'))

    # Ensure leave request is still pending
    if leave_request.status != 'pending':
        flash('Cannot cancel a leave request that has already been processed', 'danger')
        return redirect(url_for('student.leave_requests'))

    db.session.delete(leave_request)
    db.session.commit()

    flash('Leave request cancelled successfully', 'success')
    return redirect(url_for('student.leave_requests'))
