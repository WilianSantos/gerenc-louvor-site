from django import forms


class LoginForms(forms.Form):
    username=forms.CharField(
        label='Usuário',
        required=True, 
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'username',
                'name': 'username',
                'placeholder': 'Usuário',
            }
        )
    )
    password=forms.CharField(
        label='Senha',
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password',
                'name': 'password',
                'placeholder': 'Senha',
            }
        )
    )