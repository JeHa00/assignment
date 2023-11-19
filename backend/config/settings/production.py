from config.settings.base import *

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": env.str("DEV_DB_HOST"),
        "USER": env.str("DEV_DB_USER"),
        "PASSWORD": env.str("DEV_DB_PASSWORD"),
        "NAME": env.str("DEV_DB_NAME"),
        "PORT": env.str("DEV_DB_PORT"),
    },
}

INTERNAL_IPS = [
    "127.0.0.1",
]
