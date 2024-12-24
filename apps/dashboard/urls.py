from django.urls import path
from .views import dashboard

urlpatterns = [
    path('inicio/', dashboard, name='dashboard'),
]