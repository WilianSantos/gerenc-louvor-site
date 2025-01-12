from django.urls import path
from .views import music

urlpatterns = [
    path('musicas/', music, name='music'),
]