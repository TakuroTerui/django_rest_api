from rest_framework import routers
from .views import UserViewSet, EntryViewSet, EntryRegister, PokemonRegister, ImageViewSet, PartyViewSet
from django.conf.urls import include, url
from django.urls import path

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('entries', EntryViewSet)
router.register('register', EntryRegister)
router.register('pokemon', PokemonRegister)
router.register('predict', ImageViewSet)
router.register('party', PartyViewSet)