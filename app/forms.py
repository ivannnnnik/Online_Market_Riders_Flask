from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length
import email_validator
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename


# class SearchProducts(FlaskForm):
#     name_product = StringField(validators=[DataRequired()])
#     submit = SubmitField("Найти")

class RegistrForm(FlaskForm):
    username = StringField("Имя: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Email()])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=8, max=25)])
    submit = SubmitField("Отправить")


class AuthForm(FlaskForm):
    email = StringField("Email: ", validators=[Email('Некорректный Email')])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                     Length(min=8,
                                                            max=25,
                                                            message='Пароль должен быть от 8 до 25 символов')
                                                     ]
                             )
    remember = BooleanField('Запомнить меня: ')
    submit = SubmitField("Отправить")

    class UpdateUserForm(FlaskForm):
        email = StringField("Email: ", validators=[Email('Некорректный Email')])
        old_password = PasswordField("Старый пароль: ", validators=[DataRequired(),
                                                             Length(min=8,
                                                                    max=25,
                                                                    message='Пароль должен быть от 8 до 25 символов')
                                                             ]
                                     )
        new_password = PasswordField("Новый пароль: ", validators=[DataRequired(),
                                                             Length(min=8,
                                                                    max=25,
                                                                    message='Пароль должен быть от 8 до 25 символов')
                                                             ]
                                     )
        submit = SubmitField("Изменить данные")


class CreateProduct(FlaskForm):
    name = StringField("Название: ", validators=[DataRequired()])
    text = TextAreaField("Описание: ", validators=[DataRequired()])
    price = IntegerField('Цена: ', validators=[DataRequired()])
    photo = FileField('Картинка: ', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])
    count = IntegerField('Количество: ', validators=[DataRequired()])
    type_product = StringField("Тип товара: ", validators=[DataRequired()])
    submit = SubmitField("Отправить")
