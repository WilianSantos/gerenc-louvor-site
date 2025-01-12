document.addEventListener('DOMContentLoaded', function() {
     // Função que captura o e-mail digitado e adiciona em um input emails
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