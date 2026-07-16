from pathlib import Path
import dj_database_url
import os


def _load_env_file(file_path: Path) -> None:
    """Load KEY=VALUE pairs from .env files without external dependencies."""
    if not file_path.exists():
        return

    for raw_line in file_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

# Base
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment files from project roots for local development.
_load_env_file(BASE_DIR / '.env')
_load_env_file(BASE_DIR.parent / '.env')

# Seguridad
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-cambiar-esto-en-produccion')
DEBUG = os.environ.get('VERCEL') is None
ALLOWED_HOSTS = ['.vercel.app', 'medistock-duoc.vercel.app', '127.0.0.1', 'localhost']
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

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
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DB_URL')
FORCE_SUPABASE_DB = os.environ.get('FORCE_SUPABASE_DB', '').lower() in ('1', 'true', 'yes')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    if FORCE_SUPABASE_DB:
        raise RuntimeError(
            'FORCE_SUPABASE_DB is enabled but SUPABASE_DB_URL/DATABASE_URL is missing. '
            'Set the Supabase Postgres connection string in .env.'
        )

    # Fallback to local SQLite for development/testing when no DATABASE_URL is provided
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# In production (on Vercel) we must have a proper DATABASE_URL configured.
# Raise a clear error early to avoid obscure 500 responses during auth or migrations.
if os.environ.get('VERCEL') is not None and not DATABASE_URL:
    raise RuntimeError(
        'Missing DATABASE_URL: set the DATABASE_URL or SUPABASE_DB_URL environment variable '
        'in your Vercel project and run migrations. Using SQLite on Vercel is not supported.'
    )

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

SUPABASE_URL = os.environ.get(
    'SUPABASE_URL',
    'https://ljzypuiqebttfmmgzsqk.supabase.co'
)

SUPABASE_PUBLISHABLE_KEY = os.environ.get(
    'SUPABASE_PUBLISHABLE_KEY',
    'sb_publishable_LM3_tYyHvBjdPQxqJwB-zA_u03mDQwR'
)

SUPABASE_SECRET_KEY = os.environ.get(
    'SUPABASE_SECRET_KEY',
    ''
)

SUPABASE_SERVER_KEY = os.environ.get(
    'SUPABASE_SERVER_KEY',
    SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY
)

# Compatibilidad con código existente de templates y scripts
SUPABASE_KEY = SUPABASE_PUBLISHABLE_KEY


# ── Chilexpress API ──

CHILEXPRESS_BASE_URL = "http://testservices.wschilexpress.com"

CHILEXPRESS_API_KEY = ""
CHILEXPRESS_API_SECRET = ""
