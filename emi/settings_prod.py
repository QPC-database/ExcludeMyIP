from .settings import *

from os import makedirs
from os.path import exists

import re

from emi.secret_key import SECRET_KEY

LOG_DIR = join(BASE_DIR, 'logs')
if not exists(LOG_DIR):
	makedirs(LOG_DIR)

LOGGING['handlers']['default'] = {
	'level': 'INFO',
	'class': 'logging.FileHandler',
	'filename': join(LOG_DIR, 'django.log'),
	'formatter': 'default'
}

DEBUG = False

# Use Postfix:
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

STATIC_URL = '/static/'
STATIC_ROOT = '/home/emi/src/static-collected/'

ALLOWED_HOSTS = ('www.excludemyip.com',)

# SSL Settings:
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')