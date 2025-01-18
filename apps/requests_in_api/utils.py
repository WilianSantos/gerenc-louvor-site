from django.contrib import messages
from django.shortcuts import redirect
from django.core.signing import Signer
from django.conf import settings

import requests

from apps.accounts.models import CustomUser


def error_checking(request, response):
    if response.get('status_code') != 200:
        if response.get('token_not_valid'):
            messages.error(request, response.get('token_not_valid'))
            redirect('login_with_jwt')
        
        elif response.get('detail_error'):
            messages.error(request, response.get('detail_error'))

#TODO Juntar as duas funções de requisição em uma so para simplificar o codigo
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
        return {"data": response.json(), "status_code": 200}

    except requests.exceptions.HTTPError as e:
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
    try:
        user = CustomUser.objects.get(id=request.user.id)
        
        # Recuperando dados e verificando
        signer = Signer()
        encrypted_refresh_token = user.refresh_token
        decrypting_refresh_token = signer.unsign_object(encrypted_refresh_token)
        refresh_token = decrypting_refresh_token
        
        if not refresh_token:
            messages.error(request, 'O token de atualização não é válido. Faça login novamente.')
            return redirect('login_with_jwt')
        
        server_url = getattr(settings, "URL_API_SIMPLE_JWT_REFRESH", None)
        if not server_url:
            messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
            return redirect('login_with_jwt')
        
        data = {"refresh": refresh_token}
        response = requests.post(url=server_url, data=data, timeout=10)
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 200:
            access_response = response.json()
            new_access_token = access_response.get('access')
            
            if not new_access_token:
                messages.error(request, 'Falha ao obter o novo token de acesso.')
                return redirect('login_with_jwt')
            
            # Criptografando os dados e salvando no banco
            signed_access_token = signer.sign_object(new_access_token)
            user.access_token = signed_access_token
            user.save()
            
            return new_access_token
        else:
            messages.error(request, f'Erro na renovação do token: {response.status_code}')
            return redirect('login_with_jwt')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao renovar o token: {str(e)}')
        return redirect('login_with_jwt')


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
            if files:
                delete_response = handle_request_errors(
                request=request, 
                func=requests.delete,
                url=server_url,
                headers=headers,
                files=files, 
                timeout=10
            )

            delete_response = handle_request_errors(
                request=request, 
                func=requests.delete,
                url=server_url,
                headers=headers, 
                timeout=10
            )
            return delete_response
        