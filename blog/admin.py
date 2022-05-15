from django.contrib import admin
from .models import User, Entry, Pokemon, PokemonType, PokemonTypeRelation, Party, PokemonImage, PokemonPredict, Favorite

@admin.register(Entry)
class Entry(admin.ModelAdmin):
  pass

@admin.register(Pokemon)
class Pokemon(admin.ModelAdmin):
  pass

@admin.register(PokemonType)
class PokemonType(admin.ModelAdmin):
  pass

@admin.register(PokemonTypeRelation)
class PokemonTypeRelation(admin.ModelAdmin):
  pass

@admin.register(Party)
class Party(admin.ModelAdmin):
  pass

@admin.register(PokemonImage)
class PokemonImage(admin.ModelAdmin):
  pass

@admin.register(PokemonPredict)
class PokemonPredict(admin.ModelAdmin):
  pass

@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
  pass
