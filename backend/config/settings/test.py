from config.settings.base import *

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
        # "HOST": env.str("TEST_DB_HOST"),
        "HOST": "localhost",
        "USER": env.str("TEST_DB_USER"),
        "PASSWORD": env.str("TEST_DB_PASSWORD"),
        "NAME": env.str("TEST_DB_NAME"),
        "PORT": env.int("TEST_DB_PORT"),
    },
}

"""
{'default': {'ENGINE': 'django.db.backends.mysql', 
'HOST': 'localhost', 
'USER': 'project', 
'PASSWORD': 'a1s2d3f4', 
'NAME': 'test', 
'PORT': 3310}
}
"""
