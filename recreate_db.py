import os
from app import create_app
from extensions import db
from models import User, Course, Section, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime

def recreate_database():
    """
    Recreate the database with the updated schema
    """
    # Delete the existing database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')
    if os.path.exists(db_path):
        print(f"Removing existing database at: {db_path}")
        os.remove(db_path)

    # Create a new app instance
    app = create_app()

    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()

        # Create admin user if not exists
        print("Creating admin user...")
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                name='Admin User',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)

        # Create some sample data
        print("Creating sample data...")

        # Create faculty user if not exists
        faculty = User.query.filter_by(email='faculty@example.com').first()
        if not faculty:
            faculty = User(
                name='Faculty User',
                email='faculty@example.com',
                password=generate_password_hash('faculty123'),
                role='faculty'
            )
            db.session.add(faculty)

        # Create student user if not exists
        student = User.query.filter_by(email='student@example.com').first()
        if not student:
            student = User(
                name='Student User',
                email='student@example.com',
                password=generate_password_hash('student123'),
                role='student',
                department='Computer Science'
            )
            db.session.add(student)

        # Create course if not exists
        course = Course.query.filter_by(code='CS101').first()
        if not course:
            course = Course(
                name='Sample Course',
                code='CS101',
                faculty_id=faculty.id
            )
            db.session.add(course)

        # Create section if not exists
        section = Section.query.filter_by(name='Sample Section').first()
        if not section:
            section = Section(
                name='Sample Section',
                description='This is a sample section',
                created_by=admin.id
            )
            db.session.add(section)

        # Commit to get IDs
        db.session.commit()

        # Add relationships if not already added
        if student not in section.students:
            section.students.append(student)
        if course not in section.section_courses_rel:
            section.section_courses_rel.append(course)

        # Create attendance record if not exists
        today = datetime.now().date()
        attendance = Attendance.query.filter_by(
            user_id=student.id,
            course_id=course.id,
            date=today
        ).first()
        if not attendance:
            attendance = Attendance(
                user_id=student.id,
                course_id=course.id,
                date=today,
                status='present',
                marked_by=faculty.id,
                marked_at=datetime.now()
            )
            db.session.add(attendance)

        # Commit all changes
        db.session.commit()

        print("Database recreated successfully with sample data.")

if __name__ == "__main__":
    recreate_database()
