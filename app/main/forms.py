from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired
from ..models import User, Closet
from flask_login import current_user


class CreatePackingList(FlaskForm):
    name = StringField('Closet Name', validators=[DataRequired()])
    primary = BooleanField('Is this your main closet?')
    activity = SelectField('What activity is this for?', coerce=int)


class UpdateCloset(FlaskForm):
    name = StringField('Item', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    type = SelectField('Type', coerce=int, validators=[DataRequired()])
    weight = IntegerField('Weight (kgs)')





