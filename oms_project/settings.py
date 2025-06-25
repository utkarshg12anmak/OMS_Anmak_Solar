import os
import pymysql
from pathlib import Path
import dj_database_url

# ─── OLD DEFINITIONS (REMOVE THESE!) ────────────────────────────────────────────
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ────────────────────────────────────────────────────────────────────────────────SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-key")
# ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
ALLOWED_HOSTS = ['127.0.0.1', 'localhost','oms-project.onrender.com']

# Add dynamic Render hostname (optional, safe fallback)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)



pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

 # 3a) Tell Django to also look inside <BASE_DIR>/static/ when loading static files.
STATICFILES_DIRS = [
     BASE_DIR / "static",
]



USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'

# ─── 4) Template directories ───────────────────────────────────────────────────
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-*51yuzpyls+3q#n1w4!lyxyf4h3si=pb6($ovjheousnhn)+&j"

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.contenttypes",
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.humanize',
    "core",
    "leads",
    'customers',
    'profiles',
    'expenses',
    'interests',
    "widget_tweaks",
    "items", 
    "visit_details",
    "reminders",   # ← newly created
    "quotes",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # must be right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
ROOT_URLCONF = "oms_project.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # This will now work, because BASE_DIR is a `Path`.
        "DIRS": [ BASE_DIR / "templates_tmp" ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "oms_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get("MYSQL_DB"),
#         'USER': os.environ.get("MYSQL_USER"),
#         'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
#         'HOST': os.environ.get("MYSQL_HOST"),
#         'PORT': os.environ.get("MYSQL_PORT", "3306"),
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#             # Uncomment below for production security
#             # 'ssl': {'ssl-mode': 'REQUIRED'},
#         }
#     }
# }

DATABASES = {
    "default": dj_database_url.parse(
        "mysql://admin:asdfghjklp123@oms1.cpyqk6c0avpq.eu-north-1.rds.amazonaws.com:3306/oms_db",  # throws KeyError if missing—good for catching mis-configuration early
        conn_max_age=600,
        ssl_require=False,
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"


USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = '/'      # where to go after a successful login
LOGOUT_REDIRECT_URL = '/accounts/login/'

LOGIN_URL = 'login'              # where @login_required sends you when not authenticated

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


# ALLOWED_HOSTS = ["*"]     # during development, or set appropriately
