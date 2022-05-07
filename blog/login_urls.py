from . import views
from .views import Login
from django.urls import path

urlpatterns = [
	path('login', Login.as_view())
]