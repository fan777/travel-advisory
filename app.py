import os
import requests
import requests_cache

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from requests.exceptions import Timeout

from models import db, connect_db, Country, Language, Currency, CountryCurrency, CountryLanguage, User
from forms import RegisterForm, LoginForm

API_BASE_URL_TA = 'https://www.travel-advisory.info/api'
API_BASE_URL_COVID = 'https://disease.sh/v3/covid-19'
API_BASE_URL_TUGO = 'https://api.tugo.com/v1/travelsafe'
API_SECRET_KEY_TUGO = os.environ.get('API_SECRET_KEY_TUGO')
CURR_USER_KEY = 'curr_user'

app = Flask(__name__)
app.config.from_pyfile('config.py')

connect_db(app)
toolbar = DebugToolbarExtension(app)
requests_cache.install_cache(cache_name='travel_cache', backend='sqlite', expire_after=86400)

######################################################
# User signup / login / logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.before_request
def add_countries_to_g():
    g.countries = Country.query.filter(Country.region != '').all()

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    do_logout()
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(form.username.data, form.password.data, form.email.data)
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            # form.username.errors.append('Username taken.  Please pick another')
            return render_template('users/register.html', form=form)
        do_login(user)
        return redirect('/')
    return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials.", 'danger')
            # form.username.errors = ['Invalid username/password.']
    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash(f'Logged out!', 'success')
    return redirect(request.referrer)

######################################################
# Homepage

@app.route('/')
def homepage():
    '''Show homepage.'''
    return render_template('countries/index.html')

######################################################
# Country pages

@app.route('/country/<country_code>')
def country(country_code):
    country = Country.query.get_or_404(country_code)
    advisory = get_basic_advisory(country_code)
    covid = get_covid_stats(country_code)
    graph = get_covid_graph_data(country_code)
    detailed = get_detailed_advisory(country_code)
    return render_template('countries/single.html', country=country, advisory=advisory, covid=covid, graph=graph, detailed=detailed)

@app.route('/country/unbookmark/<country_code>', methods=['POST'])
def unbookmark(country_code):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    bookmarked_country = Country.query.get_or_404(country_code)
    g.user.bookmarks.remove(bookmarked_country)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/country/bookmark/<country_code>', methods=['POST'])
def bookmark(country_code):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    bookmarked_country = Country.query.get_or_404(country_code)
    g.user.bookmarks.append(bookmarked_country)
    db.session.commit()
    return redirect(request.referrer)

def get_basic_advisory(country_code):
    url = f'{API_BASE_URL_TA}'
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

def get_covid_graph_data (country_code):
    url = f'{API_BASE_URL_COVID}/historical/{country_code}?lastdays=30'
    try:
      response = requests.get(url)
      data = response.json()
      if response.status_code == 404:
        raise Exception()
      values = data.get('timeline').get('cases').values()
      labels = data.get('timeline').get('cases').keys()
      return dict([
        ('values', list(values)),
        ('labels', list(labels))
      ])
    except:
      return dict([
        ('error', 'Graph data for this country could not be computed.')
      ])

def get_detailed_advisory(country_code):
    url = f'{API_BASE_URL_TUGO}/countries/{country_code}'
    try:
      headers = {'X-Auth-API-Key': API_SECRET_KEY_TUGO}
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
