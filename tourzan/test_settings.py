import os
DEBUG = False
ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'realtestingdb',
        'USER': 'testingdb',
        'PASSWORD': 'TourzanTesting12#$',
        'HOST': 'testingdb.cgeysenvqij7.us-west-2.rds.amazonaws.com',
        'PORT': '',                      # Set to empty string for default.
    }
}

#for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'tourzan.storage_backends.PublicMediaStorageSameLocation'

AWS_ACCESS_KEY_ID = 'AKIAJE5BFN42CHVOOZJA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'tourzan-testing'

AWS_S3_FILE_OVERWRITE = False #to append extra characters to the file with the same name as existing file
AWS_S3_ENCRYPTION = True

# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_PRIVATE_MEDIA_LOCATION = "media/private"

MEDIA_URL = 'https://d3lcm1fnjqs9jv.cloudfront.net/'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}


AXES_BEHIND_REVERSE_PROXY = True

BRAINTREE_ENV = 'Sandbox'
BRAINTREE_MERCHANT_ID = os.environ.get('BRAINTREE_MERCHANT_ID', '')
BRAINTREE_PUBLIC_KEY = os.environ.get('BRAINTREE_PUBLIC_KEY', '')
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY', '')

PAYMENT_RAILS_KEY = os.environ.get('PAYMENT_RAILS_KEY', '')
PAYMENT_RAILS_SECRET = os.environ.get('PAYMENT_RAILS_SECRET', '')

FROM_EMAIL = "noreply@tourzan.com"

ONFIDO_TOKEN = os.environ.get('ONFIDO_TOKEN', 'test_tLlvRsGwFHHBHZr_mw02f372SkQwFAb3')
ONFIDO_IS_TEST_MODE = os.environ.get('ONFIDO_IS_TEST_MODE ', True)
