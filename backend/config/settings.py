"""
Django settings for MediLocate AI backend project.
"""

import os
import sys
from pathlib import Path
from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project: BASE_DIR is the 'backend' directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Project root (where root .env.example / .env resides)
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables from .env in project root or backend
load_dotenv(PROJECT_ROOT / '.env')
load_dotenv(BASE_DIR / '.env')

# Ensure backend directory and project root are in python path
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ------------------------------------------------------------------------------
# Security & Environment Settings
# ------------------------------------------------------------------------------
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development').lower()

# Secret key: In development a deterministic fallback is permitted if unset;
# in production it must be explicitly defined.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DJANGO_ENV == 'production':
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production environment.")
    SECRET_KEY = 'django-insecure-dev-only-secret-key-replace-in-production-min-50-chars'

# Debug mode
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')
if DJANGO_ENV == 'production' and DEBUG:
    # Safety guardrail: Never allow DEBUG in production
    DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
    if host.strip()
]
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ------------------------------------------------------------------------------
# Application Definitions
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party applications
    'rest_framework',
    'corsheaders',

    # MediLocate Domain Applications
    'apps.accounts.apps.AccountsConfig',
    'apps.pharmacies.apps.PharmaciesConfig',
    'apps.medicines.apps.MedicinesConfig',
    'apps.inventory.apps.InventoryConfig',
    'apps.search.apps.SearchConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the very top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Immediately after SecurityMiddleware for asset delivery
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ------------------------------------------------------------------------------
# Database Configuration (Render / PostgreSQL via DATABASE_URL, Supabase, or SQLite)
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
SUPABASE_DB_SSLMODE = os.getenv('SUPABASE_DB_SSLMODE', 'require')

if DATABASE_URL:
    # Production PostgreSQL connection string (Render managed PostgreSQL)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD:
    # Direct PostgreSQL connection to Supabase via Psycopg 3
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': SUPABASE_DB_NAME,
            'USER': SUPABASE_DB_USER,
            'PASSWORD': SUPABASE_DB_PASSWORD,
            'HOST': SUPABASE_DB_HOST,
            'PORT': SUPABASE_DB_PORT,
            'OPTIONS': {
                'sslmode': SUPABASE_DB_SSLMODE,
            },
        }
    }
else:
    # Fallback mode for local development/testing when PostgreSQL credentials are not provided
    if DJANGO_ENV == 'production':
        raise ImproperlyConfigured(
            "Production database configuration missing: set DATABASE_URL or "
            "SUPABASE_DB_HOST / SUPABASE_DB_PASSWORD in the environment."
        )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ------------------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# Internationalization & Regional Settings
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'

# Explicitly configured to Asia/Kolkata per CTO directive
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images, and Frontend Vite Build via WhiteNoise)
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

VITE_DIST_DIR = PROJECT_ROOT / 'frontend' / 'dist'
STATICFILES_DIRS = []
if VITE_DIST_DIR.exists():
    STATICFILES_DIRS.append(VITE_DIST_DIR)
    # Serve root-level PWA and static assets (favicon.svg, manifest, sw.js, offline.html) directly from root
    WHITENOISE_ROOT = VITE_DIST_DIR

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------------------
# Django REST Framework Settings
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

if DEBUG:
    # Enable browsable API in local development mode
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# ------------------------------------------------------------------------------
# CORS & CSRF Configuration
# ------------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origin.strip()
]

if RENDER_EXTERNAL_HOSTNAME:
    render_url = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if render_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_url)
    if render_url not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(render_url)

# ------------------------------------------------------------------------------
# Session & CSRF Cookie Security
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_HTTPONLY = False  # Must be False so frontend client can read csrftoken for safe bootstrap
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# ------------------------------------------------------------------------------
# Production Security Headers & SSL Guardrails
# ------------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
