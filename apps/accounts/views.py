from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages

import requests

from .forms import LoginForms
from .utils import handling_login_error


def login_with_jwt(request):
    login_form = LoginForms()

    # Autenticação de login
    if request.method == 'POST':
        login_form = LoginForms(request.POST)
        username = login_form['username'].value()
        password = login_form['password'].value()
        
        server_url = settings.URL_API_SIMPLE_JWT 

        login_data = {
            "username": username,
            "password": password
        }
        
        # Requisição do token
        try:
            response = requests.post(server_url, json=login_data, timeout=10)
            response.raise_for_status()

            return redirect('home')  
        
        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                message_error =  handling_login_error(response_json=response.json(), response_code=response.status_code)
                messages.error(request, message_error)
                
            elif response.status_code == 500:
                message_error =  handling_login_error(response_json=response.json(), response_code=response.status_code)
                messages.error(request, message_error)
                
            else:
                message_error =  handling_login_error(response_json=response.json(), response_code=response.status_code)
                messages.error(request, message_error)
        
        except requests.RequestException as e:
            message_error =  handling_login_error(response_json=response.json(), response_code=response.status_code)
            messages.error(request, message_error)
    
        return render(request, 'accounts/login.html', {'login_form': login_form})
    else:
        return render(request, 'accounts/login.html', {'login_form': login_form})


def refresh_token(request):
    refresh_token = request.session.get('refresh_token')
    
    if not refresh_token:
        return JsonResponse({'error': 'Token de atualização não encontrado'}, status=401)
    
    server_url = f'{settings.URL_API_SIMPLE_JWT}refresh/'  # Substitua pelo URL real
    response = requests.post(server_url, json={"refresh": refresh_token})
    
    if response.status_code == 200:
        tokens = response.json()
        request.session['access_token'] = tokens.get('access')
        return JsonResponse({'message': 'Token renovado com sucesso'})
    else:
        return JsonResponse({'error': 'Erro ao renovar token'}, status=response.status_code)
