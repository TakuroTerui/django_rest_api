from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny
import django_filters
from django.db import transaction
from rest_framework import viewsets, filters, generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, Entry
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