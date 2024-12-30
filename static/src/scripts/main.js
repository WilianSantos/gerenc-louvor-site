$(document).ready(function () {
    
    // $('form').on('submit', function (e) {
    //     e.preventDefault(); // Evitar envio padrão do formulário
    // });

    new TomSelect('#function-id',{
        plugins: {
            'clear_button':{
                'title':'Remove all selected options',
            },
            'checkbox_options': {
                'checkedClassNames':   ['ts-checked'],
                'uncheckedClassNames': ['ts-unchecked'],
            }
        },
        persist: false,
        create: true,
        onDelete: function(values) {
            return confirm(values.length > 1 ? 'Are you sure you want to remove these ' + values.length + ' items?' : 'Are you sure you want to remove "' + values[0] + '"?');
        }
    })

    // const { changePassword } = require('./pages/profile.js')
    // changePassword()
    // $('#form-change-password').on('submit', function (e) {
    //     e.preventDefault();
    //     const tabPane = $('#profile-change-password');
    //     const otherTabs = $('.tab-pane'); // Seleciona todas as outras abas
    
    //     // Remove classes "show" e "active" de todas as abas
    //     otherTabs.removeClass('show active');
    
    //     // Adiciona as classes "show" e "active" à aba desejada
    //     tabPane.addClass('show active');

    //     const form = $(this);
    //     $.ajax({
    //         url: form.attr('action'),
    //         type: form.attr('method'),
    //         data: form.serialize(),
        
    //     });
    // })
});
