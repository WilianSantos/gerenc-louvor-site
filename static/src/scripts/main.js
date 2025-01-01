$(document).ready(function () {

    // Seletor multiplo com o TomSelect
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

    // Enviar email 
    document.getElementById('add-email').addEventListener('click', function() {
        const emailInput = document.getElementById('email-input');
        const emailList = document.getElementById('email-list');
        const emailsField = document.getElementById('emails');
    
        if (emailInput.value) {
            // Adiciona o e-mail à lista visível
            const li = document.createElement('li');
            li.textContent = emailInput.value;
            emailList.appendChild(li);
    
            // Adiciona o e-mail ao campo oculto
            let emails = emailsField.value ? JSON.parse(emailsField.value) : [];
            emails.push(emailInput.value);
            emailsField.value = JSON.stringify(emails);
    
            // Limpa o campo de entrada
            emailInput.value = '';
        }
    });

});
