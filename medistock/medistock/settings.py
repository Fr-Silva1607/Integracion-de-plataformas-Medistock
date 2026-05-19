from pathlib import Path
import dj_database_url
import os

# Base
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = 'django-insecure-cambiar-esto-en-produccion'
DEBUG = os.environ.get('VERCEL') is None
ALLOWED_HOSTS = ['.vercel.app', '127.0.0.1', 'localhost']

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tienda',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medistock.urls'

# Templates (OPCIÓN 2)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  #  IMPORTANTE: vacío
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'medistock.wsgi.application'

# DB
DATABASES = {
    'default': dj_database_url.config(
           default='postgresql://postgres.ljzypuiqebttfmmgzsqk:rZsix5iBIfwCKEuy@aws-1-us-east-1.pooler.supabase.com:5432/postgres'
         
    )
}

# Passwords
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Idioma
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SUPABASE_URL = 'https://ljzypuiqebttfmmgzsqk.supabase.co'
SUPABASE_KEY = 'sb_publishable_LM3_tYyHvBjdPQxqJwB-zA_u03mDQwR'