from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.signing import Signer
from django.contrib.auth.decorators import login_required

from apps.accounts.models import CustomUser
from apps.accounts.simple_jwt import make_request_in_api


@login_required
def dashboard(request):
    
    user = CustomUser.objects.get(id=request.user.id)

    member_id = user.member_id

    # Recuperando e verificando os dados
    signer = Signer()
    retrieved_data = signer.unsign_object(request.session['encrypted_tokens'])
    access_token = retrieved_data.get('access_token') 

    if access_token:

        member_response = make_request_in_api(
            endpoint='member/', 
            id=member_id, 
            request_method='GET', 
            access_token=access_token
        )
        
        member_name = member_response.get('name')

        return render (request, 'dashboard/index.html', {'member_name': member_name})

    return render (request, 'dashboard/index.html')
