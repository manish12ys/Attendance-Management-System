from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Course, Attendance, LeaveRequest, Section
from datetime import datetime, date

faculty_bp = Blueprint('faculty', __name__)

# Faculty dashboard
@faculty_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get courses taught by the faculty
    courses = Course.query.filter_by(faculty_id=current_user.id).all()

    # Get recent attendance records for these courses
    recent_attendance = Attendance.query.filter(
        Attendance.course_id.in_([course.id for course in courses])
    ).order_by(Attendance.marked_at.desc()).limit(10).all()

    # Get student count for each course
    course_stats = []
    for course in courses:
        student_count = Attendance.query.filter_by(course_id=course.id).distinct(Attendance.user_id).count()
        course_stats.append({
            'course': course,
            'student_count': student_count
        })

    return render_template('faculty/dashboard.html',
                          courses=courses,
                          recent_attendance=recent_attendance,
                          course_stats=course_stats)

# View course details
@faculty_bp.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    # Get sections for this course
    sections = Section.query.filter(Section.courses.contains(course)).all()

    # Get students from all sections of this course
    students = []
    for section in sections:
        students.extend([s for s in section.students if s not in students])

    return render_template('faculty/view_course.html', course=course, students=students)

# Mark attendance
@faculty_bp.route('/attendance/<int:course_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(course_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    # Get sections for this course
    sections = Section.query.filter(Section.courses.contains(course)).all()

    if not sections:
        flash('This course is not assigned to any section. Please assign it to a section first.', 'warning')
        return redirect(url_for('faculty.dashboard'))

    # Get students from all sections of this course
    students = []
    for section in sections:
        students.extend([s for s in section.students if s not in students])

    if request.method == 'POST':
        attendance_date = request.form.get('attendance_date')
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

        # Check if attendance already marked for this date
        existing_attendance = Attendance.query.filter_by(
            course_id=course_id,
            date=attendance_date
        ).first()

        if existing_attendance:
            flash('Attendance already marked for this date. Please edit instead.', 'warning')
            return redirect(url_for('faculty.mark_attendance', course_id=course_id))

        # Process attendance for each student
        for student in students:
            status = request.form.get(f'status_{student.id}')

            if status:
                # Find the section this student belongs to for this course
                student_section = None
                for section in sections:
                    if student in section.students:
                        student_section = section
                        break

                # Create attendance record
                attendance = Attendance(
                    user_id=student.id,
                    course_id=course_id,
                    date=attendance_date,
                    status=status,
                    marked_by=current_user.id
                )

                # Set section_id if student is in a section
                if student_section:
                    attendance.section_id = student_section.id
                db.session.add(attendance)

        db.session.commit()
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('faculty.view_course', course_id=course_id))

    return render_template('faculty/mark_attendance.html',
                          course=course,
                          students=students,
                          today=date.today())

# Edit attendance
@faculty_bp.route('/attendance/<int:course_id>/edit', methods=['GET'])
@login_required
def edit_attendance(course_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    # Get available dates for this course
    attendance_dates = db.session.query(Attendance.date).filter_by(
        course_id=course_id
    ).distinct().order_by(Attendance.date.desc()).all()

    attendance_dates = [date[0] for date in attendance_dates]

    return render_template('faculty/edit_attendance.html',
                          course=course,
                          attendance_dates=attendance_dates)

# Edit attendance for a specific date
@faculty_bp.route('/attendance/<int:course_id>/edit_date', methods=['GET', 'POST'])
@login_required
def edit_attendance_date(course_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    if request.method == 'GET':
        date_str = request.args.get('date')
        if not date_str:
            flash('Please select a date', 'warning')
            return redirect(url_for('faculty.edit_attendance', course_id=course_id))

        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get sections for this course
        sections = Section.query.filter(Section.courses.contains(course)).all()

        # Get students from all sections of this course
        students = []
        for section in sections:
            students.extend([s for s in section.students if s not in students])

        # Get attendance records for this date
        attendance_records = {}
        for student in students:
            attendance = Attendance.query.filter_by(
                user_id=student.id,
                course_id=course_id,
                date=attendance_date
            ).first()

            attendance_records[student.id] = attendance.status if attendance else None

        return render_template('faculty/edit_attendance_date.html',
                              course=course,
                              students=students,
                              attendance_date=attendance_date,
                              attendance_records=attendance_records)

    if request.method == 'POST':
        attendance_date = request.form.get('attendance_date')
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

        # Get sections for this course
        sections = Section.query.filter(Section.courses.contains(course)).all()

        # Get students from all sections of this course
        students = []
        for section in sections:
            students.extend([s for s in section.students if s not in students])

        # Update attendance for each student
        for student in students:
            status = request.form.get(f'status_{student.id}')

            # Find existing attendance record
            attendance = Attendance.query.filter_by(
                user_id=student.id,
                course_id=course_id,
                date=attendance_date
            ).first()

            if attendance:
                # Update existing record
                attendance.status = status
                attendance.marked_at = datetime.utcnow()
            else:
                # Create new record if not exists
                # Find the section this student belongs to for this course
                student_section = None
                for section in sections:
                    if student in section.students:
                        student_section = section
                        break

                # Create attendance record
                attendance = Attendance(
                    user_id=student.id,
                    course_id=course_id,
                    date=attendance_date,
                    status=status,
                    marked_by=current_user.id
                )

                # Set section_id if student is in a section
                if student_section:
                    attendance.section_id = student_section.id
                db.session.add(attendance)

        db.session.commit()
        flash('Attendance updated successfully', 'success')
        return redirect(url_for('faculty.view_course', course_id=course_id))



# View attendance for a specific date
@faculty_bp.route('/attendance/<int:course_id>/view/<date>')
@login_required
def view_attendance(course_id, date):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    attendance_date = datetime.strptime(date, '%Y-%m-%d').date()

    # Get all students
    students = User.query.filter_by(role='student').all()

    # Get attendance records for this date
    attendance_records = {}
    for student in students:
        attendance = Attendance.query.filter_by(
            user_id=student.id,
            course_id=course_id,
            date=attendance_date
        ).first()

        attendance_records[student.id] = attendance.status if attendance else 'Not marked'

    return render_template('faculty/view_attendance.html',
                          course=course,
                          students=students,
                          attendance_records=attendance_records,
                          attendance_date=attendance_date)

# Generate reports
@faculty_bp.route('/reports/<int:course_id>')
@login_required
def reports(course_id):
    if current_user.role != 'faculty':
        flash('Access denied. Faculty privileges required.', 'danger')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Ensure faculty is assigned to this course
    if course.faculty_id != current_user.id:
        flash('You are not assigned to this course', 'danger')
        return redirect(url_for('faculty.dashboard'))

    # Get all students
    students = User.query.filter_by(role='student').all()

    # Get attendance statistics for each student
    student_stats = []
    for student in students:
        total_classes = Attendance.query.filter_by(
            course_id=course_id,
            user_id=student.id
        ).count()

        present_count = Attendance.query.filter_by(
            course_id=course_id,
            user_id=student.id,
            status='present'
        ).count()

        absent_count = Attendance.query.filter_by(
            course_id=course_id,
            user_id=student.id,
            status='absent'
        ).count()

        late_count = Attendance.query.filter_by(
            course_id=course_id,
            user_id=student.id,
            status='late'
        ).count()

        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

        student_stats.append({
            'student': student,
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'attendance_percentage': attendance_percentage
        })

    return render_template('faculty/reports.html',
                          course=course,
                          student_stats=student_stats)
