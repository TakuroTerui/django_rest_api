from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny
from django.conf import settings
import django_filters
import csv
from django.db import transaction
from io import TextIOWrapper
from rest_framework import viewsets, filters, generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FileUploadParser
from .models import User, Entry, Pokemon, PokemonType, PokemonTypeRelation, PokemonImage, PokemonPredict
from .serializer import UserSerializer, EntrySerializer, SearchEntrySerializer, PokemonSerializer, SearchPokemonSerializer, PokemonPagination, PokemonImageSerializer
import pytorch_lightning as pl
import torchvision
from torchvision import transforms
from torchvision import datasets
from torchvision.models import resnet18
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchmetrics
from torchmetrics.functional import accuracy
from PIL import Image
import base64
from django.core.files.base import ContentFile
import uuid
import os

class Net(pl.LightningModule):
  def __init__(self):
    super().__init__()
    self.feature = resnet18(pretrained=True)
    self.fc = nn.Linear(1000, 151)

  def forward(self, x):
    h = self.feature(x)
    h = self.fc(h)
    return h

  def training_step(self, batch, batch_idx):
    x, t = batch
    y = self(x)
    loss = F.cross_entropy(y, t)
    self.log('train_loss', loss, on_step=False, on_epoch=True)
    self.log('train_acc', accuracy(y.softmax(dim=-1), t), on_step=False, on_epoch=True)
    return loss

  def validation_step(self, batch, batch_idx):
    x, t = batch
    y = self(x)
    loss = F.cross_entropy(y, t)
    self.log('val_loss', loss, on_step=False, on_epoch=True)
    self.log('val_acc', accuracy(y.softmax(dim=-1), t), on_step=False, on_epoch=True)
    return loss

  def test_step(self, batch, batch_idx):
    x, t = batch
    y = self(x)
    loss = F.cross_entropy(y, t)
    self.log('test_loss', loss, on_step=False, on_epoch=True)
    self.log('test_acc', accuracy(y.softmax(dim=-1), t), on_step=False, on_epoch=True)
    return loss

  def configure_optimizers(self):
    optimizer = torch.optim.SGD(self.parameters(), lr=0.01)
    return optimizer

# ネットワークの準備
net = Net()
# 重みの読み込み
net.load_state_dict(torch.load('model/image.pt'))
net.eval()

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  # 動作確認用
  permission_classes = [AllowAny]

class EntryViewSet(viewsets.ModelViewSet):
  queryset = Entry.objects.all()
  serializer_class = EntrySerializer
  filter_fields = ('author', 'status')
  # 動作確認用
  permission_classes = [AllowAny]

class EntryRegister(viewsets.ModelViewSet):
  permission_classes = [AllowAny]
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

class PokemonRegister(viewsets.ModelViewSet):
  queryset = Pokemon.objects.all()
  serializer_class = PokemonSerializer
  filter_class = SearchPokemonSerializer
  pagination_class = PokemonPagination
  permission_classes = [AllowAny]

  def create(self, request):
    return Response([], status=status.HTTP_400_BAD_REQUEST)

  def update(self, request, pk=None):
    return Response([], status=status.HTTP_400_BAD_REQUEST)

class ImageViewSet(viewsets.ModelViewSet):
  queryset = PokemonImage.objects.all()
  parser_class = (FileUploadParser,)
  permission_classes = [AllowAny]
  serializer_class = PokemonImageSerializer

  def create(self, request):
    ustr = uuid.uuid4()
    root_ext_pair = os.path.splitext(request.data['name'])
    file_name = str(ustr) + str(root_ext_pair[1])
    serializer = PokemonImageSerializer(
      data={'file': base64_file(request.data['file'], name=file_name)}
    )

    if serializer.is_valid():
      # pokemon_image保存
      serializer.save()

      image_url = '/media/{}'.format(file_name)
      image_id = serializer.data['id']
      image_object = PokemonImage.objects.get(id=image_id)
      predict_data = predict(image_url, image_object)
      return Response(predict_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def predict(image_url, image_object):
  image_url = str(settings.BASE_DIR) + image_url
  img = Image.open(image_url).convert('RGB')
  transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])
  img = transform(img)
  # 予測値の算出
  y = net(img.unsqueeze(0))
  # 確率に変換
  y = F.softmax(y)
  proba = torch.max(y).item() * 100
  # 予測ラベル
  y = torch.argmax(y)
  # 予測ポケモン
  predict = Pokemon.objects.order_by("name").values_list('pk', flat=True)
  pokemon = Pokemon.objects.get(pk=predict[y.item()])
  # 推論結果保存
  PokemonPredict.objects.create(
    pokemon_name=pokemon.name,
    proba=proba,
    image=image_object
  )
  result_list = {
    'proba' : round(proba),
    'pokemon_name': pokemon.name,
    'label': predict[y.item()]
  }
  return result_list

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

def base64_file(data, name):
  _format, _img_str = data.split(';base64,')
  _name, ext = _format.split('/')
  return ContentFile(base64.b64decode(_img_str), name='{}'.format(name))