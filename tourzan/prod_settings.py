import os
DEBUG = False
ALLOWED_HOSTS = ['*']
ON_PRODUCTION = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'testingdb',
        'USER': 'tourzandbuser',
        'PASSWORD': 'TourzanTravellingP@s$',
        'HOST': 'touzandb.cgeysenvqij7.us-west-2.rds.amazonaws.com',
        'PORT': '',                      # Set to empty string for default.
    }
}

#for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'tourzan.storage_backends.PublicMediaStorageSameLocation'

AWS_ACCESS_KEY_ID = 'AKIAJIYAQ123455'
AWS_SECRET_ACCESS_KEY = 'JC3Lpupjl8pDP/Z2sVQch/1/2/3/4/5'
AWS_STORAGE_BUCKET_NAME = 'tourzan'

AWS_S3_FILE_OVERWRITE = False #to append extra characters to the file with the same name as existing file
AWS_S3_ENCRYPTION = True

"""19.01.2020 Important: without AWS_S3_CUSTOM_DOMAIN images without custom media url replacing do not
form the correct url."""
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_PRIVATE_MEDIA_LOCATION = "media/private"

MEDIA_URL = 'https://d3n77qih6h0cff.cloudfront.net/'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AXES_BEHIND_REVERSE_PROXY = True

#Getting Braintree credentials on Production
BRAINTREE_MERCHANT_ID = os.environ.get('BRAINTREE_MERCHANT_ID', '')
BRAINTREE_PUBLIC_KEY = os.environ.get('BRAINTREE_PUBLIC_KEY', '')
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY', '')

PAYMENT_RAILS_KEY = os.environ.get('PAYMENT_RAILS_KEY', '')
PAYMENT_RAILS_SECRET = os.environ.get('PAYMENT_RAILS_SECRET', '')

FROM_EMAIL = "noreply@tourzan.com"

ONFIDO_TOKEN = os.environ.get('ONFIDO_TOKEN', 'live_ZGcfPjhQQg9u1PbNxJktE1-2-3-4')
ONFIDO_IS_TEST_MODE = os.environ.get('ONFIDO_IS_TEST_MODE ', False)
