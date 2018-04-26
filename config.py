import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'config.env')) #loading environmental files

print('The base directory is:')
print(basedir)
print(os.path.join(basedir, 'config.env'))



class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neverguessit lalalal yoyo mejeriprodukter ginsmagning'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nicolaj.schmit@gmail.com']

    POSTS_PER_PAGE = 5
    BLOG_POSTS_PER_PAGE = 5

    LANGUAGES = ['en', 'dk'] #pybabel languages supported

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') #Microsoft Azure text translator key

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') #Where elastic search is hosted

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # Flask-User settings
    USER_APP_NAME = "NicoWorld Flask App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

    RECAPTCHA_PUBLIC_KEY= os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY= os.environ.get('RECAPTCHA_PRIVATE_KEY')


if __name__ == '__main__':
    print(basedir)