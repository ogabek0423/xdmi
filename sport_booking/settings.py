"""
Django settings for sport_booking project.
"""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-development-secret-key"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "3.17.60.143",

]


# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [

    # Admin theme
    "jazzmin",

    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party
    "rest_framework",

    "django.contrib.sites",

    # Local apps
    "users",
    "facilities",
    "bookings.apps.BookingsConfig",
]


SITE_ID = 1


# =========================
# AUTH
# =========================

AUTH_USER_MODEL = "users.User"


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


LOGIN_REDIRECT_URL = "/"

ACCOUNT_LOGOUT_REDIRECT_URL = "/"


ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"


# Production uchun email keyin SMTP qilinadi
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
)


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    # Static files production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "sport_booking.urls"


# =========================
# TEMPLATES
# =========================

TEMPLATES = [

    {
        "BACKEND":
        "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

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


WSGI_APPLICATION = (
    "sport_booking.wsgi.application"
)


# =========================
# DATABASE
# =========================


# Hozir SQLite
# AWS PostgreSQL ga o'tkazilganda almashtiriladi

DATABASES = {

    "default": {

        "ENGINE":
        "django.db.backends.sqlite3",

        "NAME":
        BASE_DIR / "db.sqlite3",
    }
}



# PostgreSQL uchun:

"""
DATABASES = {
    "default": {
        "ENGINE":
        "django.db.backends.postgresql",

        "NAME":
        os.environ.get("DB_NAME"),

        "USER":
        os.environ.get("DB_USER"),

        "PASSWORD":
        os.environ.get("DB_PASSWORD"),

        "HOST":
        os.environ.get("DB_HOST"),

        "PORT":
        "5432",
    }
}
"""


# =========================
# PASSWORD VALIDATION
# =========================


AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },

]



# =========================
# LANGUAGE
# =========================


LANGUAGE_CODE = "en-us"


TIME_ZONE = "Asia/Tashkent"


USE_I18N = True


USE_TZ = True



# =========================
# STATIC / MEDIA
# =========================


STATIC_URL = "/static/"


STATICFILES_DIRS = [

    BASE_DIR / "static"

]


STATIC_ROOT = (

    BASE_DIR / "staticfiles"

)



MEDIA_URL = "/media/"


MEDIA_ROOT = (

    BASE_DIR / "media"

)



# =========================
# DEFAULT PRIMARY KEY
# =========================


DEFAULT_AUTO_FIELD = (

    "django.db.models.BigAutoField"

)



# =========================
# LOGGING
# =========================


LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,


    "handlers": {

        "console": {

            "class":
            "logging.StreamHandler",

        },

    },


    "loggers": {

        "bookings": {

            "handlers":
            [
                "console"
            ],

            "level":
            "INFO",

            "propagate":
            True,

        },

    },

}



# =========================
# JAZZMIN ADMIN
# =========================


JAZZMIN_SETTINGS = {


    "site_title":
    "Sport Booking",


    "site_header":
    "Sport Booking Admin",


    "site_brand":
    "Sport Booking",


    "topmenu_links": [

        {

            "name":
            "Asosiy sayt",

            "url":
            "/",

            "new_window":
            False,

        },


        {

            "name":
            "Statistika Dashboard",

            "url":
            "/dashboard/",

            "new_window":
            False,

        },

    ],

}



# =========================
# SECURITY SETTINGS
# =========================


SECURE_BROWSER_XSS_FILTER = True


SECURE_CONTENT_TYPE_NOSNIFF = True


X_FRAME_OPTIONS = "DENY"



# HTTPS yoqilgandan keyin True qilinadi

SESSION_COOKIE_SECURE = False

# =====================================================
# Bu kodni sport_booking/settings.py ga qo'shing
# (mavjud DATABASES va boshqa sozlamalarni almashtiring)
# =====================================================


# --- DATABASE (PostgreSQL) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# --- ALLOWED_HOSTS (env dan o'qiydi) ---
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

# --- CELERY ---
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# --- SECURITY (production) ---
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_SECURE = False