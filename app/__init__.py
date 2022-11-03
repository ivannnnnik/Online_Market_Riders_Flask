from flask import Flask

app = Flask(__name__)

app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'hfdfvhdbvhdvlfvfb7_bgfbfv_'

from app import views