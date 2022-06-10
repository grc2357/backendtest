import pytest

from django.core.management import call_command
from countries.models import Country, Currency

# Use these incorrect urls to test connection errors.
COUNTRIES_API_URL_ERROR = "https://storage.googleapis.com/ac-dev-test-mock-api/error/countries.json"
CURRENCIES_API_URL_ERROR = "https://storage.googleapis.com/ac-dev-test-mock-api/error/currencies.json"

# Code for bonus task.

@pytest.mark.django_db
class TestSyncData:

    # Call syncdata.
    def call_command(self, *args, **kwargs):
        call_command("syncdata", *args, **kwargs)

    # Add some fake data to the database that should be removed when
    # syncdata is called.
    def add_fake_data(self):
        
        currency1 = Currency(name="Gold Pressed Latinum", 
                                            symbol="FGPL")
        currency1.save()
        currency2 = Currency(name="Galactic Credits", 
                                            symbol="GC")
        currency2.save()
        currency3 = Currency(name="Pixie Dust", symbol="PXD")
        currency3.save()

        country1 = Country(name="United Federation of Planets", 
                                        symbol="UFP")
        country1.save()
        country2 = Country(name="Pixie Land", symbol="PXL")
        country2.save()
        
        country1.currencies.add(currency1, currency2)
        country2.currencies.add(currency3)

        # Add the incorrect US currency to the UK.
        
        uk = Country.objects.get(symbol="GBR")
        uk.currencies.add(Currency.objects.get(symbol="USD"))

        # Spell Chinese country and currency incorrectly.
        china = Country.objects.get(symbol="CHN")
        china.name = "Xhina"
        china.save()
        cny = Currency.objects.get(symbol="CNY")
        cny.name = "XXXXX"
        cny.save()

    # Delete or remove some valid data from the database that should
    # be added back when syncdata is called.
    def delete_remove_real_data(self):
        
        Country.objects.get(symbol="AUS").delete()
        Country.objects.get(symbol="AUT").delete()

        Country.objects.get(symbol="USA").currencies.remove(
                            Currency.objects.get(symbol="USD"))

        Currency.objects.get(symbol="USN").delete()
    
    
    def test_call(self):
        # Apply add_fake_data and test that the fake data has been added correctly.
        self.add_fake_data()
        assert len(Currency.objects.filter(symbol="FGPL")) == 1
        assert len(Currency.objects.filter(symbol="GC")) == 1
        assert len(Currency.objects.filter(symbol="PXD")) == 1
        assert len(Country.objects.filter(symbol="UFP")) == 1
        assert len(Country.objects.filter(symbol="PXL")) == 1

        assert Currency.objects.get(symbol="USD") in Country.objects.get(
            symbol="GBR").currencies.all()

        assert Country.objects.get(symbol="CHN").name == "Xhina"
        assert Currency.objects.get(symbol="CNY").name == "XXXXX"

        # Apply delete_remove_real_data and test that the real data has been
        # removed correctly.
    
        self.delete_remove_real_data()
        assert len(Country.objects.filter(symbol="AUS")) == 0
        assert len(Country.objects.filter(symbol="AUT")) == 0
        assert len(Currency.objects.filter(symbol="USN")) == 0

        assert Currency.objects.get(symbol="USD") not in Country.objects.get(
            symbol="USA").currencies.all()

        # Apply the call to syncdata.py and apply the reverse of the test above
        # to test if the damage has been undone.
    
        self.call_command()

        assert len(Currency.objects.filter(symbol="FGPL")) == 0
        assert len(Currency.objects.filter(symbol="GC")) == 0
        assert len(Currency.objects.filter(symbol="PXD")) == 0
        assert len(Country.objects.filter(symbol="UFP")) == 0
        assert len(Country.objects.filter(symbol="PXL")) == 0

        assert Currency.objects.get(symbol="USD") not in Country.objects.get(
            symbol="GBR").currencies.all()

        assert Country.objects.get(symbol="CHN").name == "China"
        assert Currency.objects.get(symbol="CNY").name == "Yuan Renminbi"

        assert len(Country.objects.filter(symbol="AUS")) == 1
        assert len(Country.objects.filter(symbol="AUT")) == 1
        assert len(Currency.objects.filter(symbol="USN")) == 1

        assert Currency.objects.get(symbol="USD") in Country.objects.get(
            symbol="USA").currencies.all()
    
    # Test the the call to syncdata.py with incorrect urls.
    def test_call_error(self):
        with pytest.raises(Exception):
            self.call_command(countries_url=COUNTRIES_API_URL_ERROR, 
                            currencies_url=CURRENCIES_API_URL_ERROR)
        with pytest.raises(Exception):
            self.call_command(countries_url="", currencies_url="")
        with pytest.raises(Exception):
            self.call_command(currencies_url=CURRENCIES_API_URL_ERROR)
        with pytest.raises(Exception):
            self.call_command(currencies_url="")