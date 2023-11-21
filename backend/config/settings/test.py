from config.settings.base import *

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
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("TEST_DB_NAME"),
        "USER": env.str("TEST_DB_USER"),
        "PASSWORD": env.str("TEST_DB_PASSWORD"),
        "HOST": "localhost",
        "PORT": env.str("TEST_DB_PORT"),
        "TEST": {"NAME": "test"},
    },
}
