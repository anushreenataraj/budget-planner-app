from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FileField,IntegerField
from wtforms.fields.core import DateField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from budgetapp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Department Name', choices=['--','Admin', 'Operations', 'Marketing', 'Sales'])
    dep_num= SelectField('Inter Department', choices=['--','Dep-Admin','Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3','Marketing-Dep:1', 'Marketing-Dep:2', 'Marketing-Dep:3','Sales-Dep:1', 'Sales-Dep:2', 'Sales-Dep:3'])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email is taken. Please choose a different one.')

class RegistrationForm_Ope(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dep_num= SelectField('Inter Department', choices=['--','Dep-Admin','Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3'])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')  
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email is taken. Please choose a different one.')

class RegistrationForm_Mar(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dep_num= SelectField('Inter Department', choices=['--','Dep-Admin','Marketing-Dep:1', 'Marketing-Dep:2', 'Marketing-Dep:3'])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')  
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email is taken. Please choose a different one.')

class RegistrationForm_Sal(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dep_num= SelectField('Inter Department', choices=['--','Dep-Admin','Sales-Dep:1', 'Sales-Dep:2', 'Sales-Dep:3'])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email is taken. Please choose a different one.')
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('The username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('The email is taken. Please choose a different one.')
class DeleteAccountForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if not user:
                raise ValidationError('Account associated with this email address do not exist!')

class CheckAccountForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Check')

class UploadForm(FlaskForm):
    file = FileField()
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y")
    submit = SubmitField('Upload')

class DeleteDataForm(FlaskForm):
    department = SelectField('Department Name',choices=['--','Operations', 'Marketing', 'Sales'], validators=[DataRequired()])
    dep_num = SelectField('Inter Department Name',choices=['--','Dep-Admin','Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3','Marketing-Dep:1', 'Marketing-Dep:2', 'Marketing-Dep:3','Sales-Dep:1', 'Sales-Dep:2', 'Sales-Dep:3'],validators=[DataRequired()])
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y", validators=[DataRequired()])
    submit = SubmitField('Delete')
class DeleteDataForm_Ope(FlaskForm):
    dep_num = SelectField('Inter Department Name',choices=['--','Dep-Admin','Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3'],validators=[DataRequired()])
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y", validators=[DataRequired()])
    submit = SubmitField('Delete')
class DeleteDataForm_Mar(FlaskForm):
    dep_num = SelectField('Inter Department Name',choices=['--','Dep-Admin','Marketing-Dep:1', 'Marketing-Dep:2', 'Marketing-Dep:3'],validators=[DataRequired()])
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y", validators=[DataRequired()])
    submit = SubmitField('Delete')
class DeleteDataForm_Sal(FlaskForm):
    dep_num = SelectField('Inter Department Name',choices=['--','Dep-Admin','Sales-Dep:1', 'Sales-Dep:2', 'Sales-Dep:3'],validators=[DataRequired()])
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y", validators=[DataRequired()])
    submit = SubmitField('Delete')

class MonthDataForm(FlaskForm):
    type_of_file= SelectField('Type of File', choices=['Expected','Actual'],validators=[DataRequired()])
    mode= SelectField('Mode', choices=['Monthly','Quarterly','Half-yearly','Annually'])
    month = SelectField('Month',choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],validators=[DataRequired()])
    year = DateField('Year',format="%Y")
    submit1 = SubmitField('Submit')
class SalaryForm(FlaskForm):
    file = FileField()
    submit = SubmitField('Submit')
