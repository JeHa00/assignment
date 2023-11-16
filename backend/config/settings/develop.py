from config.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "HOST": env.str("DEV_DB_HOST", "localhost"),
        "USER": env.str("DEV_DB_USER"),
        "PASSWORD": env.str("DEV_DB_PASSWORD"),
        "NAME": env.str("DEV_DB_NAME"),
        "PORT": env.str("DEV_DB_PORT"),
    },
}


INTERNAL_IPS = [
    "127.0.0.1",
]
