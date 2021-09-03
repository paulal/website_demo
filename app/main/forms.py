from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, DecimalField, FloatField
from wtforms.validators import Optional, ValidationError, DataRequired, NumberRange

from app.main.helpers import FlexibleFloatField, get_food_names


class FinnaForm(FlaskForm):
    target = SelectField('Haun kohdekenttä', 
                         choices=[('author', 'Kirjailija'), 
                         ('title', 'Kirjan nimi')])
    language = SelectField('Teosten kieli', 
                         choices=[('fin', 'Suomi'), 
                         ('eng', 'Englanti'), 
                         ('spa', 'Espanja'),
                         ('jpn', 'Japani'),
                         ('fre', 'Ranska'),
                         ('swe', 'Ruotsi'),
                         ('rus', 'Venäjä'),
                         ('est', 'Viro'),
                         ('all', 'Kaikki')])

    search_term = StringField('Hakusana(t):', validators=[DataRequired()])
    submit = SubmitField('Hae')
    

class PlottingForm(FlaskForm):
    const = FlexibleFloatField('Vakio', default=0, validators=[Optional()])
    x1 = FlexibleFloatField('X', default=0, validators=[Optional()])
    x2 = FlexibleFloatField('X2', default=0, validators=[Optional()])
    x3 = FlexibleFloatField('X3', default=0, validators=[Optional()])
    x4 = FlexibleFloatField('X4', default=0, validators=[Optional()])
    
    x_start = FlexibleFloatField('X-akselin arvovälin alku:', default=-5, validators=[Optional()])
    x_end = FlexibleFloatField('X-akselin arvovälin loppu:', default=5, validators=[Optional()])

    submit = SubmitField('Piirrä')
    

class NutrientForm(FlaskForm):
    food = StringField('Ruoka', validators=[DataRequired(message="Ruoka puuttuu")])
    amount = FlexibleFloatField('Määrä (grammoina)',
                                validators=[DataRequired(message="Määrä puuttuu"),
                                            NumberRange(min=0.1)])
    submit = SubmitField('Laske')