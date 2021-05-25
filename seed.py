import requests
from app import db
from models import Country, Language, Currency, CountryCurrency, CountryLanguage

API_BASE_URL = 'https://restcountries.eu/rest/v2'

countries = []
languages = []
currencies = []
country_language = []
country_currency = []
    
def seed_all():
    url = f'{API_BASE_URL}/all'
    response = requests.get(url)
    for data in response.json():
        add_to_data_load(data)
    add_to_db()

def seed_one(country):
    url = f'{API_BASE_URL}/alpha/{country}'
    response = requests.get(url)
    data = response.json()
    add_to_data_load(data)
    add_to_db()

def add_to_data_load(data):
    country = Country(
        code = data.get('alpha2Code'),
        name = data.get('name'),
        capital = data.get('capital'),
        region = data.get('region'),
        subregion = data.get('subregion'),
        population = data.get('population'),
        flag = data.get('flag'),
    )
    if country not in countries:
        countries.append(country)

    for language_data in data.get('languages'):
        language = Language(
            code = language_data.get('iso639_2'),
            name = language_data.get('name')
        )
        if language not in languages:
            languages.append(language)
        country_language.append(CountryLanguage(country_code=country.code, language_code=language.code))
    
    for currency_data in data.get('currencies'):
        if currency := validate_currency(currency_data):
            if currency not in currencies:
                currencies.append(currency)
            country_currency.append(CountryCurrency(country_code=country.code, currency_code=currency.code))

def validate_currency(data):
    try:
      code = data.get('code')
      if code == 'null' or code == None or code == '(none)':
          return False
      return Currency(
        code=code,
        name = data.get('name')
      )
    except:
        return False

def add_to_db():
    db.session.add_all(countries)
    db.session.add_all(languages)
    db.session.add_all(currencies)
    db.session.commit()
    db.session.add_all(country_language)
    db.session.add_all(country_currency)
    db.session.commit()

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    seed_all()
    # seed_one('AF')
    # seed_one('US')
    # seed_one('AU')
    # seed_one('ZW')
    # seed_one('MY')
    # seed_one('VG')
    # seed_one('NR')
    # seed_one('PN')