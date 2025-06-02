import os
import dj_database_url
from .settings import *
from .settings import BASE_DIR

RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = [
    RENDER_HOST,
    'main.dq2ikwq61x8m0.amplifyapp.com',
    'react-next-swart-zeta.vercel.app',
]

CSRF_TRUSTED_ORIGINS = [
    f'https://{RENDER_HOST}',
    'https://main.dq2ikwq61x8m0.amplifyapp.com',
    'https://react-next-swart-zeta.vercel.app',
]

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'https://react-next-swart-zeta.vercel.app',
    'https://main.dq2ikwq61x8m0.amplifyapp.com',
]

DATABASES = {
    'default' : dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600
    )
}

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "eu-north-1")

STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/static/"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"
