from storages.backends.s3boto3 import S3Boto3Storage
from . import settings


class PrivateMediaStorageSameLocation(S3Boto3Storage):
    # location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False #it is needed for adding access key to media file url