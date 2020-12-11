from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, DecimalField, FloatField, RadioField, DateField, BooleanField
from wtforms.validators import Optional, ValidationError, DataRequired, Length, NumberRange

from helpers import FlexibleFloatField

class FinnaForm(FlaskForm):
    target = SelectField('Haun kohdekenttä', 
                         choices=[('author', 'Kirjailija'), 
                         ('title', 'Kirjan nimi')])
    language = SelectField('Teosten kieli', 
                         choices=[('fin', 'Suomi'), 
                         ('eng', 'Englanti'), 
                         ('swe', 'Ruotsi'),
                         ('all', 'Kaikki')])

    search_term = StringField('Hakusana(t):', validators=[DataRequired()])
    submit = SubmitField('Hae')

class PlottingForm(FlaskForm):
    const = FlexibleFloatField('Vakio', default=0, validators=[Optional()])
    x1 = FlexibleFloatField('X', default=0, validators=[Optional()])
    x2 = FlexibleFloatField('X2', default=0, validators=[Optional()])
    x3 = FlexibleFloatField('X3', default=0, validators=[Optional()])
    x4 = FlexibleFloatField('X4', default=0, validators=[Optional()])

    submit = SubmitField('Piirrä')