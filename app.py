import os
import requests
import requests_cache

from flask import Flask, render_template, request, flash, redirect, session, g
from requests.exceptions import Timeout
from models import db, connect_db, Country, Language, Currency, CountryCurrency, CountryLanguage
from key_file import API_SECRET_KEY_DETAIL_ADIVSORY

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
    return render_template('country/all.html', countries=countries)

@app.route('/country/<country_code>')
def country(country_code):
    country = Country.query.get_or_404(country_code)
    advisory = get_basic_advisory(country_code)
    covid = get_covid_stats(country_code)
    detailed = get_detailed_advisory(country_code)
    return render_template('country/country.html', country=country, advisory=advisory, covid=covid, detailed=detailed)

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
