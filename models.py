from flask_login import UserMixin
from datetime import datetime
from extensions import db

# Association tables for many-to-many relationships
section_students = db.Table('section_students',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

section_teachers = db.Table('section_teachers',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

section_courses = db.Table('section_courses',
    db.Column('section_id', db.Integer, db.ForeignKey('section.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'faculty', 'student'
    department = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendances = db.relationship('Attendance', foreign_keys='Attendance.user_id', backref='user', lazy=True)
    marked_attendances = db.relationship('Attendance', foreign_keys='Attendance.marked_by', backref='marked_by_user', lazy=True)
    leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.user_id', backref='user', lazy=True)
    approved_leaves = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.approved_by', backref='approved_by_user', lazy=True)

    # Section relationships
    student_sections = db.relationship('Section', secondary=section_students, backref=db.backref('students', lazy='dynamic'))
    teacher_sections = db.relationship('Section', secondary=section_teachers, backref=db.backref('teachers', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendances = db.relationship('Attendance', backref='course', lazy=True)
    faculty = db.relationship('User', foreign_keys=[faculty_id], backref='courses')
    sections = db.relationship('Section', secondary=section_courses, backref=db.backref('courses', lazy='dynamic'))

    def __repr__(self):
        return f'<Course {self.name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent', 'late'
    marked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.user_id} {self.date}>'

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LeaveRequest {self.user_id} {self.start_date}>'

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Creator relationship
    creator = db.relationship('User', foreign_keys=[created_by])

    # Many-to-many relationships
    section_courses_rel = db.relationship('Course', secondary=section_courses, overlaps="courses,sections", viewonly=True)

    def __repr__(self):
        return f'<Section {self.name}>'
