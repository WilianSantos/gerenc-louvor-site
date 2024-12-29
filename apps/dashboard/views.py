from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
    

    return render (request, 'dashboard/index.html', {'member': member_response})
