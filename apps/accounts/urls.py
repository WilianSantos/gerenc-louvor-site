from django.urls import path
from .views import login_with_jwt, my_profile

urlpatterns = [
    path('login/', login_with_jwt, name='login_with_jwt'),
    path('meu-perfil/', my_profile, name='my_profile'),
]