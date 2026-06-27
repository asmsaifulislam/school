from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, BooleanField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = TextAreaField('Address')
    department_id = SelectField('Department', coerce=int)
    photo = FileField('Photo')


class TeacherForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(max=20)])
    qualification = StringField('Qualification', validators=[Length(max=200)])
    address = TextAreaField('Address')
    department_id = SelectField('Department', coerce=int)
    photo = FileField('Photo')


class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Department Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    head = StringField('Department Head', validators=[Length(max=100)])


class NoticeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('academic', 'Academic'),
        ('exam', 'Exam'),
        ('holiday', 'Holiday'),
        ('event', 'Event'),
        ('admission', 'Admission')
    ])
    is_published = BooleanField('Published')


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=200)])
    color = StringField('Color', validators=[Length(max=7)])
    is_public = BooleanField('Public Event')


class AdmissionForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = TextAreaField('Address')
    department_id = SelectField('Department', coerce=int)
    previous_school = StringField('Previous School', validators=[Length(max=200)])
    grade_applying = StringField('Grade Applying For', validators=[Length(max=20)])


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
