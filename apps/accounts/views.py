import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import requests

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from .models import CustomUser, TokenRecord
from .forms import LoginForms, ProfileForms, ChangePasswordForms, CreateUserForms, MemberFunctionForms
from apps.simpleJWT.utils import make_request_in_api, handle_request_errors, error_checking


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # Formulario para renovação de senha
        if form_type == 'password_recovery':
            email_password_recovery = request.POST.get("emailPasswordRecovery")

            server_url = getattr(settings, "URL_API", None)
            if not server_url:
                return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
            server_url += 'request-password-reset/'
            
            data = {"email": email_password_recovery}

            token_response = handle_request_errors(
                func=requests.post,
                url=server_url,
                json=data
            )
            # Verificação dos erros
            error_checking(request=request, response=token_response)

            new_password = request.POST.get('newPassword')
            try:
                validate_password(new_password)
                
            except ValidationError as e:
                message_error = ', '.join(e.messages)
                messages.error(request, message_error)
            
            token_response = token_response.get('data')
            provisional_token = token_response.get('reset_token')
            
            data_password = {
                "token": provisional_token,
                "new_password": new_password
            }
            url = getattr(settings, "URL_API", None) + 'reset-password/'
            
            reset_password_response = handle_request_errors(
                func=requests.post,
                url=url,
                json=data_password
            )
            # Verificação dos erros
            error_checking(request=request, response=reset_password_response)

            messages.success(request, 'Senha atualizada.')
        
            #Garantindo que o usuario no cliente acesse com a nova senha para receber um novo token
            logout(request)
                        
                
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
                # Verificação dos erros
                error_checking(request=request, response=access_response)
                access_response = access_response.get('data')

                if not access_response:
                    return redirect('login_with_jwt')

                user_id = access_response.get('user_id')
                member_id = access_response.get('member_id')

                # Criptografando os dados
                signer = Signer()
                access_token = access_response.get('access')
                signed_access_token = signer.sign_object(access_token)
                refresh_token = access_response.get('refresh')
                signed_refresh_token = signer.sign_object(refresh_token)

                
                user, _ = CustomUser.objects.get_or_create(
                    id=user_id, 
                    defaults={"username": username, "member_id": member_id}
                )
                user.access_token = signed_access_token
                user.refresh_token = signed_refresh_token
                user.save()
                login(request, user)
                return redirect('dashboard')
            

    return render(request, 'accounts/login.html', {'login_form': login_form})

@login_required
def my_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id

    # Determina a aba ativa no frontend
    active_tab = request.GET.get('tab', 'edit-profile')
    
    member_response = make_request_in_api(
        endpoint='member/', 
        id=member_id, 
        request_method='GET', 
        request=request
    )
    # Verificação dos erros
    error_checking(request=request, response=member_response)
    member_response = member_response.get('data')
            
    user_response = make_request_in_api(
        endpoint='user/',
        id=user.id,
        request_method='GET',
        request=request
    )
    # Verificações dos erros
    error_checking(request=request, response=user_response)
    user_response = user_response.get('data')

    functions_response = make_request_in_api(
        endpoint='member-functions/',
        request_method='GET',
        request=request
    )
    # Verificação dos erros
    error_checking(request=request, response=functions_response)
    functions_response = functions_response.get('data')

    if not functions_response or not user_response or not member_response:
        logout(request)
        return redirect('login_with_jwt')
    
    # Carregando formularios da pagina
    change_password_forms = ChangePasswordForms()

    member_functions_forms = MemberFunctionForms()

    form_data = {**member_response, **user_response}
    profile_forms = ProfileForms(form_data=form_data, functions_data=functions_response)

    # Atualizando as informaçoes do usuario
    if request.method == 'POST':
        # Identifica o formulário através de um input com propriedade hidden
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            # Formulario do perfil
            profile_forms = ProfileForms(request.POST, request.FILES, functions_data=functions_response)
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
                
                files_data = None
                if profile_picture:
                    # Salvando a imagem no site
                    user.profile_picture = profile_picture
                    user.save()

                    with open(user.profile_picture.path, 'rb') as file:
                        files_data = {"profile_picture": file}

                        patch_response_member = make_request_in_api(
                            endpoint='member/',
                            id=member_id,
                            request_method='PATCH',
                            payload=member_data,
                            request=request,
                            files=files_data
                        )
                else:
                    patch_response_member = make_request_in_api(
                    endpoint='member/',
                    id=member_id,
                    request_method='PATCH',
                    payload=member_data,
                    request=request,
                )
                # Verificando erro da requisição
                error_checking(request=request, response=patch_response_member)

                patch_response_user = make_request_in_api(
                    endpoint='user/',
                    id=user.id,
                    request_method='PATCH',
                    payload=user_data,
                    request=request
                )
                # Verificando erro da requisição
                error_checking(request=request, response=patch_response_user)

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

                response_change_password = make_request_in_api(
                    endpoint='change-password/',
                    request_method='POST',
                    request=request,
                    payload=data_change_password
                )
                # Verificando erro da requisição
                error_checking(request=request, response=response_change_password)
                
                messages.success(request, 'Senha atualizada.')
            
                return redirect('my_profile')
            else:
                active_tab = 'change-password'
                return render(request, 'accounts/my_profile.html', 
                    {
                        'member': member_response,
                        "user": user,
                        'profile_forms': profile_forms,
                        'change_password_forms': change_password_forms,
                        'member_functions_forms': member_functions_forms,
                        'active_tab': active_tab
                    }
                )

        elif form_type == 'create_functions':
            # Formulario para criar função do usuario
            member_functions_forms = MemberFunctionForms(request.POST)
            if member_functions_forms.is_valid():
                functions_name = member_functions_forms.cleaned_data['functions_name']

                create_function_response = make_request_in_api(
                    request=request,
                    endpoint='member-functions/',
                    request_method='POST',
                    payload={"functions_name": functions_name}
                )
                # Verificando erro da requisição
                error_checking(request=request, response=create_function_response)
                messages.success(request, 'Função criada.')
            
                return redirect('my_profile')
            else:
                active_tab = 'create-functions'
                return render(request, 'accounts/my_profile.html', 
                    {
                        'member': member_response,
                        "user": user,
                        'profile_forms': profile_forms,
                        'change_password_forms': change_password_forms,
                        'member_functions_forms': member_functions_forms,
                        'active_tab': active_tab
                    }
                )

    return render(request, 'accounts/my_profile.html', 
        {
            'member': member_response,
            "user": user,
            'profile_forms': profile_forms,
            'change_password_forms': change_password_forms,
            'member_functions_forms': member_functions_forms,
            'active_tab': active_tab
        }
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Login encerrado com sucesso!")
    return redirect('login_with_jwt')


def create_user(request, signed_data):
    auth_s = URLSafeTimedSerializer(settings.SECRET_KEY)
    # 1 dias de validade (1 dias * 24 horas * 60 minutos * 60 segundos)
    # Tempo máximo para o token ser válido (por exemplo, 1 dia)
    max_age_seconds = 1 * 24 * 60 * 60

    try:
        # Decodifica os dados assinados
        decoded_data = auth_s.loads(signed_data, salt="email-invite", max_age=max_age_seconds)
        
        # Recupera os parâmetros
        email = decoded_data.get("email")
        token = decoded_data.get("token")

        token_record = TokenRecord.objects.filter(temporary_token=signed_data).first()

        if not token_record:
            messages.error(request, 'Este token é invalido.')
            return redirect('login_with_jwt')

        if token_record.is_used:
            messages.error(request, 'Este token já foi usado.')
            return redirect('login_with_jwt')

    except SignatureExpired:
        messages.error(request, "Este link expirou. Você precisa de outro link")
        return redirect('login_with_jwt')
    except BadSignature:
        messages.error(request, "Este link não é válido.")
        return redirect('login_with_jwt')
    
    create_user_forms = CreateUserForms()

    if request.method == 'POST':
        create_user_forms = CreateUserForms(request.POST)
        if create_user_forms.is_valid():
            username = create_user_forms.cleaned_data['username']
            first_name = create_user_forms.cleaned_data['first_name']
            last_name = create_user_forms.cleaned_data['last_name']
            password = create_user_forms.cleaned_data['password']
            cell_phone = create_user_forms.cleaned_data['cell_phone']

            data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "email": email,
                "cell_phone": cell_phone,
                "token": token
            }
            
            server_url = getattr(settings, "URL_API", None)
            if not server_url:
                return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')      

            server_url += 'register-user/'
            create_user_response = handle_request_errors(
                request=request,
                func=requests.post,
                url=server_url, 
                json=data, 
                timeout=10
            )
            # Verificando erro da requisição
            error_checking(request=request, response=create_user_response)
            create_user_response = create_user_response.get('data')
            if not create_user_response:
                return redirect('login_with_jwt')
            
            user_id = create_user_response.get('user_id')
            member_id = create_user_response.get('member_id')
            
            if not CustomUser.objects.filter(username=username).exists():
                CustomUser.objects.create_user(
                    id=user_id,
                    email=email, 
                    password=password, 
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    member_id=member_id
                )

            # Garantindo que o token não seja usado
            token_record.is_used = True
            token_record.save()

            messages.success(request, 'Usuário criado, entre com seu usuário e senha.')
            return redirect('login_with_jwt')

    return render(request, 'accounts/create_user.html', {
        'create_user_forms': create_user_forms,
        'signed_data': signed_data
    })
