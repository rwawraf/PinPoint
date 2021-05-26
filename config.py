from dotenv import load_dotenv
from os import environ, path

"""
plik konfiguracyjny. konfiguracja odbywa sie za pomoca obiektow.
korzysta sie z niego w pliku application/__init__.py, gdzie sa importowane ustawienia
sa dwie konfiguracje do wyboru: produkcja oraz development. 
"""

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))



class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SERVER = environ.get('SERVER')

    # database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost:5432/pinpoint_db'


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    DEV_DB_NAME = "dev_pinpoint.db"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DEV_DB_NAME}'


