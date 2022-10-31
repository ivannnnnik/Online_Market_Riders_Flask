# -*- encoding: utf-8 -*-


from flask import render_template, request
from jinja2 import TemplateNotFound
from app import app


@app.route('/')
def index():
    return render_template('index.html', title='Главная')


@app.route('/registration')
def register():
    return render_template('accounts/register.html')


@app.route('/authorization')
def login():
    return render_template('accounts/login.html')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена !')


if __name__ == '__main__':
    app.run(debug=True)
