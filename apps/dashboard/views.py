from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.conf import settings

import re

from apps.accounts.models import CustomUser
from apps.simpleJWT.utils import make_request_in_api


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

            subject = "Teste"
            message = "Este é o corpo do e-mail."
            recipient_list = email_address
            print(email_address)
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                bcc=recipient_list,  # Destinatários ocultos
            )
            email.send(fail_silently=False)

            messages.success(request, "sucesso")

    return render (request, 'dashboard/index.html', 
                    {
                        'member': member_response
                        
                    })
