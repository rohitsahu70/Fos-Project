from urllib.parse import urlparse
from .base import *

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else ['*']
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

redis_url = os.environ.get('REDIS_URL')
if redis_url:
    parsed_redis_url = urlparse(redis_url)
    hostname = parsed_redis_url.hostname
    port = parsed_redis_url.port
    password = parsed_redis_url.password
    ssl = parsed_redis_url.scheme == 'rediss'
    abort_connect = parsed_redis_url.query == 'abortConnect=False'
else:
    raise ValueError("REDIS_URL environment variable is not set")

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{hostname}:{port}/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': password,
            'SSL': ssl,
            'ABORT_CONNECT': abort_connect,
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# WhiteNoise configuration to serve static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure Postgres database based on connection string of the libpq
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AZURE_STORAGE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
AZURE_STORAGE_CONTAINER_NAME = os.environ['AZURE_STORAGE_CONTAINER_NAME']
