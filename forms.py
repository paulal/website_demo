from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, RadioField, DateField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange


class FinnaForm(FlaskForm):
    target = SelectField('Haun kohdekenttä', 
                         choices=[('all', 'Kaikki kentät'), 
                         ('author', 'Kirjailija'), 
                         ('title', 'Kirjan nimi')])
    language = SelectField('Teosten kieli', 
                         choices=[('fin', 'Suomi'), 
                         ('eng', 'Englanti'), 
                         ('swe', 'Ruotsi'),
                         ('all', 'Kaikki')])

    search_term = StringField('Hakusana(t):', validators=[DataRequired()])
    submit = SubmitField('Lähetä')