// $(document).ready(function () {
//     $('#loginForm').on('submit', function (e) {
//         e.preventDefault(); // Evitar envio padrão do formulário

//         // Fazer a requisição de envio do formulário via AJAX
//         $.ajax({
//             url: $(this).attr('action'),
//             type: $(this).attr('method'),
//             data: $(this).serialize(), // Serializar os dados do formulário
//             success: function (response) {
//                 // Após o login, acessar o cookie 'access_token'
//                 document.cookie.split('; ').forEach(cookie => {
//                     if (cookie.startsWith('access_token=')) {
//                         const accessToken = cookie.split('=')[1];
//                         console.log('Access Token:', accessToken);

//                         // Aqui você pode usar o token conforme necessário
//                     }
//                 });

//                 // Redirecionar ou fazer algo após o login
//                 window.location.href = '/dashboard/';
//             },
//             error: function (xhr, status, error) {
//                 console.error('Erro ao fazer login:', error);
//                 alert('Erro ao fazer login. Tente novamente.');
//             }
//         });
//     });
// });
