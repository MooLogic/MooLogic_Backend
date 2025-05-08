from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-szqjme@62se#a3%fq2yw8+f6tmrp5)nk^(j!8=h&zqz7a5=k8^'

DEBUG = True

ALLOWED_HOSTS = [
    'moologic-backend-3.onrender.com',
    'moologic-backend-4.onrender.com',
    'moologic-backend-5.onrender.com',
    'moologic-backend-6.onrender.com',
    'moologic-backend-7.onrender.com',
    '127.0.0.1'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',

    # Custom Apps
    'userauth',
    'finance_tracker',
    'core',
    'milk_tracker',
    'health_manager',

    # DRF & Auth
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',

    # Social Auth Setup
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# Custom User Model
AUTH_USER_MODEL = 'userauth.User'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

ROOT_URLCONF = 'moologic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'moologic.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔹 REST Framework Authentication Setup
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Optional for browsable API
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 🔹 Enable JWT Auth
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Default for all views
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=500),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 🔹 Enable JWT Authentication
REST_USE_JWT = True

# 🔹 Google OAuth2 Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            'key': ''
        },
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# 🔹 Authentication Backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# 🔹 Redirect URLs After Login
LOGIN_REDIRECT_URL = "/dashboard"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True

# 🔹 Required for Django-Allauth
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
# ACCOUNT_LOGIN_METHODS = {"email"}  # Use a set
# ACCOUNT_SIGNUP_FIELDS = {
    
#     "email": {"required": True},
#     "username": {"required": True},
#     "password1": {"required": True},
#     "password2": {"required": True},
# }

# Email Settings (For production, update SMTP settings accordingly)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 8025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
