from rest_framework import serializers
from .models import User, Entry, Pokemon, PokemonType, PokemonImage, Party
from django.contrib.auth.hashers import make_password
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('username', 'email')

  def create(self, validated_data):
    password = validated_data.get('password')
    validated_data['password'] = make_password(password)
    return User.objects.create_user(**validated_data)

class EntrySerializer(serializers.ModelSerializer):
  author = UserSerializer()
  class Meta:
    model = Entry
    fields = ('id', 'title', 'body', 'created_at', 'status', 'author')

  def create(self, validated_data):
    entry = Entry()
    entry.title = validated_data['title']
    entry.body = validated_data['body']
    entry.author = validated_data['author']
    if 'status' in validated_data:
      entry.status = validated_data['status']
    entry.save()
    return entry

class SearchEntrySerializer(filters.FilterSet):
  search = filters.CharFilter(lookup_expr='contains')

  class Meta:
    model = Entry
    fields = ('title', 'body', 'created_at', 'status', 'author')

class PokemonTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = PokemonType
    fields = ('type_name',)

class PokemonSerializer(serializers.ModelSerializer):
  pokemons = PokemonTypeSerializer(many=True)
  class Meta:
    model = Pokemon
    fields = '__all__'

class SearchPokemonSerializer(filters.FilterSet):
  search = filters.CharFilter(lookup_expr='contains')

  class Meta:
    model = Pokemon
    fields = '__all__'

class PokemonPagination(PageNumberPagination):
  page_size = 30
  page_size_query_param = 'page_size'

class EntryPagination(PageNumberPagination):
  page_size = 30
  page_size_query_param = 'page_size'

class PokemonImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = PokemonImage
    fields = '__all__'

class PartySerializer(serializers.ModelSerializer):
  class Meta:
    model = Party
    fields = '__all__'