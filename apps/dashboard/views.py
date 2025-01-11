from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout

import re

from itsdangerous import URLSafeTimedSerializer

from apps.accounts.models import CustomUser, TokenRecord
from apps.requests_in_api.utils import make_request_in_api, error_checking


@login_required
def dashboard(request): 

    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id
    
    member_response = make_request_in_api(
        endpoint='member/', 
        id=member_id, 
        request_method='GET', 
        request=request
    )
    # Verificando erros
    error_checking(request=request, response=member_response)
    member_response = member_response.get('data')

    if not member_response:
        logout(request)
        return redirect('login_with_jwt')


    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'send_email':
            """
            POST recebido para enviar e-mail com um link criptografado 
            com o email e o token recebido da api para poder criar o usuário
            """
            email_list = request.POST['emails']

            if email_list:
                # Divide os e-mails e remove valores indesejados
                email_address = re.split(r'[,"]', email_list)
                email_address = [
                    email.strip('[] ').strip() for email in email_address 
                    if email.strip('[] ').strip()
                ]

                if not email_address:
                    messages.error(request, "Nenhum e-mail válido foi encontrado.")
                    return redirect("login_with_jwt")

                from_email = getattr(settings, "EMAIL_HOST_USER", None)
                if not from_email:
                    messages.error(request, "E-mail host não configurado.")
                    return redirect("login_with_jwt") 

                auth_s = URLSafeTimedSerializer(settings.SECRET_KEY)

                for email in email_address:
                    data_email = {"email": email}
                    token_response = make_request_in_api(
                        request=request,
                        endpoint="token-temporary/",
                        request_method="POST",
                        payload=data_email
                    )
                    error_checking(request=request, response=token_response)
                    token_response = token_response.get('data')

                    if not token_response:
                        return redirect('dashboard')

                    temporary_token = token_response.get("temporary_token")
                    

                    if not temporary_token:
                        messages.error(request, f"Erro ao gerar token para {email}. {temporary_token}")
                        continue  # Pula para o próximo e-mail se houver erro

                    signed_data = {"email": email, "token": temporary_token}
                    token = auth_s.dumps(signed_data, salt='email-invite')
                    if TokenRecord.objects.filter(temporary_token=token).exists():
                        token = auth_s.dumps(signed_data, salt='email-invite')

                    TokenRecord.objects.create(temporary_token=token, email=email)

                    link = request.build_absolute_uri(
                        reverse('create_user', args=[token])
                    )
                    
                    subject = "Você foi convidado para participar do nosso site!"
                    message = f"""
                        Olá,

                        Você foi convidado para participar do nosso site! Clique no link abaixo para aceitar o convite:
                        {link}

                        Este convite expira em 7 dias.
                    """
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=[email],
                        fail_silently=False,  # Gera exceções se ocorrer erro
                    )
                    
                    print(temporary_token)
                messages.success(request, "E-mails enviados com sucesso!")
            else:
                messages.error(request, "Adicione o e-mail para poder enviar.")

                        
    return render (request, 'dashboard/index.html', 
                    {
                        'member': member_response
                    })
