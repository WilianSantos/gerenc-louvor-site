from django.contrib.auth.password_validation import validate_password
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


class ProfileForms(forms.Form):    
    # Campos do modelo Member da api
    name = forms.CharField(
        max_length=150, 
        required=True, 
        label="Nome", 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': "name",
            'id': 'name-id'
        })
    )
    availability = forms.BooleanField(
        required=False, 
        label="Disponibilidade", 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'name': 'availability',
            'id': 'availability-id'
            })
    )
    cell_phone = forms.CharField(
        max_length=15, 
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
            "id": "profile_picture-id",
            'name': 'profilePicture'
        })
    )
    
    # Campos consumidos da API
    function = forms.MultipleChoiceField(
        label="Funções", 
        required=False, 
        widget=forms.SelectMultiple(attrs={
            'autocomplete': "off", 
            'id': 'function-id',
            'value': "awesome,neat",
            'name': 'function'
        })
    )
    
    # Campos adicionais da model User da api
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nome de Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Primeiro Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'firstName'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Último Nome",
        widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'lastName'})
    )
    email = forms.EmailField(
        required=False,
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'name': 'email',
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
        self.fields['function'].choices = [(int(item['id']) , item['functions_name']) for item in functions_data]
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
            }
        ),
    )
    password_1=forms.CharField(
        label='Senha', 
        required=True, 
        max_length=70,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
    )
    password_2=forms.CharField(
        label='Confirme sua senha', 
        required=True, 
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    def clean_password_1(self):
        password_1 = self.cleaned_data.get('password_1')
        validate_password(password_1)
        return password_1