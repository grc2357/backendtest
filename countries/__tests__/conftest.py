import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Force pytest to use existing DB not its own
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": settings.BASE_DIR / "db.sqlite3",
    }
