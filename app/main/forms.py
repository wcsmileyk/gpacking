from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email
from ..models import User, Closet
from flask_login import current_user


class MultipleCheckBox(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


class CreatePackingList(FlaskForm):
    name = StringField('Packing List Name', validators=[DataRequired()])
    activity = SelectField('What activity is this for?', coerce=int)
    items = SelectMultipleField('Which Items are you bringing?', coerce=int)


class CreateGroup(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    activity = SelectField('What activity is this for?', coerce=int)
    friends = SelectMultipleField('Add friends', coerce=int)
    items = SelectMultipleField('Which items are you brining?', coerce=int)
    shared_items = SelectMultipleField('Which items are you sharing with the group?', coerce=int)


class UpdateGroupList(FlaskForm):
    name = StringField('Item')
    category = SelectField('Category', coerce=int)
    type = SelectField('Type', coerce=int)
    weight = IntegerField('Weight (grams)')
    items = SelectMultipleField('Which Items?', coerce=int)


class AddItem(FlaskForm):
    name = StringField('Item', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    type = SelectField('Type', coerce=int, validators=[DataRequired()])
    weight = IntegerField('Weight (grams)')


class FriendRequest(FlaskForm):
    user_email = StringField('Add by email')
    username = StringField('Add by username')








