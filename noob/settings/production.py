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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'mantos.db'),
    }
}