from django import forms


class MusicForms(forms.Form):
    music_title = forms.CharField(
        max_length=100, 
        required=True, 
        label="Título da Música", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'music_title-id'})
    )
    author = forms.CharField(
        max_length=100, 
        required=True, 
        label="Autor", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'author-id'})
    )
    category = forms.MultipleChoiceField(
        label="Categorias", 
        required=True, 
        widget=forms.SelectMultiple(attrs={
            'autocomplete': "off", 
            'id': 'category-id',
            'class': 'multiple-selector',
            'value': "awesome,neat"
        })
    )
    music_tone = forms.CharField(
        max_length=10, 
        required=True, 
        label="Tom da Música", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'music_tone-id'})
    )
    music_text = forms.CharField(
        required=True, 
        label="Texto da Música", 
        widget=forms.Textarea(attrs={'id': 'music_text-id'})
    )
    music_link = forms.URLField(
        max_length=255, 
        required=False, 
        label="Link youtube da Música", 
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Cole o link da música (opcional)',
            'id': 'music_link-id'
            })
    )

    def clean_category(self):
        category = self.cleaned_data.get('category')
        category_converted_int = [int(item) for item in category]
        return category_converted_int

    # Sobrescrevendo o init para popular os choices com dados da API
    def __init__(self, *args, **kwargs):
        categorys_data = kwargs.pop('categorys_data', [])
        super().__init__(*args, **kwargs)
        
        # Populando os choices com os dados da API
        self.fields['category'].choices = [(str(item['id']) , item['category_name']) for item in categorys_data]
        

class FileUploadForm(forms.Form):
    file = forms.FileField(
        label="Carregar PDF (Opcional)",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            'id': 'file-id'
            }),
    )

    def clean_file(self):
        file = self.cleaned_data.get("file")

        # Validação do tamanho do arquivo (máximo: 5MB)
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError("O arquivo não pode exceder 5MB.")

        # Validação do tipo de arquivo
        valid_extensions = [".pdf"]
        if not any(file.name.endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError("Tipo de arquivo não permitido. Carregue apenas PDF")

        return file
