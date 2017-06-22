from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Email, DataRequired, EqualTo
from gpacking import User



class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class CreateForm(FlaskForm):
    fname = StringField('fname', validators=[DataRequired()])
    lname = StringField('lname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[
        DataRequired(), EqualTo(confirm, message='Passwords must match')])
    confirm = PasswordField('confirm', validators=[DataRequired()])

    def validate_email(self, field):
        if User.query.filter_by.
