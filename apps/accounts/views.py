from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login

from .models import CustomUser
from .forms import LoginForms
from .utils import getting_access_token


def login_with_jwt(request):
    login_form = LoginForms()

    if request.method == 'POST':
        login_form = LoginForms(request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            access_response = getting_access_token(request=request, username=username, password=password)

            if 'message_error' not in access_response:

                member_id = access_response['member_id']

                # Buscar ou criar usuário localmente
                user_id = access_response['user_id']
                user, _ = CustomUser.objects.get_or_create(
                    id=user_id, 
                    defaults={"username": username, "member_id": member_id}
                )
                login(request, user)
                
                return redirect('dashboard')

            message_error = access_response['message_error']
            messages.error(request, message_error)

        else:
            messages.error(request, "Dados inválidos no formulário.")

    return render(request, 'accounts/login.html', {'login_form': login_form})
