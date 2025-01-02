from django.urls import path
from .views import login_with_jwt, my_profile, logout_view, create_user

urlpatterns = [
    path('login/', login_with_jwt, name='login_with_jwt'),
    path('invitations/accept/criar-usuario/', create_user, name='create_user'),
    path('invitations/accept/criar-usuario/<str:invite_key>/', create_user, name='create_user_link'),
    path('recuperar-senha/', login_with_jwt, name='password_recovery'),
    path('meu-perfil/', my_profile, name='my_profile'),
    path('alterar-senha/', my_profile, name='change_password'),
    path('sair/', logout_view, name='logout')
]