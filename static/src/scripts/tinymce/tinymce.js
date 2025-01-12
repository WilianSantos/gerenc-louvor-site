tinymce.init({
    selector: 'textarea',
    plugins: 'anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount',
    toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table | align lineheight | numlist bullist indent outdent | emoticons charmap | removeformat',
    language: 'pt_BR',
})

document.addEventListener('DOMContentLoaded', function() {
    // Após carregar a página, preenche o conteúdo no TinyMCE
    tinymce.get('music_text-id').setContent('{{ music_forms.fields.music_text.initial|escapejs }}');
});
