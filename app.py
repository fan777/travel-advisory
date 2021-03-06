import os
import requests
import requests_cache

from flask import Flask, render_template, jsonify, request, flash, redirect, session, g
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
    g.countries = Country.query.all()

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user signup."""
    do_logout()
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(form.username.data, form.password.data, form.email.data)
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)
        do_login(user)
        flash("Account created!", 'success')
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
    return render_template('country/list.html')

######################################################
# Country list / single / bookmark

@app.route('/country/<country_code>')
def country(country_code):
    if not [country for country in g.countries if country.code == country_code]:
        flash(f'{country_code} is an invalid country code', 'danger')
        return redirect('/')
    country = Country.query.get(country_code)
    advisory = get_basic_advisory(country_code)
    covid = get_covid_stats(country_code)
    detailed = get_detailed_advisory(country_code)
    return render_template('country/country.html', country=country, advisory=advisory, covid=covid, detailed=detailed)  

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

@app.route('/country/<country_code>/covid_data')
def country_covid(country_code):
    return jsonify(get_covid_graph_data(country_code))

######################################################
# Additional routes

@app.errorhandler(404)
def page_not_found(e):
    flash("404 error! Page or route not found.", "danger")
    return redirect('/')

######################################################
# API calls

def get_basic_advisory(country_code):
    url = f'{API_BASE_URL_TA}'
    try:
        response = requests.get(url, timeout=8, params={'countrycode': country_code})
        data = response.json().get('data').get(country_code).get('advisory')
        return dict([
            ('score', data.get('score')),
            ('message', data.get('message')),
            ('updated', data.get('updated')),
            ('source', data.get('source'))
        ])
    except Timeout as ex:
        return dict([
            ('error', 'API service timed out.')
        ])
    except:
        return dict([
            ('error', 'Advisory for this country not found.')
        ])

def get_covid_stats(country_code):
    url = f'{API_BASE_URL_COVID}/countries/{country_code}'
    try:
        response = requests.get(url, timeout=8)
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
    except Timeout as ex:
        return dict([
            ('error', 'API service timed out.')
        ])
    except:
        return dict([
            ('error', 'Statistics for this country not found.')
        ])

def get_covid_graph_data(country_code):
    url = f'{API_BASE_URL_COVID}/historical/{country_code}?lastdays=182'
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        if response.status_code == 404:
            raise Exception()
        values = data.get('timeline').get('cases').values()
        keys = data.get('timeline').get('cases').keys()
        return dict([
            ('data', list(values)),
            ('labels', list(keys))
        ])
    except Timeout as ex:
        return dict([
            ('error', 'API service timed out.')
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
