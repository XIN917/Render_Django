from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class StaticS3Boto3Storage(S3Boto3Storage):
    location = getattr(settings, "STATICFILES_LOCATION", "")

    def __init__(self, *args, **kwargs):
        minio_url = getattr(settings, "MINIO_ACCESS_URL", None)
        if minio_url:
            self.secure_urls = False
            self.custom_domain = minio_url
        super().__init__(*args, **kwargs)


class S3MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        minio_url = getattr(settings, "MINIO_ACCESS_URL", None)
        if minio_url:
            self.secure_urls = False
            self.custom_domain = minio_url
        super().__init__(*args, **kwargs)
