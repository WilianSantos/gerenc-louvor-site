function changePassword() {
    $('#form-change-password').on('submit', function (e) {
        const tabPane = $('#profile-change-password')

        tabPane.addClass('show active')
    })
}

module.exports = {changePassword}