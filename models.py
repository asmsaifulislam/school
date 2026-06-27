from datetime import datetime
from extensions import db


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    head = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='department', lazy=True)
    teachers = db.relationship('Teacher', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    qualification = db.Column(db.String(200))
    address = db.Column(db.Text)
    photo = db.Column(db.String(200))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Teacher {self.full_name()}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    photo = db.Column(db.String(200))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Student {self.full_name()}>'


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Notice {self.title}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#3788d8')
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'


class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    previous_school = db.Column(db.String(200))
    grade_applying = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)

    department_rel = db.relationship('Department')

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Admission {self.full_name()}>'


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage {self.name}>'


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
