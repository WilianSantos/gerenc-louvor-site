from django.urls import path
from .views import login_with_jwt

urlpatterns = [
    path('login/', login_with_jwt, name='login_with_jwt'),
]