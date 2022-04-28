from . import views
from django.urls import path

urlpatterns = [
	path('pokemon', views.pokemon, name='pokemon'),
	path('type', views.type, name='type'),
	path('pokemon-type', views.pokemon_type, name='pokemon-type'),
]