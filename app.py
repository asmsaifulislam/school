import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from extensions import db

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

from models import Department, Teacher, Student, Notice, Event, Admission, ContactMessage, AdminUser
from forms import (LoginForm, StudentForm, TeacherForm, DepartmentForm,
                   NoticeForm, EventForm, AdmissionForm, ContactForm)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def save_file(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'{uuid.uuid4()}.{ext}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_now():
    return {
        'now': datetime.utcnow(),
        'Student': Student,
        'Teacher': Teacher,
        'Department': Department,
        'Notice': Notice,
        'Event': Event
    }


@app.route('/')
def index():
    notices = Notice.query.filter_by(is_published=True).order_by(Notice.created_at.desc()).limit(5).all()
    events = Event.query.filter_by(is_public=True).order_by(Event.start_date.asc()).limit(5).all()
    departments = Department.query.all()
    return render_template('index.html', notices=notices, events=events, departments=departments)


@app.route('/students')
def students():
    page = request.args.get('page', 1, type=int)
    dept_id = request.args.get('department', 0, type=int)
    search = request.args.get('search', '')

    query = Student.query.filter_by(is_active=True)
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if search:
        query = query.filter(
            Student.first_name.contains(search) |
            Student.last_name.contains(search) |
            Student.email.contains(search)
        )
    students_list = query.order_by(Student.first_name).paginate(page=page, per_page=12)
    departments = Department.query.all()
    return render_template('students.html', students=students_list, departments=departments)


@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    return render_template('student.html', student=student)


@app.route('/teachers')
def teachers():
    page = request.args.get('page', 1, type=int)
    dept_id = request.args.get('department', 0, type=int)

    query = Teacher.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    teachers_list = query.order_by(Teacher.first_name).paginate(page=page, per_page=12)
    departments = Department.query.all()
    return render_template('teachers.html', teachers=teachers_list, departments=departments)


@app.route('/teacher/<int:id>')
def teacher_detail(id):
    teacher = Teacher.query.get_or_404(id)
    return render_template('teacher.html', teacher=teacher)


@app.route('/departments')
def departments():
    dept_list = Department.query.all()
    return render_template('departments.html', departments=dept_list)


@app.route('/department/<int:id>')
def department_detail(id):
    department = Department.query.get_or_404(id)
    return render_template('department.html', department=department)


@app.route('/calendar')
def calendar():
    events = Event.query.filter_by(is_public=True).order_by(Event.start_date).all()
    return render_template('calendar.html', events=events)


@app.route('/notices')
def notices():
    page = request.args.get('page', 1, type=int)
    cat = request.args.get('category', '')

    query = Notice.query.filter_by(is_published=True)
    if cat:
        query = query.filter_by(category=cat)
    notices_list = query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('notices.html', notices=notices_list)


@app.route('/notice/<int:id>')
def notice_detail(id):
    notice = Notice.query.get_or_404(id)
    return render_template('notice.html', notice=notice)


@app.route('/admission', methods=['GET', 'POST'])
def admission():
    form = AdmissionForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        admission = Admission(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            address=form.address.data,
            department_id=form.department_id.data,
            previous_school=form.previous_school.data,
            grade_applying=form.grade_applying.data
        )
        db.session.add(admission)
        db.session.commit()
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('admission.html', form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = AdminUser.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            session['is_superadmin'] = admin.is_superadmin
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'students': Student.query.count(),
        'teachers': Teacher.query.count(),
        'departments': Department.query.count(),
        'notices': Notice.query.count(),
        'events': Event.query.count(),
        'admissions': Admission.query.filter_by(status='pending').count(),
        'messages': ContactMessage.query.filter_by(is_read=False).count()
    }
    recent_admissions = Admission.query.order_by(Admission.applied_date.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_admissions=recent_admissions, recent_messages=recent_messages)


@app.route('/admin/students')
@login_required
def admin_students():
    page = request.args.get('page', 1, type=int)
    students_list = Student.query.order_by(Student.first_name).paginate(page=page, per_page=20)
    return render_template('admin/students.html', students=students_list)


@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
def admin_add_student():
    form = StudentForm()
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        photo = save_file(form.photo.data) if form.photo.data else None
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            address=form.address.data,
            department_id=form.department_id.data if form.department_id.data else None,
            photo=photo
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin/student_form.html', form=form, title='Add Student')


@app.route('/admin/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.email = form.email.data
        student.phone = form.phone.data
        student.date_of_birth = form.date_of_birth.data
        student.gender = form.gender.data
        student.address = form.address.data
        student.department_id = form.department_id.data if form.department_id.data else None
        if form.photo.data:
            photo = save_file(form.photo.data)
            if photo:
                student.photo = photo
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin_students'))
    form.department_id.data = student.department_id or 0
    return render_template('admin/student_form.html', form=form, title='Edit Student', student=student)


@app.route('/admin/students/delete/<int:id>')
@login_required
def admin_delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/teachers')
@login_required
def admin_teachers():
    page = request.args.get('page', 1, type=int)
    teachers_list = Teacher.query.order_by(Teacher.first_name).paginate(page=page, per_page=20)
    return render_template('admin/teachers.html', teachers=teachers_list)


@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
def admin_add_teacher():
    form = TeacherForm()
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        photo = save_file(form.photo.data) if form.photo.data else None
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            qualification=form.qualification.data,
            address=form.address.data,
            department_id=form.department_id.data if form.department_id.data else None,
            photo=photo
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('admin_teachers'))
    return render_template('admin/teacher_form.html', form=form, title='Add Teacher')


@app.route('/admin/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    form = TeacherForm(obj=teacher)
    form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data
        teacher.phone = form.phone.data
        teacher.qualification = form.qualification.data
        teacher.address = form.address.data
        teacher.department_id = form.department_id.data if form.department_id.data else None
        if form.photo.data:
            photo = save_file(form.photo.data)
            if photo:
                teacher.photo = photo
        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('admin_teachers'))
    form.department_id.data = teacher.department_id or 0
    return render_template('admin/teacher_form.html', form=form, title='Edit Teacher', teacher=teacher)


@app.route('/admin/teachers/delete/<int:id>')
@login_required
def admin_delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('admin_teachers'))


@app.route('/admin/departments')
@login_required
def admin_departments():
    dept_list = Department.query.all()
    return render_template('admin/departments.html', departments=dept_list)


@app.route('/admin/departments/add', methods=['GET', 'POST'])
@login_required
def admin_add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        dept = Department(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            head=form.head.data
        )
        db.session.add(dept)
        db.session.commit()
        flash('Department added successfully!', 'success')
        return redirect(url_for('admin_departments'))
    return render_template('admin/department_form.html', form=form, title='Add Department')


@app.route('/admin/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_department(id):
    dept = Department.query.get_or_404(id)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        dept.name = form.name.data
        dept.code = form.code.data
        dept.description = form.description.data
        dept.head = form.head.data
        db.session.commit()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('admin_departments'))
    return render_template('admin/department_form.html', form=form, title='Edit Department', department=dept)


@app.route('/admin/departments/delete/<int:id>')
@login_required
def admin_delete_department(id):
    dept = Department.query.get_or_404(id)
    if dept.students or dept.teachers:
        flash('Cannot delete department with associated students or teachers', 'danger')
        return redirect(url_for('admin_departments'))
    db.session.delete(dept)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('admin_departments'))


@app.route('/admin/notices')
@login_required
def admin_notices():
    page = request.args.get('page', 1, type=int)
    notices_list = Notice.query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/notices.html', notices=notices_list)


@app.route('/admin/notices/add', methods=['GET', 'POST'])
@login_required
def admin_add_notice():
    form = NoticeForm()
    if form.validate_on_submit():
        notice = Notice(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            is_published=form.is_published.data
        )
        db.session.add(notice)
        db.session.commit()
        flash('Notice added successfully!', 'success')
        return redirect(url_for('admin_notices'))
    return render_template('admin/notice_form.html', form=form, title='Add Notice')


@app.route('/admin/notices/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_notice(id):
    notice = Notice.query.get_or_404(id)
    form = NoticeForm(obj=notice)
    if form.validate_on_submit():
        notice.title = form.title.data
        notice.content = form.content.data
        notice.category = form.category.data
        notice.is_published = form.is_published.data
        db.session.commit()
        flash('Notice updated successfully!', 'success')
        return redirect(url_for('admin_notices'))
    return render_template('admin/notice_form.html', form=form, title='Edit Notice', notice=notice)


@app.route('/admin/notices/delete/<int:id>')
@login_required
def admin_delete_notice(id):
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('admin_notices'))


@app.route('/admin/events')
@login_required
def admin_events():
    page = request.args.get('page', 1, type=int)
    events_list = Event.query.order_by(Event.start_date.desc()).paginate(page=page, per_page=20)
    return render_template('admin/events.html', events=events_list)


@app.route('/admin/events/add', methods=['GET', 'POST'])
@login_required
def admin_add_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            color=form.color.data or '#3788d8',
            is_public=form.is_public.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/event_form.html', form=form, title='Add Event')


@app.route('/admin/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_event(id):
    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.location = form.location.data
        event.color = form.color.data
        event.is_public = form.is_public.data
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/event_form.html', form=form, title='Edit Event', event=event)


@app.route('/admin/events/delete/<int:id>')
@login_required
def admin_delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin_events'))


@app.route('/admin/admissions')
@login_required
def admin_admissions():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Admission.query
    if status:
        query = query.filter_by(status=status)
    admissions_list = query.order_by(Admission.applied_date.desc()).paginate(page=page, per_page=20)
    return render_template('admin/admissions.html', admissions=admissions_list)


@app.route('/admin/admissions/<int:id>/status/<string:status>')
@login_required
def admin_update_admission_status(id, status):
    admission = Admission.query.get_or_404(id)
    if status in ['pending', 'approved', 'rejected']:
        admission.status = status
        db.session.commit()
        flash(f'Admission status updated to {status}', 'success')
    return redirect(url_for('admin_admissions'))


@app.route('/admin/admissions/delete/<int:id>')
@login_required
def admin_delete_admission(id):
    admission = Admission.query.get_or_404(id)
    db.session.delete(admission)
    db.session.commit()
    flash('Admission deleted successfully!', 'success')
    return redirect(url_for('admin_admissions'))


@app.route('/admin/messages')
@login_required
def admin_messages():
    page = request.args.get('page', 1, type=int)
    messages_list = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/messages.html', messages=messages_list)


@app.route('/admin/messages/read/<int:id>')
@login_required
def admin_mark_read(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for('admin_messages'))


@app.route('/admin/messages/delete/<int:id>')
@login_required
def admin_delete_message(id):
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/api/events')
def api_events():
    events = Event.query.filter_by(is_public=True).all()
    events_list = []
    for e in events:
        events_list.append({
            'id': e.id,
            'title': e.title,
            'start': e.start_date.strftime('%Y-%m-%d'),
            'end': e.end_date.strftime('%Y-%m-%d'),
            'color': e.color,
            'description': e.description,
            'location': e.location
        })
    return {'events': events_list}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not AdminUser.query.filter_by(username='admin').first():
            admin = AdminUser(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@school.com',
                is_superadmin=True
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5000)
