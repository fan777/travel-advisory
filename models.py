from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    code = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    capital = db.Column(db.Text)
    region = db.Column(db.Text)
    subregion = db.Column(db.Text)
    population = db.Column(db.BigInteger)
    flag = db.Column(db.Text)
    languages = db.relationship('Language', secondary='country_language', backref='countries')
    currencies = db.relationship('Currency', secondary='country_currency', backref='countries')

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    country_code = db.Column(db.Text, db.ForeignKey('countries.code', ondelete='cascade'))

class Language(db.Model):
    __tablename__ = 'languages'
    code = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    def __eq__(self, other):
        return self.code == other.code

class Currency(db.Model):
    __tablename__ = 'currencies'
    code = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    
    def __eq__(self, other):
        return self.code == other.code

class CountryLanguage(db.Model):
    __tablename__ = 'country_language'
    country_code = db.Column(db.Text, db.ForeignKey('countries.code', ondelete='cascade'), primary_key=True)
    language_code = db.Column(db.Text, db.ForeignKey('languages.code', ondelete='cascade'), primary_key=True)

class CountryCurrency(db.Model):
    __tablename__ = 'country_currency'
    country_code = db.Column(db.Text, db.ForeignKey('countries.code', ondelete='cascade'), primary_key=True)
    currency_code = db.Column(db.Text, db.ForeignKey('currencies.code', ondelete='cascade'), primary_key=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bookmarks = db.relationship('Country', secondary='bookmarks', backref='users')

    @classmethod
    def register(cls, username, password, email):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
          return user
        else:
          return False

def connect_db(app):
    db.app = app
    db.init_app(app)
