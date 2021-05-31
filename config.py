'''Flask config'''
import os
import re

############################################
# General
SECRET_KEY = os.environ.get('SECRET_KEY', "yKwxyju9bYpbWcwTQiFotjgMLpoIcoM-rMmk4QYWKQQ")

############################################
# SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql:///travel')
if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

############################################
# DebugToolbar
DEBUG_TB_INTERCEPT_REDIRECTS = False