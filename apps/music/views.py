from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from apps.requests_in_api.utils import error_checking, get_access_token, handle_request_errors
from apps.accounts.models import CustomUser
from .forms import MusicForms, FileUploadForm

import fitz  

import requests


@login_required
def music(request):
    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id

    # Determina a aba ativa no frontend
    active_tab = request.GET.get('tab', 'music')

    # Determina a pagina ativa para o header
    active_page = 'music'

    tinymce_url = getattr(settings, "TINYMCE_JS_URL", None) 
    if not tinymce_url:
        messages.error(request, 'Configuração da url do tinymce ausente.')
    
    server_url = getattr(settings, "URL_API", None)
    if not server_url:
        return messages.error(request, 'Configuração do servidor de autenticação está ausente. - Status: 400')
    
    access_token = get_access_token(request)
    headers = {"Authorization": f"Bearer {access_token}"}

    member_url = server_url + 'member/' + str(member_id) + '/'
    member_response = handle_request_errors(
        request=request, 
        func=requests.get,
        url=member_url,
        headers=headers, 
        timeout=10
    )
    # Verificação dos erros
    error_checking(request=request, response=member_response)
    member_response = member_response.get('data')

    music_categorys_url = server_url + 'music-category/'

    music_categorys_response = handle_request_errors(
        request=request,
        func=requests.get,
        url=music_categorys_url,
        headers=headers, 
        timeout=10
    )
    # Verificação dos erros
    error_checking(request=request, response=music_categorys_response)
    music_categorys_response =music_categorys_response.get('data')

    if not member_response:
        logout(request)
        return redirect('login_with_jwt')
    
    # Carregando formularios
    music_forms = MusicForms(categorys_data=music_categorys_response)
    file_upload_forms = FileUploadForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'input_file':
            file_upload_forms = FileUploadForm(request.POST, request.FILES)
            if file_upload_forms.is_valid():
                uploaded_file = file_upload_forms.cleaned_data['file']

                if uploaded_file:
                    # Salve o arquivo no servidor
                    fs = FileSystemStorage()
                    file_path = fs.save(uploaded_file.name, uploaded_file)
                    file_full_path = fs.path(file_path)  # Caminho completo do arquivo salvo

                    
                
                    doc = fitz.open(file_full_path)
                    text = ""
                    for page in doc:
                        text += page.get_text("html")
                    
                    # Atualiza o campo music_text com o conteúdo extraído
                    music_forms.fields['music_text'].initial = text

                    active_tab = 'add-music'

    return render(request, 'music/music.html', {
        'member': member_response,
        'music_forms': music_forms,
        'file_upload_forms': file_upload_forms,
        'active_tab': active_tab,
        'active_page': active_page,
        'tinymce_url': tinymce_url
    })
