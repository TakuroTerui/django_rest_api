from rest_framework import serializers
from .models import User, Entry
from django.contrib.auth.hashers import make_password
from django_filters import rest_framework as filters

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('username', 'email')

  def create(self, validated_data):
    password = validated_data.get('password')
    validated_data['password'] = make_password(password)
    return User.objects.create(**validated_data)

class EntrySerializer(serializers.ModelSerializer):
  class Meta:
    model = Entry
    fields = ('title', 'body', 'created_at', 'status', 'author')

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