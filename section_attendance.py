from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Course, Section
from datetime import datetime, date

# Create a blueprint for section-based attendance
section_bp = Blueprint('section', __name__)

@section_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard for section-based attendance
    """
    if current_user.role == 'admin':
        # Get all sections
        sections = Section.query.all()
    elif current_user.role == 'faculty':
        # Get sections where the faculty teaches
        sections = []
        courses = Course.query.filter_by(faculty_id=current_user.id).all()
        for course in courses:
            for section in course.sections:
                if section not in sections:
                    sections.append(section)
    else:
        # Get sections where the student is enrolled
        sections = current_user.student_sections

    return render_template('section/dashboard.html', sections=sections)

@section_bp.route('/section/<int:section_id>')
@login_required
def view_section(section_id):
    """
    View section details
    """
    section = Section.query.get_or_404(section_id)

    # Check if the user has access to this section
    if current_user.role == 'admin':
        pass  # Admin has access to all sections
    elif current_user.role == 'faculty':
        # Check if the faculty teaches any course in this section
        faculty_courses = Course.query.filter_by(faculty_id=current_user.id).all()
        if not any(course in section.courses for course in faculty_courses):
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))
    else:
        # Check if the student is enrolled in this section
        if section not in current_user.student_sections:
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))

    return render_template('section/view_section.html', section=section)

@section_bp.route('/section/<int:section_id>/courses')
@login_required
def section_courses(section_id):
    """
    View courses in a section
    """
    section = Section.query.get_or_404(section_id)

    # Check if the user has access to this section
    if current_user.role == 'admin':
        pass  # Admin has access to all sections
    elif current_user.role == 'faculty':
        # Check if the faculty teaches any course in this section
        faculty_courses = Course.query.filter_by(faculty_id=current_user.id).all()
        if not any(course in section.courses for course in faculty_courses):
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))
    else:
        # Check if the student is enrolled in this section
        if section not in current_user.student_sections:
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))

    return render_template('section/section_courses.html', section=section)

@section_bp.route('/section/<int:section_id>/students')
@login_required
def section_students(section_id):
    """
    View students in a section
    """
    section = Section.query.get_or_404(section_id)

    # Check if the user has access to this section
    if current_user.role == 'admin':
        pass  # Admin has access to all sections
    elif current_user.role == 'faculty':
        # Check if the faculty teaches any course in this section
        faculty_courses = Course.query.filter_by(faculty_id=current_user.id).all()
        if not any(course in section.courses for course in faculty_courses):
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))
    else:
        # Check if the student is enrolled in this section
        if section not in current_user.student_sections:
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))

    return render_template('section/section_students.html', section=section)

@section_bp.route('/section/<int:section_id>/attendance')
@login_required
def section_attendance(section_id):
    """
    View attendance for a section
    """
    section = Section.query.get_or_404(section_id)

    # Check if the user has access to this section
    if current_user.role == 'admin':
        pass  # Admin has access to all sections
    elif current_user.role == 'faculty':
        # Check if the faculty teaches any course in this section
        faculty_courses = Course.query.filter_by(faculty_id=current_user.id).all()
        if not any(course in section.courses for course in faculty_courses):
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))
    else:
        # Check if the student is enrolled in this section
        if section not in current_user.student_sections:
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))

    # Get attendance records for this section
    # We'll use the existing Attendance model but filter by section_id
    # This will be implemented in the template

    return render_template('section/section_attendance.html', section=section)

@section_bp.route('/section/<int:section_id>/mark_attendance', methods=['GET', 'POST'])
@login_required
def mark_section_attendance(section_id):
    """
    Mark attendance for a section
    """
    if current_user.role not in ['admin', 'faculty']:
        flash('Access denied. Admin or faculty privileges required.', 'danger')
        return redirect(url_for('section.dashboard'))

    section = Section.query.get_or_404(section_id)

    # Check if the faculty teaches any course in this section
    if current_user.role == 'faculty':
        faculty_courses = Course.query.filter_by(faculty_id=current_user.id).all()
        if not any(course in section.courses for course in faculty_courses):
            flash('You do not have access to this section', 'danger')
            return redirect(url_for('section.dashboard'))

    if request.method == 'POST':
        # Get form data
        course_id = request.form.get('course_id')
        attendance_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()

        # Validate form data
        if not course_id or not attendance_date:
            flash('Please select a course and date', 'danger')
            return redirect(url_for('section.mark_section_attendance', section_id=section_id))

        # Check if the course is in this section
        course = Course.query.get(course_id)
        if course not in section.courses:
            flash('The selected course is not in this section', 'danger')
            return redirect(url_for('section.mark_section_attendance', section_id=section_id))

        # Mark attendance for each student in the section
        for student in section.students:
            status = request.form.get(f'status_{student.id}')

            if status:
                # Check if attendance record already exists
                attendance = db.session.execute(
                    db.select(Attendance).filter_by(
                        user_id=student.id,
                        course_id=course_id,
                        date=attendance_date
                    )
                ).scalar_one_or_none()

                if attendance:
                    # Update existing record
                    attendance.status = status
                    attendance.marked_by = current_user.id
                    attendance.marked_at = datetime.utcnow()
                    attendance.section_id = section_id
                else:
                    # Create new record
                    attendance = Attendance(
                        user_id=student.id,
                        course_id=course_id,
                        date=attendance_date,
                        status=status,
                        marked_by=current_user.id,
                        section_id=section_id
                    )
                    db.session.add(attendance)

        db.session.commit()
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('section.section_attendance', section_id=section_id))

    # Get courses in this section
    courses = list(section.courses)

    # Get students in this section
    students = list(section.students)

    return render_template('section/mark_section_attendance.html',
                          section=section,
                          courses=courses,
                          students=students,
                          today=date.today().strftime('%Y-%m-%d'))

# Import this at the end to avoid circular imports
from models import Attendance
