import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) #loading environmental files

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neverguessit'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']

    POSTS_PER_PAGE = 5

    LANGUAGES = ['en', 'dk'] #pybabel languages supported

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') #Microsoft Azure text translator key

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') #Where is elastic search hosted

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

if __name__ == '__main__':
    print(basedir)