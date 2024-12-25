from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required

import requests


@login_required
def dashboard(request):
    
    # user_id = request.user.id
    # url = f'{settings.URL_API}member/{user_id}/'
    # member_response = requests.get(url=url)
    # member_data = member_response.json()
    # member_name = member_data.get('name'){"member_name": member_name}

    return render (request, 'dashboard/index.html')
