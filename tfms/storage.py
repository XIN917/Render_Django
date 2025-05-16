# tfms/storage.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class StaticS3Boto3Storage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        if settings.MINIO_ACCESS_URL:
            self.secure_urls = False
            self.custom_domain = settings.MINIO_ACCESS_URL
        super().__init__(*args, **kwargs)

class S3MediaStorage(S3Boto3Storage):
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        if settings.MINIO_ACCESS_URL:
            self.secure_urls = False
            self.custom_domain = settings.MINIO_ACCESS_URL
        super().__init__(*args, **kwargs)

