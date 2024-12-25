from django.conf import settings
from django.http import HttpResponse

import requests

from rest_framework_simplejwt.tokens import RefreshToken


# Captura de erro
def handling_login_error(response_json, response_code):
    error_code = response_code
    try:
        error_data = response_json
        detail_message = error_data.get('detail', 'Erro desconhecido.')
                    
        return f'Erro de autenticação: {error_code} - {detail_message}'
        
    except ValueError:
        return 'A resposta não é um JSON válido.'
    

# Pegando token de acesso
def getting_access_token(request, username, password):
    server_url = getattr(settings, "URL_API_SIMPLE_JWT", None)
    if not server_url:
        return {
            'message_error': 'Configuração do servidor de autenticação está ausente.',
            'status': 400
        }
    
    login_data = {"username": username, "password": password}

    try:
        # Recuperar o refresh token do cookie
        refresh_token_cookie = request.COOKIES.get("refresh_token")

        if not refresh_token_cookie:
            response = requests.post(server_url, json=login_data, timeout=10)
            response.raise_for_status()

            access_response = response.json()

            # Adicionando o refresh ao Cookies HttpOnly
            refresh_token = access_response.get('refresh')
            cookie = HttpResponse(access_response)
            cookie.set_cookie(
                key="refresh_token", 
                value=refresh_token,
                httponly=True,  
                secure=True,    
                samesite="Lax" 
            )
            

            user_id = access_response.get('user_id')
            access_token = access_response.get('access')
            member_id = access_response.get('member_id')

            return {
                'access_token': access_token,
                'user_id': user_id,
                'member_id': member_id
            }
        
        # Se o refresh token já estiver presente, tentamos gerar um novo access token
        new_access_token = refresh_access_token(refresh_token_cookie)

        if 'message_error' in new_access_token:
            message_error = new_access_token['message_error']
            return {
                'message_error': message_error,
                'status': 401
            }

        token = new_access_token['access_token']
        return {'access_token': token}

    except requests.exceptions.HTTPError as e:
        message_error = handling_login_error(
            response_json=e.response.json(),  # A resposta do erro pode estar em `e.response`
            response_code=e.response.status_code
        )
        return {'message_error': message_error}

    except requests.RequestException:
        return {
            'message_error': 'Erro de conexão com o servidor. Tente novamente mais tarde.',
            'status': 503
        }
    

def refresh_access_token(refresh_token):
    try:
        # Usar o refresh token para gerar um novo access token
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)

        return {"access_token": new_access_token}
    except Exception:
        return {"message_error": "Token inválido ou expirado"}
