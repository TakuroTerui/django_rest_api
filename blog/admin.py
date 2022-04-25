from django.contrib import admin
from .models import User, Entry

@admin.register(Entry)
class Entry(admin.ModelAdmin):
  pass
