from app import app
from extensions import db
from models import Department, Teacher, Student, Notice, Event, AdminUser
from werkzeug.security import generate_password_hash
from datetime import datetime, date


def seed():
    with app.app_context():
        db.create_all()

        if Department.query.first():
            print('Database already seeded.')
            return

        depts = [
            Department(name='Computer Science', code='CS', description='Study of computers and computational systems. Covers programming, algorithms, data structures, and software engineering.', head='Dr. Alan Turing'),
            Department(name='Mathematics', code='MATH', description='Study of numbers, quantities, shapes, and patterns. Includes algebra, calculus, statistics, and geometry.', head='Dr. Ada Lovelace'),
            Department(name='Physics', code='PHY', description='Study of matter, energy, and the fundamental forces of nature. Covers mechanics, thermodynamics, and quantum physics.', head='Dr. Albert Einstein'),
            Department(name='English Literature', code='ENG', description='Study of literature written in the English language. Covers poetry, drama, fiction, and literary criticism.', head='Dr. Jane Austen'),
            Department(name='Biology', code='BIO', description='Study of living organisms and life processes. Covers genetics, ecology, microbiology, and evolution.', head='Dr. Charles Darwin'),
            Department(name='Chemistry', code='CHEM', description='Study of substances, their properties, and reactions. Covers organic, inorganic, physical, and analytical chemistry.', head='Dr. Marie Curie'),
        ]
        db.session.add_all(depts)
        db.session.commit()

        teachers = [
            Teacher(first_name='John', last_name='Smith', email='john.smith@school.com', phone='+1-555-0101', qualification='PhD in Computer Science', address='123 Oak St', department_id=1),
            Teacher(first_name='Sarah', last_name='Johnson', email='sarah.johnson@school.com', phone='+1-555-0102', qualification='PhD in Mathematics', address='456 Maple Ave', department_id=2),
            Teacher(first_name='Michael', last_name='Williams', email='michael.williams@school.com', phone='+1-555-0103', qualification='PhD in Physics', address='789 Pine Rd', department_id=3),
            Teacher(first_name='Emily', last_name='Brown', email='emily.brown@school.com', phone='+1-555-0104', qualification='MA in English', address='321 Elm St', department_id=4),
            Teacher(first_name='David', last_name='Jones', email='david.jones@school.com', phone='+1-555-0105', qualification='PhD in Biology', address='654 Cedar Ln', department_id=5),
            Teacher(first_name='Lisa', last_name='Garcia', email='lisa.garcia@school.com', phone='+1-555-0106', qualification='PhD in Chemistry', address='987 Birch Dr', department_id=6),
        ]
        db.session.add_all(teachers)
        db.session.commit()

        students_data = [
            ('Alice', 'Anderson', 'alice@example.com', '2005-03-15', 'Female', 1),
            ('Bob', 'Baker', 'bob@example.com', '2004-07-22', 'Male', 2),
            ('Charlie', 'Clark', 'charlie@example.com', '2005-01-10', 'Male', 3),
            ('Diana', 'Davis', 'diana@example.com', '2004-11-05', 'Female', 4),
            ('Edward', 'Evans', 'edward@example.com', '2005-05-20', 'Male', 5),
            ('Fiona', 'Foster', 'fiona@example.com', '2004-09-12', 'Female', 6),
            ('George', 'Green', 'george@example.com', '2005-02-28', 'Male', 1),
            ('Hannah', 'Hill', 'hannah@example.com', '2004-12-01', 'Female', 2),
        ]
        for fn, ln, em, dob, g, did in students_data:
            student = Student(
                first_name=fn, last_name=ln, email=em,
                phone='+1-555-1'+str(students_data.index((fn, ln, em, dob, g, did))+100),
                date_of_birth=datetime.strptime(dob, '%Y-%m-%d').date(),
                gender=g, address='123 Student St', department_id=did
            )
            db.session.add(student)
        db.session.commit()

        notices = [
            Notice(title='Welcome to the New Academic Year', content='We are excited to welcome all students and staff to the new academic year. Classes will begin on September 1st. Please check your schedules and reach out to your department for any questions.', category='general', is_published=True),
            Notice(title='Mid-Term Exam Schedule', content='The mid-term examinations will be held from October 15th to October 25th. Please check the examination schedule posted in your departments. All students must carry their ID cards to the exam hall.', category='exam', is_published=True),
            Notice(title='Annual Sports Day', content='The annual sports day will be held on December 10th. Students are encouraged to participate in various sports events. Registration forms are available at the sports office.', category='event', is_published=True),
            Notice(title='Holiday Notice: Winter Break', content='The institution will remain closed for winter break from December 20th to January 5th. All offices will reopen on January 6th. Wishing everyone a happy holiday season!', category='holiday', is_published=True),
        ]
        db.session.add_all(notices)
        db.session.commit()

        events = [
            Event(title='Orientation Day', description='Welcome orientation for new students', start_date=datetime(2024, 9, 1), end_date=datetime(2024, 9, 1), location='Main Auditorium', color='#3788d8', is_public=True),
            Event(title='Science Fair', description='Annual science exhibition', start_date=datetime(2024, 10, 20), end_date=datetime(2024, 10, 22), location='Science Building', color='#1cc88a', is_public=True),
            Event(title='Sports Day', description='Annual sports competition', start_date=datetime(2024, 12, 10), end_date=datetime(2024, 12, 10), location='Sports Complex', color='#f6c23e', is_public=True),
            Event(title='Winter Break', description='Winter holidays', start_date=datetime(2024, 12, 20), end_date=datetime(2025, 1, 5), location='', color='#e74a3b', is_public=True),
            Event(title='Parent-Teacher Meeting', description='Quarterly parent-teacher meeting', start_date=datetime(2024, 11, 15), end_date=datetime(2024, 11, 15), location='School Hall', color='#36b9cc', is_public=True),
        ]
        db.session.add_all(events)
        db.session.commit()

        print('Database seeded successfully!')
        print('Admin login: username=admin, password=admin123')


if __name__ == '__main__':
    seed()
