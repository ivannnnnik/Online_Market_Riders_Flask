# -*- encoding: utf-8 -*-


from flask import render_template, request, redirect, url_for, flash
from jinja2 import TemplateNotFound
from app import app
from app import db_util
from werkzeug.security import generate_password_hash, check_password_hash
from app import forms

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app.UserLogin import UserLogin

db = db_util.Database()
login_manager = LoginManager(app)
app.debug = True

login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, авторизуйтесь для продолжения'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().from_db(user_id, db)


@app.route('/')
def index():
    is_auth = current_user.is_authenticated
    print(is_auth)
    return render_template('index.html', is_auth=is_auth)


@app.route('/registration', methods=['POST', 'GET'])
def register():
    form = forms.RegistrForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        print(type(username))
        result = db.create_user(username, email, generate_password_hash(password))
        if result is False:
            status = 'Пользователь с Email уже существует !'
            return render_template('accounts/register.html', form=form, status=status)
        else:
            if result is True:
                status = 'Вы успешно зарегистрировались !'
                return redirect(url_for('login'))
    return render_template('accounts/register.html', form=form)


@app.route('/authorization', methods=['POST', 'GET'])
def login():
    form = forms.AuthForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = db.get_user_by_email(email)
        print(user)
        if user:
            if check_password_hash(user[0]['password'], password):
                user_login = UserLogin().create(user)
                rm = remember
                login_user(user_login, remember=rm)
                return redirect(url_for('index'))
            else:
                status = 'Вы ввели неверные данные !'
                return render_template('accounts/login.html', form=form, status=status)
        else:
            status = 'Вы не зарегистрировались !'
            return render_template('accounts/login.html', form=form, status=status)
    else:
        pass
    return render_template('accounts/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта !')
    return render_template('index.html')


@app.route('/new_product')
@login_required
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
    user_id = current_user.get_id()
    user_data = db.get_user(user_id)[0]
    context = {
        'username': user_data['name'],
        'email': user_data['email']
    }
    return render_template('profile.html', context=context)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена !')


if __name__ == '__main__':
    app.run(debug=True)
