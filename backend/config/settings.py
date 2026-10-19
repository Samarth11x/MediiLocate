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

# Ensure backend directory is in python path
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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
    for host in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

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
# Database Configuration (Supabase PostgreSQL with Development SQLite Fallback)
# ------------------------------------------------------------------------------
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
SUPABASE_DB_SSLMODE = os.getenv('SUPABASE_DB_SSLMODE', 'require')

if SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD:
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
    # Fallback mode for local development/testing when Supabase credentials are not provided
    if DJANGO_ENV == 'production':
        raise ImproperlyConfigured(
            "Production database configuration missing: SUPABASE_DB_HOST and "
            "SUPABASE_DB_PASSWORD must be configured in environment."
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
# Static files (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

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
}

if DEBUG:
    # Enable browsable API in local development mode
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# ------------------------------------------------------------------------------
# CORS Configuration (Explicit Origins, No Unrestricted Wildcards)
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
