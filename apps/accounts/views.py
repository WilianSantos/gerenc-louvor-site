from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from django.http import HttpResponse

from .models import CustomUser
from .forms import LoginForms
from .simple_jwt import getting_access_token


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        login_form = LoginForms(request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            access_response = getting_access_token(request=request, username=username, password=password)

            message_error = access_response.get('message_error')
            if message_error:
                return messages(request, f'{message_error} - {access_response['status']}')
        
            user_id = access_response.get('user_id')
            member_id = access_response.get('member_id')

            # Buscar ou criar usuário localmente
            user, _ = CustomUser.objects.get_or_create(
                id=user_id, 
                defaults={"username": username, "member_id": member_id}
            )
            login(request, user)

            refresh_token = access_response.get('refresh')
            request.session['refresh_token'] = refresh_token

            access_token = access_response.get('access')
            request.session['access_token'] = access_token
            
            return redirect('dashboard')
        
        else:
            messages.error(request, "Dados inválidos no formulário.")

    return render(request, 'accounts/login.html', {'login_form': login_form})
