import os

SECRET_KEY = 'DEBUG secret key'

ALLOWED_HOSTS = ['*']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TELEGRAM_TOKEN = '565445966:AAEMHZ0swAHLej4my2ZEthkzVIYVQAeUi9U'
