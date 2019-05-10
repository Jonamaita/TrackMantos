#Settings para producción
from .base import *
DEBUG= False
CSRF_COOKIE_SECURE=True
X_FRAME_OPTIONS='DENY'
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
#SECURE_SSL_REDIRECT=True
ALLOWED_HOSTS = ['192.168.1.168']
SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mantos',
        'USER': os.environ.get('USER_DB'),
        'PASSWORD': os.environ.get('PASSWORD_DB'),
        'HOST': 'localhost',
        'PORT': '',                      # Set to empty string for default.
    }
}