from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from urllib.parse import urlparse

class StaticS3Boto3Storage(S3Boto3Storage):
    location = getattr(settings, "STATICFILES_LOCATION", "")

    def __init__(self, *args, **kwargs):
        minio_url = getattr(settings, "MINIO_ACCESS_URL", None)
        if minio_url:
            self.secure_urls = False
            parsed = urlparse(minio_url)
            self.custom_domain = parsed.netloc  # ✅ only 'localhost:9000'
        super().__init__(*args, **kwargs)

class S3MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        minio_url = getattr(settings, "MINIO_ACCESS_URL", None)
        if minio_url:
            self.secure_urls = False
            parsed = urlparse(minio_url)
            self.custom_domain = parsed.netloc  # ✅ only 'localhost:9000'
        super().__init__(*args, **kwargs)
