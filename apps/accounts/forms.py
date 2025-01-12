from django.contrib.auth.password_validation import validate_password
from django import forms

from .models import CustomUser


class LoginForms(forms.Form):
    username=forms.CharField(
        label='Usuário',
        required=True, 
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'username-id',
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
                'id': 'password-id',
                'placeholder': 'Senha',
            }
        )
    )


class ProfileForms(forms.Form):    
    # Campos do modelo Member da api
    name = forms.CharField(
        max_length=150, 
        required=True, 
        label="Nome", 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'name-id'
        })
    )
    availability = forms.BooleanField(
        required=False, 
        label="Disponibilidade", 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'availability-id'
            })
    )
    cell_phone = forms.CharField(
        max_length=15,
        min_length=15, 
        required=False, 
        label="Celular", 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'name': 'cellPhone',
            'id': 'cell_phone-id',
            'type': 'tel'
            })
    )
    profile_picture = forms.ImageField(
        required=False, 
        label="Foto de Perfil", 
        widget=forms.FileInput(attrs={
            "class": "form-control form-control",
            "id": "profile_picture-id"
        })
    )
    
    # Campos consumidos da API
    function = forms.MultipleChoiceField(
        label="Funções", 
        required=False, 
        widget=forms.SelectMultiple(attrs={
            'autocomplete': "off", 
            'id': 'function-id',
            'class': 'multiple-selector',
            'value': "awesome,neat"
        })
    )
    
    # Campos adicionais da model User da api
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nome de Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username-id'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Primeiro Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name-id'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Último Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name-id'})
    )
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email-id'
            })
    )

    # Validações
    def clean_cell_phone(self):
        cell_phone = self.cleaned_data.get('cell_phone')
        clean_cell_phone = "".join([digit for digit in cell_phone if digit.isdigit()])
        return clean_cell_phone
    
    def clean_function(self):
        function = self.cleaned_data.get('function')
        
        function_converted_int = [int(item) for item in function]
        return function_converted_int

    # Sobrescrevendo o init para popular os choices com dados da API
    def __init__(self, *args, **kwargs):
        functions_data = kwargs.pop('functions_data', [])
        form_data = kwargs.pop('form_data', {})
        super().__init__(*args, **kwargs)
        
        # Populando os choices com os dados da API
        self.fields['function'].choices = [(str(item['id']) , item['functions_name']) for item in functions_data]
        self.initial['function'] = form_data.get('function', [])

        # Campos de member
        self.fields['name'].initial = form_data.get('name', '')
        self.fields['cell_phone'].initial = form_data.get('cell_phone', '')
        self.fields['availability'].initial = form_data.get('availability', False)
        self.fields['profile_picture'].initial = form_data.get('profile_picture', '')
        # Campos do usuário 
        self.fields['username'].initial = form_data.get('username', '')
        self.fields['first_name'].initial = form_data.get('first_name', '')
        self.fields['last_name'].initial = form_data.get('last_name', '')
        self.fields['email'].initial = form_data.get('email', '')


class ChangePasswordForms(forms.Form):
    old_password = forms.CharField(
        label='Senha Antiga', 
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'old_password-id'
            }
        ),
    )
    new_password=forms.CharField(
        label='Senha', 
        required=True, 
        max_length=70,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'new_password-id'
            }
        ),
    )
    password_confirmation=forms.CharField(
        label='Confirme sua senha', 
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password_confirmation-id'
            }
        ),
    )

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        validate_password(new_password)
        return new_password
    
    def clean_password_confirmation(self):
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if new_password and password_confirmation:
            if new_password != password_confirmation:
                raise forms.ValidationError('As senhas não são iguais')
            else:
                return password_confirmation
            

class CreateUserForms(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nome de Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username-id'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Primeiro Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Último Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name-id'})
    )
    #campo para Member
    cell_phone = forms.CharField(
        max_length=15,
        min_length=15, 
        required=False, 
        label="Celular", 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'name': 'cellPhone',
            'id': 'cell_phone-id',
            'type': 'tel'
            })
    )
    
    password=forms.CharField(
        label='Senha', 
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password-id',
            }
        ),
    )
    password_confirmation=forms.CharField(
        label='Confirme sua senha', 
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password_confirmation-id',
            }
        ),
    )

    # Validações
    def clean_cell_phone(self):
        cell_phone = self.cleaned_data.get('cell_phone')
        clean_cell_phone = "".join([digit for digit in cell_phone if digit.isdigit()])
        return clean_cell_phone
    

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Usuário já existe')
        else:
            return username
            
            
    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password and password_confirmation:
            if password != password_confirmation:
                raise forms.ValidationError('Senhas não são iguais')
            else:
                return password_confirmation
        

class MemberFunctionForms(forms.Form):
    functions_name = forms.CharField(
        max_length=50,
        required=True,
        label="Nome da função",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'functions_name-id'})
    )

    def clean_functions_name(self):
        functions_name = self.cleaned_data.get('functions_name')

        if not all(char.isalpha() or char.isspace() for char in functions_name):
            raise forms.ValidationError("A função deve conter apenas letras.")
        
        return functions_name.title()
