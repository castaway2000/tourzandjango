import os
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

#for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = 'AKIAJIYAQ4HEEI6HHQ3Q'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'tourzan'

AWS_S3_FILE_OVERWRITE = True #to append extra characters to the file with the same name as existing file
AWS_S3_ENCRYPTION = True

MEDIA_URL = 'https://tourzan.s3.amazonaws.com/'

AXES_BEHIND_REVERSE_PROXY = True

#Getting Braintree credentials on Production
BRAINTREE_MERCHANT_ID = os.environ.get('BRAINTREE_MERCHANT_ID', '')
BRAINTREE_PUBLIC_KEY = os.environ.get('BRAINTREE_PUBLIC_KEY', '')
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY', '')

PAYMENT_RAILS_KEY = os.environ.get('PAYMENT_RAILS_KEY', '')
PAYMENT_RAILS_SECRET = os.environ.get('PAYMENT_RAILS_SECRET', '')

FROM_EMAIL = "noreply@tourzan.com"
