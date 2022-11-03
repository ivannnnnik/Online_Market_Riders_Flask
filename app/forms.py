from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length
import email_validator

class RegistrForm(FlaskForm):
    username = StringField("Имя: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=8, max=25)])
    submit = SubmitField("Отправить")

class AuthForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=8, max=25)])
    submit = SubmitField("Отправить")
