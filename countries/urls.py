from django.urls import path
from ariadne_django.views import GraphQLView
from .schema import schema

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("graphql/", GraphQLView.as_view(schema=schema), name="graphql"),
]
