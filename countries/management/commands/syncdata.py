import json, requests
from locale import currency

from django.core.management.base import BaseCommand, CommandError
from countries.models import Country, Currency

COUNTRIES_API_URL = "https://storage.googleapis.com/ac-dev-test-mock-api/countries.json"
CURRENCIES_API_URL = "https://storage.googleapis.com/ac-dev-test-mock-api/currencies.json"

class Command(BaseCommand):

    # Enter your own urls; this is mostly for unit testing.

    def add_arguments(self, parser):

        parser.add_argument("countries_url", nargs="?", type=str, 
                            default=COUNTRIES_API_URL)
        parser.add_argument("currencies_url", nargs="?", type=str, 
                            default=CURRENCIES_API_URL)

    def handle(self, *args, **options):

        countries_url = options["countries_url"]
        currencies_url = options["currencies_url"]

        sync_data(countries_url, currencies_url)

def sync_data(countries_api_url, currencies_api_url):
    # TODO: Add a function that syncs the data in the APIs above with the data in the database

    # Notes on solution.
    # I opted to use the requests for HTTP access, a fairly standard choice.
    # I have assumed thorughout that the symbols/codes are unique identifiers.
    # I did consider a few different ways of implementing this task, but
    # since neither contries or currencies change very frequently, I went for 
    # simplicity over speed or optimization.

    # Connect to the API.
    try:
        countries_request = requests.get(countries_api_url)
        currencies_request = requests.get(currencies_api_url)
        if countries_request.status_code != 200:
            raise Exception("countries", countries_request.status_code)
        if currencies_request.status_code != 200:
            raise Exception("currencies", currencies_request.status_code)
    except Exception as error:
        if len(error.args) == 2:
            url, exit_code = error.args
            raise CommandError("Could not connect to {} url, exit code {}.".format(
                url, exit_code))
        else:
            raise CommandError("Unknown connection error.")

    # Convert the data to native python data types.
    countries_list = countries_request.json()
    currencies_list = currencies_request.json()
    
    # Task 3 part 1 and part 4.
    # For every currency extracted from the API, check if there is a currency
    # with a matching symbol in the DB. If there exist corresponding 
    # currencies, check that their names match and update the DB if required;
    # otherwise, add the new currency to a list of new currencies that can
    # be created en masse.

    new_currencies = []

    for currency in currencies_list:

        currency["symbol"] = currency.pop("code")
        try:
            currency_in_db = Currency.objects.get(symbol=currency.get("symbol"))
        except:
            currency_in_db = None
        
        if currency_in_db:
            # Check/Update names.
            if currency_in_db.name != currency.get("name"):
                currency_in_db.name = currency.get("name")
                currency_in_db.save()
        else:
            # There are new currencies.
            new_currencies.append(Currency(**currency))

    # Create new currencies en masse.
    if len(new_currencies) > 0:
        Currency.objects.bulk_create(new_currencies)

    # Task 3 part 2 and 4
    # For every country extracted from the API, check if there is a country
    # with a matching symbol in the DB. If there exist corresponding
    # countries, check that their names and currencies match and update the DB
    # if required; otherwise, create a new country and add the appropriate
    # currencies to that country.

    for country in countries_list:
        
        country["symbol"] = country.pop("code")
        try:
            country_in_db = Country.objects.get(symbol=country.get("symbol"))
        except Country.DoesNotExist:
            country_in_db = None

        if country_in_db:
            # Check/Update names.
            if country_in_db.name != country.get("name"):
                country_in_db.name = country.get("name")
                country_in_db.save()
            
            # Check/Update currencies.
            currencies_in_db = [currency.symbol 
                                for currency in country_in_db.currencies.all()]

            for symbol in country.get("currencies"):
                if symbol not in currencies_in_db:
                    country_in_db.currencies.add(Currency.objects.get(
                                                symbol=symbol))
                    country_in_db.save()

            for symbol in currencies_in_db:
                if symbol not in country.get("currencies"):
                    country_in_db.currencies.remove(Currency.objects.get(
                                                    symbol=symbol))
                    country_in_db.save()

        else:
            # Create new country.
            list_of_currencies = list(Currency.objects.filter(
                symbol__in=country["currencies"]))

            new_country = Country(name=country["name"], 
                                symbol=country["symbol"])
            new_country.save()
            new_country.currencies.add(*list_of_currencies)

    # Task 3 part 3
    # Simply, if a country or currency exists in the DB, but it is not 
    # extracted from the API (based on the symbol), then it is deleted.

    country_symbols = set([cd["symbol"] for cd in countries_list])
    country_symbols_in_db = set(Country.objects.values_list("symbol", 
                                flat=True))
    currency_symbols = set([cd["symbol"] for cd in currencies_list])
    currency_symbols_in_db = set(Currency.objects.values_list("symbol", 
                                flat=True))
    
    for symbol in currency_symbols_in_db:
        if symbol not in currency_symbols:
            Currency.objects.get(symbol=symbol).delete()

    for symbol in country_symbols_in_db:
        if symbol not in country_symbols:
            Country.objects.get(symbol=symbol).delete()

    return