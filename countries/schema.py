from ariadne import gql
from ariadne import ObjectType, QueryType, make_executable_schema

from countries.models import Country

type_defs = gql(
    """
    type Country {
        name: String!
        symbol: String!
        currencies: [Currency!]!
    }
    type Currency {
        name: String!
        symbol: String!
    }
    type Query {
        countries(search: String): [Country!]!
    }
"""
)


query = QueryType()
country = ObjectType("Country")

@query.field("countries")
def resolve_countries(*_, search=None):
    return Country.objects.order_by("name")

@country.field("currencies")
def resolve_country_currencies(obj, *_):
    return obj.currencies.all()


schema = make_executable_schema(type_defs, query, country)
