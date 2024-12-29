from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer

import os

from .models import CustomUser
from .forms import LoginForms, ProfileForms
from apps.simpleJWT.utils import getting_access_token, make_request_in_api


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        login_form = LoginForms(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            access_response = getting_access_token(request=request, username=username, password=password)
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

    form_data = {**member_response, **user_response}
    profile_forms = ProfileForms(form_data=form_data, functions_data=functions_response)
    
    # Atualizando as informaçoes do usuario
    if request.method == 'POST':
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
            
            # Eliminado Caracteres que não sejam digitos
            clean_cell_phone = "".join([digit for digit in cell_phone if digit.isdigit()])
            
            member_data = {
                "name": name,
                "availability": availability,
                "cell_phone": clean_cell_phone,
                # convertendo para inteiro
                "function": [int(item) for item in function]
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
            patch_user = make_request_in_api(
                endpoint='user/',
                id=user.id,
                request_method='PATCH',
                payload=user_data,
                request=request
            )

            patch_member = make_request_in_api(
                endpoint='member/',
                id=member_id,
                request_method='PATCH',
                payload=member_data,
                request=request,
                files=files_data
            )

            functions_response = make_request_in_api(
                endpoint='member-functions/',
                request_method='GET',
                request=request
            )

            messages.success(request, 'Dados atualizados.')
            return redirect('my_profile')

    return render(request, 'accounts/my_profile.html', 
        {
            'member': member_response,
            'profile_forms': profile_forms,
            "user": user
        }
    )
