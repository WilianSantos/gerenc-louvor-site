from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.conf import settings
from django.http.response import HttpResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import os

import requests

from invitations.models import Invitation

from .models import CustomUser
from .forms import LoginForms, ProfileForms, ChangePasswordForms
from apps.simpleJWT.utils import make_request_in_api, handle_request_errors


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # Formulario para renovação de senha
        if form_type == 'password_recovery':
            email_password_recovery = request.POST.get("emailPasswordRecovery")
            new_password = request.POST.get('newPassword')
            server_url = getattr(settings, "URL_API", None)
            if not server_url:
                return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
            server_url += 'request-password-reset/'
            data = {"email": email_password_recovery}
            send_email = requests.post(url=server_url, json=data)
            response = send_email.json()
            provisional_token = response.get('reset_token')
            try:
                validate_password(new_password)
                
            except ValidationError as e:
                message_error = ', '.join(e.messages)
                messages.error(request, message_error)
            
            try:
                data_password = {
                    "token": provisional_token,
                    "new_password": new_password
                }
                url = getattr(settings, "URL_API", None) + 'reset-password/'
                response_reset = requests.post(url=url, json=data_password)
                response_reset.raise_for_status()
                messages.success(request, 'Senha atualizada.')
                logout(request)
            except requests.exceptions.HTTPError as e:
                messages.error(request, f'{e.response.text.lower()}')

        # Formulario para logar
        if form_type == 'login_with_jwt':
            login_form = LoginForms(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                server_url = getattr(settings, "URL_API_SIMPLE_JWT", None)
                if not server_url:
                    return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
                login_data = {"username": username, "password": password}
                access_response = handle_request_errors(
                    request=request, 
                    func=requests.post, 
                    url=server_url, 
                    json=login_data, 
                    timeout=10
                )
                # Capturar mensagens adicionadas durante a requisição
                error_messages = [msg.message for msg in messages.get_messages(request) if msg.level_tag == 'error']
                if error_messages:
                    return render(request, 'accounts/login.html', {'login_form': login_form})
                
                user_id = access_response.get('user_id')
                member_id = access_response.get('member_id')
                # Criptografando os dados
                signer = Signer()
                access_token = access_response.get('access')
                signed_access_token = signer.sign_object(access_token)
                refresh_token = access_response.get('refresh')
                signed_refresh_token = signer.sign_object(refresh_token)
                #Custom é o banco customizado do user
                user, _ = CustomUser.objects.get_or_create(
                    id=user_id, 
                    defaults={"username": username, "member_id": member_id}
                )
                user.access_token = signed_access_token
                user.refresh_token = signed_refresh_token
                user.save()
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Dados inválidos no formulário.")

    return render(request, 'accounts/login.html', {'login_form': login_form})

@login_required
def my_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id
    
    member_response = make_request_in_api(
        endpoint='member/', 
        id=member_id, 
        request_method='GET', 
        request=request
    )

    user_response = make_request_in_api(
        endpoint='user/',
        id=user.id,
        request_method='GET',
        request=request
    )

    functions_response = make_request_in_api(
        endpoint='member-functions/',
        request_method='GET',
        request=request
    )

    change_password_forms = ChangePasswordForms()

    form_data = {**member_response, **user_response}
    profile_forms = ProfileForms(form_data=form_data, functions_data=functions_response)
    
    # Atualizando as informaçoes do usuario
    if request.method == 'POST':
        # Identifica o formulário através de um input com propriedade hidden
        form_type = request.POST.get('form_type')
        if form_type == 'profile':
            # Formulario do perfil
            profile_forms = ProfileForms(request.POST, functions_data=functions_response)
            if profile_forms.is_valid():
                # Dados do member/
                name = profile_forms.cleaned_data['name']
                availability = profile_forms.cleaned_data['availability']
                cell_phone = profile_forms.cleaned_data['cell_phone']
                profile_picture = profile_forms.cleaned_data['profile_picture']
                function = profile_forms.cleaned_data['function']
                # Dados do user/
                username = profile_forms.cleaned_data['username']
                first_name = profile_forms.cleaned_data['first_name']
                last_name = profile_forms.cleaned_data['last_name']
                email = profile_forms.cleaned_data['email']
                
                member_data = {
                    "name": name,
                    "availability": availability,
                    "cell_phone": cell_phone,
                    "function": function
                }
                user_data = {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                }
                
                picture = None
                if profile_picture:
                    # salvando imagem no site
                    user.profile_picture = profile_picture
                    user.save()
                    picture = user.profile_picture.path

                if picture and os.path.exists(picture):
                    files_data = {"profile_picture": open(picture, 'rb')}
                else:
                    files_data = None

                # Fazendo Requisições
                make_request_in_api(
                    endpoint='user/',
                    id=user.id,
                    request_method='PATCH',
                    payload=user_data,
                    request=request
                )

                make_request_in_api(
                    endpoint='member/',
                    id=member_id,
                    request_method='PATCH',
                    payload=member_data,
                    request=request,
                    files=files_data
                )

                messages.success(request, 'Dados atualizados.')
                return redirect('my_profile')
            
        elif form_type == 'change_password':
            # Formulario de atualização de senha
            change_password_forms = ChangePasswordForms(request.POST)
            if change_password_forms.is_valid():
                old_password = change_password_forms.cleaned_data['old_password']
                new_password = change_password_forms.cleaned_data['new_password']
                
                data_change_password = {
                    "old_password": old_password,
                    "new_password": new_password
                }

                make_request_in_api(
                    endpoint='change-password/',
                    request_method='POST',
                    request=request,
                    payload=data_change_password
                )
                messages.success(request, 'Dados atualizados.')
            
                return redirect('my_profile')
            else:
                active_tab = 'change-password'
                return render(request, 'accounts/my_profile.html', 
                    {
                        'member': member_response,
                        'profile_forms': profile_forms,
                        "user": user,
                        'change_password_forms': change_password_forms,
                        'active_tab': active_tab
                    }
                )
            
    
    # Determina a aba ativa
    active_tab = request.GET.get('tab', 'edit-profile')


    return render(request, 'accounts/my_profile.html', 
        {
            'member': member_response,
            'profile_forms': profile_forms,
            "user": user,
            'change_password_forms': change_password_forms,
            'active_tab': active_tab
        }
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Login encerrado com sucesso!")
    return redirect('login_with_jwt')
