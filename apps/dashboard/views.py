from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.conf import settings

import re

from invitations.models import Invitation

from apps.accounts.models import CustomUser
from apps.simpleJWT.utils import make_request_in_api


@login_required
def dashboard(request): 
    def send_invitation_email(email, base_url, temporary_token, from_email):
        customized_url = f"{base_url}?extra_param={temporary_token}"
        subject = "Você foi convidado para participar do nosso site!"
        message = f"""
            Olá,

            Você foi convidado para participar do nosso site! Clique no link abaixo para aceitar o convite:
            {customized_url}

            Este convite expira em 7 dias.
        """
        email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            bcc=[email],
        )
        email_message.send(fail_silently=False)

    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id
    
    member_response = make_request_in_api(
        endpoint='member/', 
        id=member_id, 
        request_method='GET', 
        request=request
    )
    # Garantindo que caso de algum erro o usuario seja redirecionado
    if isinstance(member_response, HttpResponseRedirect):
        return member_response


    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'send_email':
            email_list = request.POST['emails']
            email_address = re.split(r'[,"]', email_list)
            email_address = [email.strip('[] ') for email in email_address if email]

            from_email = getattr(settings, "EMAIL_HOST_USER", None)
            if not from_email:
                messages.error(request, "E-mail host não configurado.")
                return redirect("login")  # Redirecione para uma página adequada

            if email_address:
                for email in email_address:
                    invite = (Invitation.objects.filter(email__iexact=email).order_by('created').last())

                    if invite is None:
                        invite = Invitation.create(email=email)

                    data_email = {"email": email}
                    token_response = make_request_in_api(
                        request=request,
                        endpoint="token-temporary/",
                        request_method="POST",
                        payload=data_email,
                    )
                    # Garantindo que caso de algum erro o usuario seja redirecionado
                    if isinstance(token_response, HttpResponseRedirect):
                        return token_response

                    if not token_response or "temporary_token" not in token_response:
                        messages.error(request, f"Erro ao gerar token para {email}.")
                        continue

                    temporary_token = token_response["temporary_token"]
                    base_url = f"{request.scheme}://{request.get_host()}/invitations/accept/criar-usuario/{invite.key}/"
                    send_invitation_email(email, base_url, temporary_token, from_email)
                
            messages.success(request, "E-mails enviados com sucesso.")
                        
    return render (request, 'dashboard/index.html', 
                    {
                        'member': member_response
                    })
