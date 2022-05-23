import json
from locale import currency

from django.core.management.base import BaseCommand, CommandError
from countries.models import Country, Currency


COUNTRIES_API_URL = "https://storage.googleapis.com/ac-dev-test-mock-api/countries.json"
CURRENCIES_API_URL = "https://storage.googleapis.com/ac-dev-test-mock-api/currencies.json"

class Command(BaseCommand):
    def handle(self, *args, **options):
        sync_data()


def sync_data():
    # TODO: Add a function that syncs the data in the APIs above with the data in the database
    return

