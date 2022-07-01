import os

from django.conf import settings


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=("django_user_agents",),
        MIDDLEWARE=[
            "django_user_agents.middleware.UserAgentMiddleware",
        ],
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "TIMEOUT": 60,
                "LOCATION": "default-location",
            },
            "test": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "TIMEOUT": 60,
                "LOCATION": "test-location",
            },
        },
        ROOT_URLCONF="tests.urls",
        SECRET_KEY="dummy",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [
                    os.path.join(os.path.dirname(__file__), "templates"),
                ],
            },
        ],
    )
