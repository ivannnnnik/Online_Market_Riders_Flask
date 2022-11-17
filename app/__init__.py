from flask import Flask
from app import template_filters


app = Flask(__name__)
template_filters.init_app(app)
app.debug = True
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'hfdfvhdbvhdvlfvfb7_bgfbfv_'

from app import views

