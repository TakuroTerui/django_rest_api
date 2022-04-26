from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

class Entry(models.Model):
  STATUS_DRAFT = 'draft'
  STATUS_PUBLIC = 'public'
  STATUS_SET = (
    (STATUS_DRAFT, '下書き'),
    (STATUS_PUBLIC, '公開中'),
  )
  title = models.CharField(max_length = 128)
  body = models.TextField()
  created_at = models.DateField(auto_now_add = True)
  updated_at = models.DateField(auto_now = True)
  status = models.CharField(choices = STATUS_SET, default = STATUS_DRAFT, max_length = 8)
  author = models.ForeignKey(User, related_name = 'entries', on_delete=models.CASCADE)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  """
  ユーザ新規作成時、自動的にTOKENを発行する。
  """
  if created:
    Token.objects.create(user=instance)