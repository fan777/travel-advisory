import os
import requests
import requests_cache

from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, connect_db, Country, Language, Currency, CountryCurrency, CountryLanguage

requests_cache.install_cache(cache_name='travel_cache', backend='sqlite', expire_after=86400)
API_BASE_URL_ADVISORY = 'https://www.travel-advisory.info/api'
API_BASE_URL_COVID = 'https://disease.sh/v3/covid-19'

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

@app.route('/country')
def countries():
    countries = Country.query.all()
    return render_template('country/index.html', countries=countries)

@app.route('/country/<country_code>')
def country(country_code):
    country = Country.query.get_or_404(country_code)
    advisory = get_basic_advisory(country_code)
    covid = get_covid_stats(country_code)
    return render_template('country/country.html', country=country, advisory=advisory, covid=covid)

def get_basic_advisory(country_code):
    url = f'{API_BASE_URL_ADVISORY}'
    response = requests.get(url, params={'countrycode': country_code})
    data = response.json().get('data').get(country_code).get('advisory')
    return dict([
      ('score', data.get('score')),
      ('message', data.get('message')),
      ('updated', data.get('updated')),
      ('source', data.get('source'))
    ])

def get_covid_stats(country_code):
    url = f'{API_BASE_URL_COVID}/countries/{country_code}'
    response = requests.get(url)
    data = response.json()
    return dict([
      ('cases', data.get('cases')),
      ('deaths', data.get('deaths')),
      ('recovered', data.get('recovered')),
      ('active', data.get('active')),
      ('critical', data.get('critical'))
    ])