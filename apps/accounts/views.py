from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages

import requests

from .forms import LoginForms


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        login_form = LoginForms(request.POST)
        # Obtenha os dados do formulário de login
        username = login_form['username'].value()
        password = login_form['password'].value()
        
        # Endpoint do servidor que emite o token
        server_url = settings.URL_API_SIMPLE_JWT 

        # Dados para a autenticação
        payload = {
            "username": username,
            "password": password
        }
        
        # Faça a requisição para obter o token
        try:
            response = requests.post(server_url, json=payload, timeout=10)
            response.raise_for_status()
            return redirect('home')  # Redirecione após login bem-sucedido
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                messages.error(request, f'Erro ao efetuar login: {response.status_code} - {response.text}')
                
            elif response.status_code == 500:
                messages.error(request, f'Erro ao efetuar login: {response.status_code} - {response.text}')
                
            else:
                messages.error(request, f'Erro inesperado: {response.status_code} - {response.text}')
        
        except requests.RequestException as e:
            messages.error(request, f'Erro ao efetuar login: {response.status_code} - {response.text}')
    

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

