from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, PasswordField, BooleanField,
    SelectField, DateField, FileField, IntegerField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.utils.helpers import validate_phone


class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    query_type = SelectField('Inquiry Type', choices=[
        ('general', 'General Inquiry'),
        ('admission', 'Admission Information'),
        ('career', 'Career / Job Application'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ], validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])

    def validate_phone(self, field):
        if field.data and not validate_phone(field.data):
            raise ValidationError('Please enter a valid phone number.')


class AdmissionForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired(), Length(min=2, max=100)])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                         validators=[DataRequired()])
    father_name = StringField("Father's Name", validators=[DataRequired(), Length(min=2, max=100)])
    mother_name = StringField("Mother's Name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    previous_school = StringField('Previous School', validators=[Optional(), Length(max=200)])
    class_applying = SelectField('Class Applying For', choices=[
        ('nursery', 'Nursery'), ('lkg', 'LKG'), ('ukg', 'UKG'),
        ('1', 'Class 1'), ('2', 'Class 2'), ('3', 'Class 3'),
        ('4', 'Class 4'), ('5', 'Class 5'), ('6', 'Class 6'),
        ('7', 'Class 7'), ('8', 'Class 8'), ('9', 'Class 9'),
        ('10', 'Class 10'), ('11', 'Class 11'), ('12', 'Class 12'),
    ], validators=[DataRequired()])
    photo = FileField('Student Photo', validators=[Optional()])

    def validate_phone(self, field):
        if not validate_phone(field.data):
            raise ValidationError('Please enter a valid phone number.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class GalleryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('general', 'General'), ('campus', 'Campus'), ('events', 'Events'),
        ('sports', 'Sports'), ('academics', 'Academics'), ('facilities', 'Facilities'),
    ])
    is_featured = BooleanField('Featured')
    sort_order = IntegerField('Sort Order', default=0)
    image = FileField('Image', validators=[Optional()])


class NewsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    summary = TextAreaField('Summary', validators=[Optional()])
    content = TextAreaField('Content', validators=[DataRequired()])
    is_published = BooleanField('Published', default=True)
    image = FileField('Image', validators=[Optional()])


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    event_date = StringField('Event Date & Time', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    is_published = BooleanField('Published', default=True)
    image = FileField('Image', validators=[Optional()])


class FAQForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired(), Length(max=500)])
    answer = TextAreaField('Answer', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('general', 'General'), ('admissions', 'Admissions'), ('academics', 'Academics'),
        ('fees', 'Fees'), ('transport', 'Transport'), ('facilities', 'Facilities'),
    ])
    sort_order = IntegerField('Sort Order', default=0)
    is_published = BooleanField('Published', default=True)


class CareerForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=200)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    employment_type = SelectField('Type', choices=[
        ('full-time', 'Full Time'), ('part-time', 'Part Time'), ('contract', 'Contract'),
    ])
    is_active = BooleanField('Active', default=True)


class TestimonialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('student', 'Student'), ('alumni', 'Alumni')])
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = IntegerField('Rating', default=5)
    is_published = BooleanField('Published', default=True)
    photo = FileField('Photo', validators=[Optional()])


class AIFAQGeneratorForm(FlaskForm):
    school_info = TextAreaField('School Information', validators=[DataRequired(), Length(min=50)])


class AINoticeSummarizerForm(FlaskForm):
    notice = TextAreaField('Notice Content', validators=[DataRequired(), Length(min=20)])


class AIAdmissionAssistantForm(FlaskForm):
    student_age = IntegerField('Student Age', validators=[DataRequired()])
    class_applying = SelectField('Class Applying For', choices=[
        ('nursery', 'Nursery'), ('lkg', 'LKG'), ('ukg', 'UKG'),
        ('1', 'Class 1'), ('2', 'Class 2'), ('3', 'Class 3'),
        ('4', 'Class 4'), ('5', 'Class 5'), ('6', 'Class 6'),
        ('7', 'Class 7'), ('8', 'Class 8'), ('9', 'Class 9'),
        ('10', 'Class 10'), ('11', 'Class 11'), ('12', 'Class 12'),
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])


class AICareerGuidanceForm(FlaskForm):
    stream = SelectField('Stream', choices=[
        ('science', 'Science'), ('commerce', 'Commerce'), ('arts', 'Arts'),
    ], validators=[DataRequired()])


class JobApplicationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    cover_letter = TextAreaField('Cover Letter', validators=[Optional(), Length(max=3000)])
    resume = FileField('Resume', validators=[DataRequired()])

    def validate_phone(self, field):
        if field.data and not validate_phone(field.data):
            raise ValidationError('Please enter a valid phone number.')
