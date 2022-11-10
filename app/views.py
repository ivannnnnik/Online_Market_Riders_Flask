# -*- encoding: utf-8 -*-
import json

from flask import render_template, request, redirect, url_for, flash
from jinja2 import TemplateNotFound
from app import app
from app import db_util
from werkzeug.security import generate_password_hash, check_password_hash
from app import forms
from PIL import Image
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app.UserLogin import UserLogin
import os
from werkzeug.utils import secure_filename

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
    products = db.get_products_all()
    if products:
        context = {
            'products': products,
            'count_products': len(products)

        }
        print(products)
        return render_template('index.html', **context)
    else:
        return render_template('index.html')


@app.route('/product/<int:product_id>')
def get_product(product_id):
    products = db.get_product_by_id(product_id)[0]
    print(products)
    return render_template('product.html', product=products)


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


@app.route('/new_product', methods=['POST', 'GET'])
@login_required
def new_product():
    form = forms.CreateProduct()
    if form.validate_on_submit():
        name = form.name.data
        text = form.text.data
        price = form.price.data
        count = form.count.data
        type_product = form.type_product.data
        user_id = current_user.get_id()
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        img_id = db.last_id()
        photo.save(os.path.join(
            app.root_path, 'static\img', f'{img_id}.{filename}'))

        photo_path = os.path.join('static\img', f'{img_id}.{filename}')

        result = db.create_product(name, text, price, user_id, count, type_product, photo_path)
        if result:
            status = f'Товар {name} создан !'
            return render_template('new_product.html', status=status)
        else:
            if result is False:
                status = 'Произошла ошибка'
                return render_template('new_product.html', form=form, status=status)

    return render_template('new_product.html', form=form)


@app.route('/favourite')
@login_required
def favourite_user():
    user_id = current_user.get_id()
    user_fav_products = db.user_favourites(user_id)
    status = 'В избранном ничего нет !'
    if user_fav_products:
        context = {
            'products': user_fav_products,
            'count_products': len(user_fav_products)
        }
        print(user_fav_products)
        return render_template('favourite.html', **context)
    else:
        return render_template('favourite.html', status=status)


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
