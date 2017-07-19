DEBUG = False
ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'testingdb',
        'USER': 'tourzandbuser',
        'PASSWORD': 'TourzanTravelling12#$',
        'HOST': '176.37.92.43',
        'PORT': '',                      # Set to empty string for default.
    }
}
