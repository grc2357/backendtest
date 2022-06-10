from ariadne import gql
from ariadne import ObjectType, QueryType, make_executable_schema

from countries.models import Country

from django.db.models import Q

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

# Notes on solution.
# Task 1
# To include the search term, a simple filter was added to the existing query.
# The keyword icontains is used because it's the case-insensitive
# version of contains.

# Task 2
# To me Django's prefetch_related seems to be a tool that is highly suited, 
# in fact, designed for such a task.
# Aside: I am aware of blogs in which the authors build their own dataloaders 
# to handle the n+1 problem when working with GraphQL, so there may be an 
# issue with using prefetch_related with GraphQL of which I am unaware, but 
# based on the unit tests, it seems to work as expected, at least in this case.

@query.field("countries")
def resolve_countries(*_, search=None):
    if search:
        # Handle a query with a search term.
        return Country.objects.order_by("name").filter(
            Q(name__icontains=search) | Q(symbol__icontains=search)
            ).prefetch_related("currencies")
    return Country.objects.order_by("name").prefetch_related("currencies")

@country.field("currencies")
def resolve_country_currencies(obj, *_):
    return obj.currencies.all()

schema = make_executable_schema(type_defs, query, country)