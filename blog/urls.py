from rest_framework import routers
from .views import UserViewSet, EntryViewSet


router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('entries', EntryViewSet)