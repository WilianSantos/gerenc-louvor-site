from django.conf import settings

import requests

from rest_framework_simplejwt.tokens import RefreshToken

from .utils import handling_error


# Pegando token de acesso
def getting_access_token(username, password):
    server_url = getattr(settings, "URL_API_SIMPLE_JWT", None)
    if not server_url:
        return {
            'message_error': 'Configuração do servidor de autenticação está ausente.',
            'status': 400
        }
    
    login_data = {"username": username, "password": password}

    try:
        response = requests.post(server_url, json=login_data, timeout=10)
        response.raise_for_status()
        access_response = response.json()
        return access_response

    except requests.exceptions.HTTPError as e:
        message_error = handling_error(
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
    

# Fazendo a requisição
def make_request_in_api(endpoint, request_method, access_token, payload=None, id=None):
    server_url = getattr(settings, "URL_API", None)
    if not server_url:
        return {
            'message_error': 'Configuração do servidor de autenticação está ausente.',
            'status': 400
        }
    
    headers = {"Authorization": f"Bearer {access_token}"}

    match request_method:
        case 'GET':
            if id is not None:
                try:
                    server_url += endpoint + str(id) + '/'
                    response = requests.get(server_url, headers=headers, timeout=10)
                    response.raise_for_status()

                    get_response = response.json()

                    return get_response
                except requests.exceptions.HTTPError as e:
                    message_error = handling_error(
                        response_json=e.response.json(),  # A resposta do erro pode estar em `e.response`
                        response_code=e.response.status_code
                    )
                    return {'message_error': message_error}

                except requests.RequestException:
                    return {
                        'message_error': 'Erro de conexão com o servidor. Tente novamente mais tarde.',
                        'status': 503
                    }
                
            # Se id esta none
            try:
                server_url += endpoint
                response = requests.get(server_url, headers=headers, timeout=10)
                response.raise_for_status()

                get_response = response.json()

                return get_response
            except requests.exceptions.HTTPError as e:
                message_error = handling_error(
                    response_json=e.response.json(),  # A resposta do erro pode estar em `e.response`
                    response_code=e.response.status_code
                )
                return {'message_error': message_error}

            except requests.RequestException:
                return {
                    'message_error': 'Erro de conexão com o servidor. Tente novamente mais tarde.',
                    'status': 503
                }