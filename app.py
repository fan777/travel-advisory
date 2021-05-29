import os
import requests
import requests_cache

from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, connect_db, Country, Language, Currency, CountryCurrency, CountryLanguage, User
from forms import RegisterForm, LoginForm
from key_file import API_SECRET_KEY_DETAIL_ADIVSORY
from sqlalchemy.exc import IntegrityError
from requests.exceptions import Timeout

API_BASE_URL_SIMPLE_ADVISORY = 'https://www.travel-advisory.info/api'
API_BASE_URL_DETAIL_ADVISORY = 'https://api.tugo.com/v1/travelsafe'
API_BASE_URL_COVID = 'https://disease.sh/v3/covid-19'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///travel'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "tangobananaredchopper")

connect_db(app)

requests_cache.install_cache(cache_name='travel_cache', backend='sqlite', expire_after=86400)

@app.route('/')
def homepage():
    '''Show homepage.'''
    countries = Country.query.filter(Country.region != '').all()
    return render_template('countries/all.html', countries=countries)

@app.route('/country/<country_code>')
def country(country_code):
    country = Country.query.get_or_404(country_code)
    advisory = get_basic_advisory(country_code)
    covid = get_covid_stats(country_code)
    detailed = get_detailed_advisory(country_code)
    return render_template('countries/single.html', country=country, advisory=advisory, covid=covid, detailed=detailed)

def get_basic_advisory(country_code):
    url = f'{API_BASE_URL_SIMPLE_ADVISORY}'
    try:
      response = requests.get(url, params={'countrycode': country_code})
      data = response.json().get('data').get(country_code).get('advisory')
      return dict([
        ('score', data.get('score')),
        ('message', data.get('message')),
        ('updated', data.get('updated')),
        ('source', data.get('source'))
      ])
    except:
      return dict([
        ('error', 'Advisory for this country not found.')
      ])

def get_covid_stats(country_code):
    url = f'{API_BASE_URL_COVID}/countries/{country_code}'
    try:
      response = requests.get(url)
      data = response.json()
      if response.status_code == 404:
        raise Exception()
      return dict([
        ('cases', data.get('cases')),
        ('deaths', data.get('deaths')),
        ('recovered', data.get('recovered')),
        ('active', data.get('active')),
        ('critical', data.get('critical'))
      ])
    except:
      return dict([
        ('error', 'Statistics for this country not found.')
      ])

def get_detailed_advisory(country_code):
    url = f'{API_BASE_URL_DETAIL_ADVISORY}/countries/{country_code}'
    try:
      headers = {'X-Auth-API-Key': API_SECRET_KEY_DETAIL_ADIVSORY}
      response = requests.get(url, headers=headers, timeout=10)
      data = response.json()
      return dict([
        ('climate', data.get('climate')),
        ('health', data.get('health')),
        ('lawAndCulture', data.get('lawAndCulture'))
      ])
    except Timeout as ex:
      return dict([
        ('error', 'API service timed out.')
      ])
    except:
      return dict([
        ('error', 'Additional considerations for this country not found.')
      ])

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        new_user = User.register(username, password, email)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Pelase pick another')
            return render_template('users/register.html', form=form)
        session['user_id'] = new_user.username
        return redirect(f'/')
    return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if 'user_id' in session:
        return redirect(f"/")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.username
            return redirect(f'/')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('users/login.html', form=form)

@app.route('/users/<username>/delete', methods=['GET', 'POST'])
def delete_user(username):
    if 'user_id' not in session or username != session['user_id']:
        return redirect('/login')

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    return redirect('/login')

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/')