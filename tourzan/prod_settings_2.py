DEBUG = False
ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'testingdb',
        'USER': 'tourzandbuser',
        'PASSWORD': 'TourzanTravelling12#$',
        'HOST': 'touzandb.cgeysenvqij7.us-west-2.rds.amazonaws.com',
        'PORT': '',                      # Set to empty string for default.
    }
}
