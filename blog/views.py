from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny
import django_filters
import csv
from django.db import transaction
from io import TextIOWrapper
from rest_framework import viewsets, filters, generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, Entry, Pokemon, PokemonType, PokemonTypeRelation
from .serializer import UserSerializer, EntrySerializer, SearchEntrySerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  # 動作確認用
  # permission_classes = [AllowAny]

class EntryViewSet(viewsets.ModelViewSet):
  queryset = Entry.objects.all()
  serializer_class = EntrySerializer
  filter_fields = ('author', 'status')
  # 動作確認用
  # permission_classes = [AllowAny]

class EntryRegister(viewsets.ModelViewSet):
  # permission_classes = [AllowAny]
  queryset = Entry.objects.all()
  serializer_class = EntrySerializer
  filter_class = SearchEntrySerializer

  def create(self, request):
    """
    新規作成
    """
    #HTTPリクエストヘッダーのトークン情報からユーザーを特定する
    token = self.request.META['HTTP_AUTHORIZATION'].split(" ")[1]
    #Userオブジェクトの取得
    user_obj = Token.objects.get(key=token).user

    request_data = request.data.copy()
    regist_data = {
      'title': request_data['title'],
      'body': request_data['body'],
      'author': user_obj.id
    }
    if ('status' in dict(request_data)):
      # ステータスの初期値はdraft(=下書き)
      regist_data['status'] = request_data['status']

    serializer = EntrySerializer(data=regist_data)
    if serializer.is_valid():
      serializer.save()
      # 登録成功の場合はinsertしたレコードを返す
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def update(self, request, pk=None):
    """
    更新
    """
    queryset = Entry.objects.all()
    entry = get_object_or_404(queryset, pk=pk)

    request_data = request.data.copy()
    regist_data = {}
    if ('status' in dict(request_data)):
      regist_data['status'] = request_data['status']
    if ('title' in dict(request_data)):
      regist_data['title'] = request_data['title']
    if ('body' in dict(request_data)):
      regist_data['body'] = request_data['body']

    serializer = EntrySerializer(instance=entry, data=regist_data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def pokemon(request):
  """
  pokemonsテーブルアップロード
  """
  if 'csv' in request.FILES:
    form_data = TextIOWrapper(request.FILES['csv'].file, encoding='utf-8')
    csv_file = csv.reader(form_data)
    header = next(csv_file)
    for line in csv_file:
      pokemon = Pokemon()
      pokemon.id = line[0]
      pokemon.name = line[1]
      pokemon.hit_points = line[2]
      pokemon.attack = line[3]
      pokemon.defense = line[4]
      pokemon.special_attack = line[5]
      pokemon.special_defense = line[6]
      pokemon.speed = line[7]
      pokemon.save()
    return render(request, 'upload.html')
  else:
    return render(request, 'upload.html')

def type(request):
  """
  pokemon_typesテーブルアップロード
  """
  if 'csv' in request.FILES:
    form_data = TextIOWrapper(request.FILES['csv'].file, encoding='utf-8')
    csv_file = csv.reader(form_data)
    header = next(csv_file)
    for line in csv_file:
      type = PokemonType()
      type.id = line[0]
      type.type_name = line[1]
      type.save()
    return render(request, 'upload.html')
  else:
    return render(request, 'upload.html')

def pokemon_type(request):
  """
  pokemon_type_relationsテーブルアップロード
  """
  if 'csv' in request.FILES:
    form_data = TextIOWrapper(request.FILES['csv'].file, encoding='utf-8')
    csv_file = csv.reader(form_data)
    header = next(csv_file)
    for line in csv_file:
      pokemon_type = PokemonTypeRelation()
      pokemon_type.pokemon_id = Pokemon.objects.get(id=line[0])
      pokemon_type.type_id = PokemonType.objects.get(id=line[1])
      pokemon_type.save()
    return render(request, 'upload.html')
  else:
    return render(request, 'upload.html')