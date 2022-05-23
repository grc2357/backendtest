import pytest
from django.test import Client

pytestmark = [pytest.mark.django_db]

GRAPHQL_URL = "/graphql/"


def test_graphql_countries():

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

    client = Client()
    response = client.post(
        GRAPHQL_URL,
        {"query": query},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json().get("errors") is None

    # TODO Make assertions on the returned JSON

    # TODO Make assertions on the number of database queries


# TODO Test querying with the filter as well
