import pytest
from pytest_django.asserts import assertTemplateUsed

import test_syncdata

from django.test import Client

pytestmark = [pytest.mark.django_db]

GRAPHQL_URL = "/graphql/"

def test_graphql_countries(django_assert_max_num_queries):
    # For the query without a search term the test criteria are kept
    # more general than the test criteria for specific search terms.
    # So, even if all countries are remove from the DB, the test is passed.
    # It is also the reason for the use of the more general 
    # django_assert_max_num_queries.

    query = """
    query {
        countries {
            name
            symbol
            currencies {
                name
                symbol
            }
        }
    }
    """

    # As prefetch_related is being used in schema.py, there should, in 
    # general, be at most two queries, namely, the original query and the 
    # query fetching the currencies.
    client = Client()
    with django_assert_max_num_queries(2):
        response = client.post(
            GRAPHQL_URL,
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 200
    assert response.json().get("errors") is None

    # TODO Make assertions on the returned JSON
    assert "data" in response.json()
    assert "countries" in response.json().get("data")

    # TODO Make assertions on the number of database queries
    # Done above
    
# TODO Test querying with the filter as well

def test_graphql_countries_aus_filter(django_assert_num_queries):
    # A search for "gbr" should return a list containing only Australia and
    # Austria, in that order.

    query = """
    query {
        countries(search:"aus") {
            name
            symbol
            currencies {
                name
                symbol
            }
        }
    }
    """

    # As prefetch_related is being used with the filter in schema.py, there 
    # should be exactly two queries, namely, the original query and the query 
    # fetching the currencies.
    client = Client()
    with django_assert_num_queries(2):
        response = client.post(
            GRAPHQL_URL,
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 200
    assert response.json().get("errors") is None

    # TODO Make assertions on the returned JSON

    # Check that the countries being returned are Australia and Austria.
    assert len(response.json().get("data").get("countries")) == 2
    assert response.json().get("data").get("countries")[0].get(
        "name") == "Australia"
    assert response.json().get("data").get("countries")[1].get(
        "name") == "Austria"
    
    # TODO Make assertions on the number of database queries
    # Done above.

def test_graphql_countries_gbr_filter(django_assert_num_queries):
    # A search for "gbr" should return a list containing only the UK.

    query = """
    query {
        countries(search:"gbr") {
            name
            symbol
            currencies {
                name
                symbol
            }
        }
    }
    """

    # As prefetch_related is being used with the filter in schema.py, there 
    # should be exactly two queries, namely, the original query and the query 
    # fetching the currencies.
    client = Client()
    with django_assert_num_queries(2):
        response = client.post(
            GRAPHQL_URL,
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 200
    assert response.json().get("errors") is None

    # TODO Make assertions on the returned JSON

    # Check that the country being returned is the UK.
    assert len(response.json().get("data").get("countries")) == 1
    name_gbr = "United Kingdom of Great Britain and Northern Ireland"
    assert response.json().get("data").get("countries")[0].get(
        "name") == name_gbr
    
    # TODO Make assertions on the number of database queries
    # Done above.

def test_graphql_countries_zzz_filter(django_assert_num_queries):
    # A search for "zzz" should return an empty list.

    query = """
    query {
        countries(search:"zzz") {
            name
            symbol
            currencies {
                name
                symbol
            }
        }
    }
    """

    # As prefetch_related is being used with the filter in schema.py, there 
    # should be exactly one query, namely, the original query, this is because 
    # there are no currencies to fetch.
    client = Client()
    with django_assert_num_queries(1):
        response = client.post(
            GRAPHQL_URL,
            {"query": query},
            content_type="application/json",
        )

    assert response.status_code == 200
    assert response.json().get("errors") is None

    # TODO Make assertions on the returned JSON

    # Check that the an empty list of countries is being returned.
    assert len(response.json().get("data").get("countries")) == 0
    
    # TODO Make assertions on the number of database queries
    # Done above.


# Bonus Task
# The code for the bonus task is in test_syncdata.py.
# pytest --cov should give 100% on everything except views.py which
# I have not modified or tested.