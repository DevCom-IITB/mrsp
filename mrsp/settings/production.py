from decouple import config

from .base import *

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "gymkhana.iitb.ac.in"
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config("MRSP_test"),
        'USER':config('DB_USER'), 
	'PASSWORD': config("DB_PASSWD"), 
	'HOST':'mysql',
    }
}