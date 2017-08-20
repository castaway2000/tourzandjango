ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'realtestingdb',
        'USER': 'testingdb',
        'PASSWORD': 'TourzanTesting12#$',
        'HOST': 'testingdb.cgeysenvqij7.us-west-2.rds.amazonaws.com',
        'PORT': '',                      # Set to empty string for default.
    }
}

#for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = 'AKIAJE5BFN42CHVOOZJA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'tourzan-testing'

AWS_S3_FILE_OVERWRITE = True #to append extra characters to the file with the same name as existing file
AWS_S3_ENCRYPTION = True


MEDIA_URL = 'https://tourzan-testing.s3.amazonaws.com/'

# AXES_BEHIND_REVERSE_PROXY = True