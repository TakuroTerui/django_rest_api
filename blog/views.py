from django.shortcuts import render
from rest_framework.permissions import AllowAny
import django_filters
from django.db import transaction
from rest_framework import viewsets, filters, generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, Entry
from .serializer import UserSerializer, EntrySerializer

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
  permission_classes = [AllowAny]
  queryset = Entry.objects.all()
  serializer_class = EntrySerializer

  def create(self, request):
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
      # 登録成功の場合はinsert recordを返す
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
