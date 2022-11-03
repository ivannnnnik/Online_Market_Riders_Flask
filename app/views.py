# -*- encoding: utf-8 -*-


from flask import render_template, request
from jinja2 import TemplateNotFound
from app import app
from app import db_util
from werkzeug.security import generate_password_hash, check_password_hash
from app import forms

# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from UserLogin import UserLogin

db = db_util.Database()


# login_manager = LoginManager(app)


@app.route('/')
def index():
    return render_template('index.html', title='Главная')


@app.route('/registration', methods=['POST', 'GET'])
def register():
    form = forms.RegistrForm()
    result = None
    error = None
    if request.method == 'POST':
        username = request.form.get('username'),
        email = request.form.get('email')
        password = request.form.get('password')
        print(username)
        result = db.create_user(username[0], email, generate_password_hash(password))
        if result is False:
            status = 'Пользователь с Email уже существует !'
            return render_template('accounts/register.html', form=form, status=status)
        else:
            if result is True:
                status = 'Вы успешно зарегистрировались !'
                return render_template('accounts/login.html', form=form, status=status)
    return render_template('accounts/register.html', form=form)


@app.route('/authorization', methods=['POST', 'GET'])
def login():
    form = forms.AuthForm()
    result = False
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        result = db.is_authenticated(email, password)
        if result is False:
            status = 'Вы ввели неверные данные !'
            return render_template('accounts/login.html', form=form, status=status)
        else:
            if result is True:
                status = None
                return render_template('index.html', form=form, status=status)
    return render_template('accounts/login.html', form=form)


@app.route('/new_product')
def new_product():
    return render_template('new_product.html')


@app.route('/favourite')
def favourite_user():
    return render_template('favourite.html')


@app.route('/cart')
def cart_user():
    return render_template('cart.html')


@app.route('/profile')
def profile_user():
    return render_template('profile.html')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена !')


if __name__ == '__main__':
    app.run(debug=True)
