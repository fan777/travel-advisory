import os

from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, connect_db, Country, Language, Currency, CountryCurrency, CountryLanguage

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///travel'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "tangobananaredchopper")

connect_db(app)

@app.route('/')
def homepage():
    '''Show homepage.'''
    return render_template('index.html')