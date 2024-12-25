
# Captura de erro
def handling_error(response_json, response_code):
    error_code = response_code
    try:
        error_data = response_json
        detail_message = error_data.get('detail', 'Erro desconhecido.')
                    
        return f'Erro de autenticação: {error_code} - {detail_message}'
        
    except ValueError:
        return 'A resposta não é um JSON válido.'
