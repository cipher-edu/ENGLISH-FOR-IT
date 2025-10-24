"""
Django settings for english_for_it project.
Senior-level production-ready configuration with security best practices.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY ='django-insecure-change-this-in-production!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# Site configuration
SITE_ID = 1
SITE_NAME = 'English for IT'
SITE_DOMAIN = os.getenv('SITE_DOMAIN', 'localhost:8000')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    # 'djmoney',
]
# Money settings
CURRENCIES = ('USD', 'EUR')
CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €')]
# Third party apps
THIRD_PARTY_APPS = [
    # Admin UI (JAZZMIN 'INSTALLED_APPS' ning boshiga ko'chirildi)
    
    # Security & Monitoring (Bir joyga to'plandi)
    'corsheaders',
    'django_ratelimit',
    'axes',
    'csp',             # Takrorlanish olib tashlandi
   # 'django_csprest_framework', # O'rnatilganligini tekshiring!
    'silk',                   # API profiling (dev only)
    'debug_toolbar',          # Dev only
    
    # API & Authentication
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    
    # Database & Models
    'django_extensions',
    'django_filters',
    'import_export',
    
    # Tasks & Background Jobs
    'django_celery_beat',
    'django_celery_results',
    
    # WebSocket & Real-time
    'channels',
    'channels_redis',
    
    # Storage & Files
    'storages',
    'imagekit',
    'django_cleanup',  # Auto delete files
    
    # Other
    'taggit',
    'django_countries',
    'phonenumber_field',
    'djmoney',
    'django_redis',
]
# Local apps
LOCAL_APPS = [
    'accounts.apps.AccountsConfig',
    'courses.apps.CoursesConfig',
    'vocabulary.apps.VocabularyConfig',
    'speaking.apps.SpeakingConfig',
    'writing.apps.WritingConfig',
    'assessments.apps.AssessmentsConfig',
    'gamification.apps.GamificationConfig',
    'corporate.apps.CorporateConfig',
]

# Jazzmin should be before admin
INSTALLED_APPS = ['jazzmin'] + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware configuration
MIDDLEWARE = [
    # Security
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Django defaults
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # REQUIRED FOR ALLAUTH
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Third party
    'axes.middleware.AxesMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
    'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
    # Removed duplicate CSPMiddleware
]
# Instead of CSP_XXX = ...
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net')
# ... etc
# Development-only middleware
if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'silk.middleware.SilkyMiddleware',
    ]

ROOT_URLCONF = 'english_for_it.urls'

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# ASGI & WebSocket configuration
ASGI_APPLICATION = 'english_for_it.asgi.application'
WSGI_APPLICATION = 'english_for_it.wsgi.application'

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('REDIS_HOST', '127.0.0.1'), 6379)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Database configuration
if IS_PRODUCTION:
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'english_for_it'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=30000'  # 30 seconds
            }
        }
    }

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'english_it',
        'TIMEOUT': 3600,  # 1 hour default
    },
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/2",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'ratelimit': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/3",
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.PasswordHistoryValidator',
        'OPTIONS': {'history_limit': 5}
    },
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Brute force protection
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django-axes configuration (Brute force protection)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('uz', 'Uzbek'),
    ('ru', 'Russian'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration for static files
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_COMPRESS_OFFLINE = True
    WHITENOISE_COMPRESSION_QUALITY = 80
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AWS S3 Configuration (for production)
if IS_PRODUCTION:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    
    # Media files on S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# File upload settings
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_TEMP_DIR = '/tmp'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ] if DEBUG else [
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
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
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/hour',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'VERSION_PARAM': 'version',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': SITE_DOMAIN,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Django-allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' if IS_PRODUCTION else 'optional'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_SESSION_REMEMBER = True
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
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
CSRF_TRUSTED_ORIGINS = [f'https://{SITE_DOMAIN}'] if IS_PRODUCTION else []

# Security settings
SECURE_SSL_REDIRECT = IS_PRODUCTION
SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if IS_PRODUCTION else None
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Content Security Policy
if IS_PRODUCTION:
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net')
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", 'https://fonts.googleapis.com')
    CSP_FONT_SRC = ("'self'", 'https://fonts.gstatic.com')
    CSP_IMG_SRC = ("'self'", 'data:', 'https:')
    CSP_CONNECT_SRC = ("'self'", 'https://api.anthropic.com', 'wss:')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if IS_PRODUCTION else 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'noreply@{SITE_DOMAIN}')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Celery configuration
CELERY_BROKER_URL = f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/0"
CELERY_RESULT_BACKEND = f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes
CELERY_BEAT_SCHEDULE = {
    'check-daily-streaks': {
        'task': 'accounts.tasks.check_daily_streaks',
        'schedule': timedelta(hours=1),
    },
    'send-practice-reminders': {
        'task': 'accounts.tasks.send_practice_reminders',
        'schedule': timedelta(hours=12),
    },
    'update-leaderboards': {
        'task': 'gamification.tasks.update_leaderboards',
        'schedule': timedelta(minutes=30),
    },
    'generate-analytics': {
        'task': 'corporate.tasks.generate_daily_analytics',
        'schedule': timedelta(days=1),
    },
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
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
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django Jazzmin configuration
JAZZMIN_SETTINGS = {
    "site_title": "English for IT Admin",
    "site_header": "English for IT",
    "site_brand": "English for IT",
    "site_logo": "img/logo.png",
    "login_logo": "img/logo-large.png",
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to English for IT Admin Panel",
    "copyright": "English for IT",
    "search_model": ["accounts.User", "courses.Course"],
    
    # UI Customizations
    "custom_css": "css/admin-custom.css",
    "custom_js": "js/admin-custom.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Theme settings
    "theme": "cerulean",
    "dark_mode_theme": "darkly",
    
    # Sidebar
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "accounts", "courses", "vocabulary", 
        "speaking", "writing", "assessments", 
        "gamification", "corporate"
    ],
    
    "icons": {
        "accounts.User": "fas fa-users",
        "courses.Course": "fas fa-graduation-cap",
        "vocabulary.Word": "fas fa-spell-check",
        "assessments.Assessment": "fas fa-clipboard-check",
        "gamification.Badge": "fas fa-trophy",
        "corporate.Company": "fas fa-building",
    },
    
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "accounts.User"},
        {"app": "courses"},
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    
    "custom_links": {
        "courses": [{
            "name": "Course Analytics",
            "url": "/admin/analytics/courses",
            "icon": "fas fa-chart-line",
            "permissions": ["courses.view_course"]
        }],
    },
    
    # Change forms
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.user": "collapsible",
        "courses.course": "vertical_tabs"
    },
}

# Django Debug Toolbar (Development only)
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
    }

# Sentry configuration (for production error tracking)
if IS_PRODUCTION:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=ENVIRONMENT,
    )

# API Rate Limiting
RATELIMIT_USE_CACHE = 'ratelimit'
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = 'english_for_it.views.ratelimited'

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Custom settings for the application
VOCABULARY_SPACED_REPETITION_ALGORITHM = 'SM2'
MIN_PASSWORD_LENGTH = 8
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.m4a']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.webm', '.ogv']
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.doc', '.docx', '.txt']

# AI Service Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_SPEECH_API_KEY = os.getenv('GOOGLE_SPEECH_API_KEY')
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')

# Payment Gateway Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
PAYME_MERCHANT_ID = os.getenv('PAYME_MERCHANT_ID')
PAYME_SECRET_KEY = os.getenv('PAYME_SECRET_KEY')

# Social Authentication
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        }
    },
    'github': {
        'SCOPE': ['user:email'],
        'APP': {
            'client_id': os.getenv('GITHUB_CLIENT_ID'),
            'secret': os.getenv('GITHUB_CLIENT_SECRET'),
        }
    }
}

# Performance optimizations
if IS_PRODUCTION:
    # Database connection pooling
    DATABASES['default']['CONN_MAX_AGE'] = 600
    
    # Enable persistent connections
    DATABASES['default']['OPTIONS']['connect_timeout'] = 10
    
    # Enable database query optimization
    DATABASES['default']['OPTIONS']['server_side_cursors'] = True

# Health check endpoints
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,
    'MEMORY_MIN': 100,
}

# Feature flags
FEATURES = {
    'ENABLE_SOCIAL_LOGIN': True,
    'ENABLE_SPEAKING_MODULE': True,
    'ENABLE_AI_FEEDBACK': True,
    'ENABLE_PEER_REVIEW': True,
    'ENABLE_CORPORATE_FEATURES': True,
    'ENABLE_GAMIFICATION': True,
    'ENABLE_CERTIFICATES': True,
}

# Admin configuration
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@example.com')),
]
MANAGERS = ADMINS

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)