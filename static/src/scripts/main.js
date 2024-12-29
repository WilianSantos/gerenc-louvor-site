
$(document).ready(function () {
    
    // $('form').on('submit', function (e) {
    //     e.preventDefault(); // Evitar envio padrão do formulário
    // });

    // const { TomSelect } = require('./tom_select/tom_select.js')
    // TomSelect()

    new TomSelect('#function-id',{
        plugins: ['caret_position','input_autogrow'],
        plugins: {
            'clear_button':{
                'title':'Remove all selected options',
            }
        },
        plugins: ['restore_on_backspace'],
        onChange: function(option){
            return option[self.settings.labelField];
        },
        persist: false,
        create: true
    })
});
