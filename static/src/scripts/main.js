
$(document).ready(function () {
    
    // $('form').on('submit', function (e) {
    //     e.preventDefault(); // Evitar envio padrão do formulário
    // });

    // const { TomSelect } = require('./tom_select/tom_select.js')
    // TomSelect()

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
});
