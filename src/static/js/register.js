// Vi Beauty - Register Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto foco no campo nome
    const nameField = document.getElementById('name');
    if (nameField) {
        nameField.focus();
    }

    // Máscara para CPF
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
        });
    }

    // Máscara para telefone
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 10) {
                value = value.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3');
            }
            this.value = value;
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const cpf = document.getElementById('cpf').value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('As senhas não coincidem!');
                return;
            }
            if (cpf.length !== 11) {
                e.preventDefault();
                alert('CPF deve ter 11 dígitos!');
                return;
            }
            const requiredFields = ['name', 'email', 'cpf', 'password', 'gender', 'phone'];
            for (let field of requiredFields) {
                if (!document.getElementById(field).value.trim()) {
                    e.preventDefault();
                    alert('Por favor, preencha todos os campos.');
                    return;
                }
            }
        });
    }
});
