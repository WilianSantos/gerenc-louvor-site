from django.contrib import messages
from django.shortcuts import redirect
from django.core.signing import Signer
from django.conf import settings

import requests

from apps.accounts.models import CustomUser


def get_access_token(request):
    signer = Signer()
    encrypted_access_token = request.user.access_token
    decrypting_access_token = signer.unsign_object(encrypted_access_token)
    access_token = decrypting_access_token
    return access_token


def error_checking(request, response):
    if response.get('detail_error'):
        messages.error(request, response.get('detail_error'))

    elif response.get('token_not_valid'):
        messages.error(request, response.get('token_not_valid'))
        redirect('login_with_jwt')

    elif not response.get('detail_error') and not response.get('token_not_valid') and not response.get('data'):
        messages.error(request, str(response.get('status_code')))


#TODO Juntar as duas funções de requisição em uma so para simplificar o codigo
def handle_request_errors(request, func, *args, **kwargs):
    """
    Função utilitária para tratar erros de requisição.
    :param request: Objeto request do Django.
    :param func: Função de requisição (ex: requests.get, requests.post).
    :param args: Argumentos posicionais para a função.
    :param kwargs: Argumentos nomeados para a função.
    :return: Retorna uma chave com a resposata da requisição (data) e o status (status_code)
    Em caso de erro é retornado ou (token_not_valid) ou (refresh_token_not_valid) ou (detail_error) em vez de (data)

    # EX:
        response = handle_request_errors(
            request, requests.get, url=server_url, headers=headers, timeout=10
        )
    """
    try:

        response = func(*args, **kwargs)
        response.raise_for_status()
        return {"data": response.json(), "status_code": 200}

    except requests.exceptions.HTTPError as e:
        if not e.response.json():
            return {"status_code": e.response.status_code}
        
        response_http = e.response.json()
        code = response_http.get('code')

        if code == 'token_not_valid' and e.response.status_code == 401:
            # Access token expirado
            if "messages" in response_http:
                token_type = response_http["messages"][0].get("token_type")
                token_class = response_http["messages"][0].get("token_class")
                if token_type == "access" and token_class == "AccessToken":
                    new_access_token = refresh_access_token(request)
                    if not new_access_token:
                        return {"redirect": redirect('login_with_jwt'), "status_code": 401}
                    kwargs['headers'] = {"Authorization": f"Bearer {new_access_token}"}

                    try:
                        response_with_new_access = func(*args, **kwargs)
                        response_with_new_access.raise_for_status()
                        return {"data": response_with_new_access.json(), "status_code": 200}

                    except requests.exceptions.HTTPError as excp:
                        message_error = 'Erro ao renovar o token de acesso. Faça login novamente.\n'
                        error = handling_error(
                            message=message_error,
                            response_json=excp.response.json(),
                            response_status=excp.response.status_code
                        )
                        return {"token_not_valid": error, "status_code": excp.response.status_code}

        # Token Refresh expirado
        elif code == 'refresh_token_not_valid' and e.response.status_code == 401:
            message_error = 'Erro ao renovar o token de acesso. Faça login novamente.'
            error = handling_error(
                message=message_error,
                response_json=e.response.json(),
                response_status=401
            )
            return {"token_not_valid": error, "status_code": 401}

        if e.response.status_code == 400:
            error = handling_error(
                message="Erro", 
                response_json=e.response.json(),
                response_status=e.response.status_code
            )
            return {"detail_error": error, "status_code": e.response.status_code}

        # Erros de Conexão
        error = handling_error(
            message="Erro de conexão", 
            response_json=e.response.json(),
            response_status=e.response.status_code
        )
        return {"detail_error": error, "status_code": e.response.status_code}
    except requests.exceptions.Timeout:
        return {"detail_error": "A requisição ao servidor excedeu o tempo limite. Tente novamente", "status_code": 408}
    except requests.exceptions.ConnectionError:
        return {"detail_error": "Erro de conexão ao servidor. Tente novamente mais tarde", "status_code": 503}
    except Exception:
        return {"detail_error": "Erro inesperado", "status_code": 500}


# Captura de erro detail do SimpleJWT
def handling_error(response_json, message, response_status):
    error_data = response_json
    status = response_status

    detail_message = error_data.get('detail', 'Erro desconhecido.')
    return f'{message}: - {detail_message} - {status}'


def refresh_access_token(request):
    user = CustomUser.objects.get(id=request.user.id)
    
    # Recuperando dados e verificando
    signer = Signer()
    encrypted_refresh_token = user.refresh_token
    decrypting_refresh_token = signer.unsign_object(encrypted_refresh_token)
    refresh_token = decrypting_refresh_token
    
    if not refresh_token:
        messages.error(request, 'O token de atualização não existe. Faça login novamente.')
        return redirect('login_with_jwt')
    
    server_url = getattr(settings, "URL_API_SIMPLE_JWT_REFRESH", None)
    if not server_url:
        messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
        return redirect('login_with_jwt')
    
    try:
        data = {"refresh": refresh_token}
        response = requests.post(url=server_url, data=data, timeout=10)
        response.raise_for_status()

        access_response = response.json()
        new_access_token = access_response.get('access')
        
        if not new_access_token:
            messages.error(request, 'Falha ao obter o novo token de acesso. Faça o login novamente.')
            return redirect('login_with_jwt')
        
        # Criptografando os dados e salvando no banco
        signed_access_token = signer.sign_object(new_access_token)
        user.access_token = signed_access_token
        user.save()
        
        return new_access_token

    except requests.exceptions.HTTPError as excp:
        message_error = 'Erro na renovação do token'
        error = handling_error(
            message=message_error,
            response_json=excp.response.json(),
            response_status=excp.response.status_code
        )
        messages.error(request, error)
        return redirect('login_with_jwt')
    
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao renovar o token: {str(e)}')
        return redirect('login_with_jwt')
