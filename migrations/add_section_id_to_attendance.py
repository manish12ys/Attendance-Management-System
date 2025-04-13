from extensions import db
from models import Section, Attendance, Course, User
from flask import Flask
from app import create_app

def migrate_attendance_data():
    """
    Migration script to add section_id to existing attendance records
    """
    app = create_app()
    
    with app.app_context():
        # Get all attendance records without section_id
        attendance_records = Attendance.query.all()
        
        # For each attendance record, find an appropriate section
        for record in attendance_records:
            # Get the course
            course = Course.query.get(record.course_id)
            
            # Get the student
            student = User.query.get(record.user_id)
            
            # Find a section that contains both the course and the student
            sections = Section.query.filter(Section.courses.contains(course)).all()
            
            student_section = None
            for section in sections:
                if student in section.students:
                    student_section = section
                    break
            
            # If no section found, use the first section that contains the course
            if not student_section and sections:
                student_section = sections[0]
            
            # If still no section, create a new one
            if not student_section:
                section_name = f"{course.name} Default Section"
                student_section = Section(
                    name=section_name,
                    description=f"Default section created for {course.name}",
                    created_by=1  # Admin user ID
                )
                student_section.courses.append(course)
                student_section.students.append(student)
                db.session.add(student_section)
                db.session.commit()
            
            # Update the attendance record
            record.section_id = student_section.id
        
        # Commit all changes
        db.session.commit()
        
        print(f"Migration completed. Updated {len(attendance_records)} attendance records.")

if __name__ == "__main__":
    migrate_attendance_data()
