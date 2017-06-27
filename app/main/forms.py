from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired
from ..models import User, Inventory
from flask_login import current_user


class CreateInventory(FlaskForm):
    name = StringField('Inventory Name', validators=[DataRequired()])
    primary = BooleanField('Is this your main inventory?')
    activity = SelectField('What activity is this for?', coerce=int)

    #TODO: Valdate that only one inventory is primary
    def validate_primary(self, field):
        pass

    #TODO Validate that inventory name is unique for this id


class UpdateInventory(FlaskForm):
    name = StringField('Item', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    type = SelectField('Type', coerce=int, validators=[DataRequired()])
    weight = IntegerField('Weight (kgs)')





