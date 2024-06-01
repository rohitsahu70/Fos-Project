from urllib.parse import urlparse
from .base import *

DEBUG = os.environ['DEBUG'] == 'True'

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] \
    if 'WEBSITE_HOSTNAME' in os.environ else ['*']
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] \
    if 'WEBSITE_HOSTNAME' in os.environ else []

redis_url = os.environ['redis_url']
# Manually parse the Redis URL string
params = {}
for param in redis_url.split(','):
    key_value = param.split('=', 1)
    if len(key_value) == 2:
        params[key_value[0]] = key_value[1]
    else:
        params['hostname'] = key_value[0]

# Extract the components
hostname, port = params.get('hostname').split(':')
password = params.get('password')
abort_connect = params.get('abortConnect') == 'False'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://:{password}@{hostname}:{port}/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': password,
            'SSL': True,
            'ABORT_CONNECT': abort_connect
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




zSTATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure Postgres database based on connection string of the libpq
# Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {
    pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')
}
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
