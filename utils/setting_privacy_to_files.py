import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import django
django.setup()
from user_verification.models import DocumentScan
from tourzan.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
import boto


s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = s3.get_bucket(AWS_STORAGE_BUCKET_NAME)

"""
run the script and then change set storage option to FileField as PrivateMediaStorageSameLocation and run migrate and makemigrations,
if it was not done before
"""
def make_files_private():
    docs = DocumentScan.objects.all()
    for doc in docs.iterator():
        f = doc.file
        if f:
            file_location = "%s" % f
            final_key = bucket.get_key(file_location)
            if final_key:
                # final_key.set_acl('public')
                final_key.set_acl('private')
                print("updated")

if __name__ == "__main__":
    make_files_private()
