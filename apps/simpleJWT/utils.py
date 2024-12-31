from django.contrib import messages
from django.shortcuts import redirect
from django.core.signing import Signer
from django.conf import settings

import requests

import logging


logger = logging.getLogger(__name__)


def handle_request_errors(request, func, *args, **kwargs):
        """
        Função utilitária para tratar erros de requisição.
        :param request: Objeto request do Django.
        :param func: Função de requisição (ex: requests.get, requests.post).
        :param args: Argumentos posicionais para a função.
        :param kwargs: Argumentos nomeados para a função.
        :return: Resposta da requisição ou None em caso de erro.

        # EX:
            response = handle_request_errors(
                request, requests.get, url=server_url, headers=headers, timeout=10
            )
        """
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            response_http = e.response.json()
            code = response_http.get('code')
            if code == 'token_not_valid' and e.response.status_code == 401:
                new_access_token = refresh_access_token(request)
                kwargs['headers'] = {"Authorization": f"Bearer {new_access_token}"}
                return handle_request_errors(request, func, *args, **kwargs)
            
            return handling_error(
                request=request, 
                message="Erro de conexão", 
                response_code=e.response.status_code, 
                response_json=e.response.json()
            )
        except requests.exceptions.Timeout:
            return messages.error(request, "A requisição ao servidor excedeu o tempo limite.")
        except requests.exceptions.ConnectionError as e:
            return handling_error(
                request=request, 
                message="Erro de conexão ao servidor.", 
                response_code=e.response.status_code, 
                response_json=e.response.json()
            )
        except Exception as e:
            return handling_error(
                request=request, 
                message="Erro inesperado",
                response_code=e.response.status_code,
                response_json=e.response.json()
            )
        


# Captura de erro detail do SimpleJWT
def handling_error(request, response_json, response_code, message):
    error_code = response_code
    try:
        error_data = response_json
        detail_message = error_data.get('detail', 'Erro desconhecido.')
                    
        return messages.error(request, f'{message}: {error_code} - {detail_message}')
        
    except ValueError:
        return messages.error(request, 'A resposta não é um JSON válido.')


def refresh_access_token(request):
    # Recuperando dados e verificando
    signer = Signer()
    encrypted_refresh_token = request.user.refresh_token
    decrypting_refresh_token = signer.unsign_object(encrypted_refresh_token)
    refresh_token = decrypting_refresh_token  
    if not refresh_token:
        messages.error(request, 'Problema na conexão faça o login novamente')
        return redirect('login_with_jwt')
    
    server_url = getattr(settings, "URL_API_SIMPLE_JWT_REFRESH", None)
    if not server_url:
        return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
    
    data = {"refresh": refresh_token}
    response = handle_request_errors(
        request=request,
        func=requests.post,
        url=server_url,
        data=data,
        timeout=10
    )
    if not response or 'access' not in response:
        messages.error(request, 'Erro ao renovar o token de acesso. Faça login novamente.')
        return redirect('login_with_jwt')
    new_access_token = response.get('access')
    return new_access_token


def make_request_in_api(endpoint, request_method, request, payload=None, id=None, files=None):
    """
        Função resposavel por fazer requisições ao servidor
        user -> usuario
        endpoint -> é a rota ex(user/)
        request_method -> é tipo da requisição tem de ser passada em caixa alta ex(PUT)
        request -> Objeto request do Django.
        payload -> o corpo ou o conteudo da requisição ex({"username": username, "password": password})
        id -> o identificador da requisição
        files -> tratasse do arquivo que sera passado
    """
    
    # Recuperando dados e verificando
    signer = Signer()
    encrypted_access_token = request.user.access_token
    decrypting_access_token = signer.unsign_object(encrypted_access_token)
    access_token = decrypting_access_token

    encrypted_refresh_token = request.user.refresh_token
    decrypting_refresh_token = signer.unsign_object(encrypted_refresh_token)
    refresh_token = decrypting_refresh_token  

    if not access_token and not refresh_token:
        messages.error(request, 'Problema na conexão faça o login novamente')
        return redirect('login_with_jwt')

    server_url = getattr(settings, "URL_API", None)
    if not server_url:
        return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')

    headers = {"Authorization": f"Bearer {access_token}"}

    match request_method:
        case 'GET':
            if id is not None:
                server_url += endpoint + str(id) + '/'
                get_response = handle_request_errors(
                    request=request, 
                    func=requests.get,
                    url=server_url,
                    headers=headers, 
                    timeout=10
                )              
                return get_response
            # Se id esta none
            else:
                server_url += endpoint
                get_response = handle_request_errors(
                    request=request, 
                    func=requests.get,
                    url=server_url,
                    headers=headers, 
                    timeout=10
                )
                return get_response
            
        case 'PUT':
            server_url += endpoint + str(id) + '/'
            if files:
                #Adicionando o arquivo
                put_response = handle_request_errors(
                    request=request,
                    func=requests.put,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    files=files,
                    timeout=10
                )
            else:
                put_response = handle_request_errors(
                    request=request,
                    func=requests.put,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )
            return put_response

        case 'PATCH':
            server_url += endpoint + str(id) + '/'
            if files:
                #Adicionando o arquivo
                patch_response = handle_request_errors(
                    request=request,
                    func=requests.patch,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    files=files,
                    timeout=10
                )
            else:
                patch_response = handle_request_errors(
                    request=request,
                    func=requests.patch,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )
            return patch_response

        case 'POST':
            server_url += endpoint
            if files:
                #Adicionando o arquivo
                post_response = handle_request_errors(
                    request=request,
                    func=requests.post,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    files=files,
                    timeout=10
                )
            else:
                post_response = handle_request_errors(
                    request=request,
                    func=requests.post,
                    url=server_url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )
            return post_response

        case 'DELETE':
            server_url += endpoint + str(id) + '/'
            delete_response = handle_request_errors(
                request=request, 
                func=requests.delete,
                url=server_url,
                headers=headers, 
                timeout=10
            )
            return delete_response
        