# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import Utente

class RegistrationForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    cognome = StringField('Cognome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrati')

    def validate_email(self, email):
        user = Utente.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Questa email è già registrata. Usa un\'altra email.')
