from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, DataRequired, EqualTo, Length, Regexp
from wtforms import ValidationError

from gpacking.models import User


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email(), Length(1, 64)])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames have only letters, numbers, underscores or periods')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Passowrd', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email Already Registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')
