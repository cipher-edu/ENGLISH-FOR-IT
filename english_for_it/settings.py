"""
Django settings for english_for_it project.
Production-ready configuration with full features.
"""

import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR

# Add apps directory to Python path
sys.path.insert(0, str(BASE_DIR / 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-a2^#gi2(=w%)n&0$l#6=))nb#*h+3z3@^=k4p4gt0*r$%m2fuq')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_STAGING = ENVIRONMENT == 'staging'
IS_PRODUCTION = ENVIRONMENT == 'production'

# Hosts configuration
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
if DEBUG:
    ALLOWED_HOSTS = ['*']

# Site configuration
SITE_ID = 1
SITE_NAME = 'English for IT'
SITE_DOMAIN = os.getenv('SITE_DOMAIN', 'localhost:8000')
SITE_PROTOCOL = 'https' if IS_PRODUCTION else 'http'
SITE_URL = f"{SITE_PROTOCOL}://{SITE_DOMAIN}"

# Application definition - FIXED
INSTALLED_APPS = [
    # Admin enhancement - Must be before admin
    'jazzmin',
    'axes',
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    
    # Third party apps - Core
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'whitenoise.runserver_nostatic',
    
    # Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    
    # Additional third party
    'django_extensions',
    'import_export',
    'imagekit',
    'django_cleanup.apps.CleanupConfig',
    'taggit',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Optional - comment out if not installed
    # 'rest_framework_simplejwt',
    # 'rest_framework_simplejwt.token_blacklist',
    # 'dj_rest_auth',
    # 'dj_rest_auth.registration',
    # 'django_celery_beat',
    # 'django_celery_results',
    # 'channels',
    # 'simple_history',
    # 'django_countries',
    # 'phonenumber_field',
    # 'djmoney',
    # 'axes',
    # 'django_csp',
    # 'storages',
    
    # Local apps
    'accounts',
    'courses',
    'vocabulary',
    'speaking',
    'writing',
    'assessments',
    'gamification',
    'corporate',
]

# Development-only apps
if DEBUG:
    # Add only if installed
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
    except ImportError:
        pass
    
    try:
        import silk
        INSTALLED_APPS += ['silk']
    except ImportError:
        pass

# Middleware configuration
MIDDLEWARE = [
    # Security
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    
    # WhiteNoise - Static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Django core
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Allauth
    'allauth.account.middleware.AccountMiddleware',
]

# Optional middleware - add only if apps are installed
try:
    import axes
    MIDDLEWARE += ['axes.middleware.AxesMiddleware']
except ImportError:
    pass

try:
    import simple_history
    MIDDLEWARE += ['simple_history.middleware.HistoryRequestMiddleware']
except ImportError:
    pass

# Development middleware
if DEBUG:
    try:
        import debug_toolbar
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    except ImportError:
        pass
    
    try:
        import silk
        MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
    except ImportError:
        pass

# Debug toolbar settings
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    try:
        import socket
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]
    except:
        pass
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
    }

ROOT_URLCONF = 'english_for_it.urls'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Django defaults
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Additional
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

# WSGI/ASGI configuration
WSGI_APPLICATION = 'english_for_it.wsgi.application'
ASGI_APPLICATION = 'english_for_it.asgi.application'

# Database configuration
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() == 'true'

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'english_for_it'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'ATOMIC_REQUESTS': True,
        }
    }
else:
    # SQLite for development (default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cache configuration
USE_REDIS = os.getenv('USE_REDIS', 'False').lower() == 'true'

if USE_REDIS:
    try:
        import django_redis
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/1",
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
    except ImportError:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication configuration
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Add axes backend if installed
try:
    import axes
    AUTHENTICATION_BACKENDS = [
        'axes.backends.AxesStandaloneBackend',
    ] + AUTHENTICATION_BACKENDS
    
    # Axes configuration
    AXES_FAILURE_LIMIT = 5
    AXES_COOLOFF_TIME = timedelta(minutes=30)
    AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
    AXES_RESET_ON_SUCCESS = True
except ImportError:
    pass

# Django-allauth configuration
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# New allauth settings format
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# Rate limiting
ACCOUNT_RATE_LIMITS = {
    'login': None,
    'login_failed': '5/5m',
    'signup': '10/h',
    'password_reset': '5/h',
}

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        }
    },
    'github': {
        'SCOPE': ['user:email'],
        'APP': {
            'client_id': os.getenv('GITHUB_CLIENT_ID', ''),
            'secret': os.getenv('GITHUB_CLIENT_SECRET', ''),
            'key': '',
        }
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('uz', 'O\'zbekcha'),
    ('ru', 'Русский'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# Create static directory if it doesn't exist
static_dir = BASE_DIR / 'static'
static_dir.mkdir(exist_ok=True)
if static_dir.exists():
    STATICFILES_DIRS = [static_dir]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_AUTOREFRESH = DEBUG

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny' if DEBUG else 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ] + (['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 
    'PATCH', 'POST', 'PUT'
]
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with', 'cache-control',
]

# CSRF Configuration
CSRF_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = []

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@englishforit.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Django Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "English for IT Admin",
    "site_header": "English for IT",
    "site_brand": "English for IT",
    "welcome_sign": "Welcome to English for IT Admin Panel",
    "copyright": "English for IT © 2024",
    
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.User": "fas fa-user-graduate",
        "courses.Course": "fas fa-graduation-cap",
        "vocabulary.Word": "fas fa-spell-check",
        "assessments.Assessment": "fas fa-clipboard-check",
        "gamification.Badge": "fas fa-trophy",
        "corporate.Company": "fas fa-building",
    },
    
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Logging Configuration
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Custom Application Settings
VOCABULARY_SPACED_REPETITION_ALGORITHM = 'SM2'
MIN_PASSWORD_LENGTH = 8
XP_PER_LESSON = 10
ASSESSMENT_PASSING_SCORE = 70

# Create necessary directories
for directory in ['logs', 'media', 'static', 'staticfiles', 'templates', 'locale']:
    dir_path = BASE_DIR / directory
    dir_path.mkdir(parents=True, exist_ok=True)

# Print configuration summary
if DEBUG:
    db_engine = DATABASES['default']['ENGINE'].split('.')[-1]
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║              English for IT - Configuration                   ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ Environment: {ENVIRONMENT:<20}                         ║
    ║ Debug Mode: {str(DEBUG):<20}                          ║
    ║ Database: {db_engine:<20}                            ║
    ║ Cache Backend: {'Redis' if USE_REDIS else 'Local Memory':<20}               ║
    ║ Static Files: WhiteNoise Enabled                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)