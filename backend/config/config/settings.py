from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
from decouple import config

# ======================
# BASE
# ======================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env',override=True)


# ======================
# SECURITY
# ======================
ENABLE_AI_MODERATION= True
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if not DEBUG:
    ALLOWED_HOSTS += ['.onrender.com']

# ======================
# APPLICATIONS
# ======================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third‑party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    # Local apps
    'categoria',
    'distrito',
    'quejas',
    'comentario',
    'megusta',
    'imagen',
    'perfil',
    'video',
    'core',
    'stats',
    'notificaciones',
    'respuesta',
]


# ======================
# MIDDLEWARE
# ======================


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ======================
# URLS / WSGI
# ======================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# ======================
# TEMPLATES
# ======================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# ======================
# DATABASE
# ======================


DATABASES = {
    'default': dj_database_url.config(
        default=(
            config('DATABASE_URL')
            if config('DATABASE_URL', default=None)
            else f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
        ),
        conn_max_age=600,
        ssl_require=config('DJANGO_ENV', default='local') == 'production'
    )
}


# ======================
# AUTH
# ======================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'auth.User'


# ======================
# I18N
# ======================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ======================
# STATIC & MEDIA
# ======================

STATIC_URL = 'static/'
STATIC_ROOT= BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ======================
# REST FRAMEWORK
# ======================

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER':'core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DATETIME_FORMAT': '%d/%m/%Y',
}


# ======================
# JWT
# ======================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}


# ======================
# DRF SPECTACULAR
# ======================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Alcalde Escuchame API',
    'DESCRIPTION': 'API para la aplicación Alcalde Escuchame',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayResquestDuration': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}


# ======================
# CORS & FRONTEND
# ======================

FRONTEND_URL = os.environ.get('FRONTEND_URL')

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "https://alcalde-escuchame-frontend.onrender.com",
]

CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
]
CORS_ALLOW_CREDENTIALS= True

# ======================
# EMAIL
# ======================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'escuchamealcalde@gmail.com'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
