from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from django.core.signing import Signer

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

            access_response = getting_access_token(username=username, password=password)

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

            signer = Signer()
            refresh_token = access_response.get('refresh')
            access_token = access_response.get('access')
            token_data = {'access_token': access_token, 'refresh_token': refresh_token}
            # Assinando os dados
            signed_data = signer.sign_object(token_data)
            request.session['encrypted_tokens'] = signed_data
            
            return redirect('dashboard')
        
        else:
            messages.error(request, "Dados inválidos no formulário.")

    return render(request, 'accounts/login.html', {'login_form': login_form})
