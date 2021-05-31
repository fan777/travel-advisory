'''Flask config'''
import os

############################################
# General
SECRET_KEY = os.environ.get('SECRET_KEY', "yKwxyju9bYpbWcwTQiFotjgMLpoIcoM-rMmk4QYWKQQ")

############################################
# SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql:///travel')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

############################################
# DebugToolbar
DEBUG_TB_INTERCEPT_REDIRECTS = False