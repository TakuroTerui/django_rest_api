from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import hashlib

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
  favorites = models.ManyToManyField(User, through='Favorite', related_name='favorites')

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  """
  ユーザ新規作成時、自動的にTOKENを発行する。
  """
  if created:
    Token.objects.create(user=instance)

class Pokemon(models.Model):
  name = models.CharField('名前', max_length=12)
  hit_points = models.IntegerField('HP')
  attack = models.IntegerField('攻撃')
  defense = models.IntegerField('防御')
  special_attack = models.IntegerField('特攻')
  special_defense = models.IntegerField('特防')
  speed = models.IntegerField('素早さ')
  parties = models.ManyToManyField(User, through='Party', related_name='parties')

  def __str__(self):
    return self.name

class PokemonType(models.Model):
  type_name = models.CharField('タイプ', max_length=5)
  pokemons = models.ManyToManyField(Pokemon, through='PokemonTypeRelation', related_name='pokemons')

  def __str__(self):
    return self.type_name

class PokemonTypeRelation(models.Model):
  pokemon_id = models.ForeignKey('Pokemon', on_delete=models.CASCADE)
  type_id = models.ForeignKey('PokemonType', on_delete=models.CASCADE)

class Party(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  pokemon_id = models.ForeignKey(Pokemon, on_delete=models.CASCADE)

  def __str__(self):
    return self.pokemon_id.name

class PokemonImage(models.Model):
  file = models.FileField(blank=False, null=False)

class PokemonPredict(models.Model):
  pokemon_name = models.CharField('名前', max_length=12, blank=True, null=True)
  proba = models.FloatField(default=0.0, blank=True, null=True)
  image = models.OneToOneField(PokemonImage, on_delete=models.CASCADE)
  created_date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return '推論:' + self.pokemon_name

class RefreshToken(models.Model):
  @staticmethod
  def create(user: User):
    if Token.objects.filter(user=user).exists():
      Token.objects.get(user=user).delete()

    dt = timezone.now()
    str = user.email + user.password + dt.strftime('%Y%m%d%H%M%S%f')
    hash = hashlib.sha1(str.encode('utf-8')).hexdigest()

    token = Token.objects.create(
      user=user,
      key=hash,
    )
    return token

class Favorite(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  entry_id = models.ForeignKey(Entry, on_delete=models.CASCADE)
