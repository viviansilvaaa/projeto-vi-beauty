// Vi Beauty - Register Hairdresser Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto foco no campo nome
    const nameField = document.getElementById('name');
    if (nameField) {
        nameField.focus();
    }

    // Contador de caracteres para especialidades
    const specialtiesField = document.getElementById('specialties');
    if (specialtiesField) {
        specialtiesField.addEventListener('input', function() {
            const remaining = 500 - this.value.length;
            const noteElement = this.nextElementSibling;
            if (noteElement?.classList.contains('field-note')) {
                noteElement.textContent = `${remaining} caracteres restantes (máximo 500)`;
                if (remaining < 50) {
                    noteElement.style.color = '#e74c3c';
                } else {
                    noteElement.style.color = '';
                }
            }
        });
    }

    // Máscara para telefone
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
            if (value.length >= 10) {
                value = value.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3');
            }
            this.value = value;
        });
    }

    // Validação da URL da imagem (opcional)
    const imageUrlInput = document.getElementById('image_url');
    if (imageUrlInput) {
        imageUrlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url) {
                try {
                    const urlObj = new URL(url);
                    if (!urlObj.protocol.startsWith('http')) {
                        alert('A URL da imagem deve começar com http:// ou https://');
                        this.focus();
                    }
                } catch (error) {
                    // URL inválida
                    alert('Por favor, informe uma URL válida para a imagem.');
                    this.focus();
                }
            }
        });
    }

    // Validação do formulário ao submeter
    const registerHairdresserForm = document.getElementById('registerHairdresserForm');
    if (registerHairdresserForm) {
        registerHairdresserForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const salonId = document.getElementById('salon_id').value;
            const phone = document.getElementById('phone').value.trim();
            const email = document.getElementById('email').value.trim();
            const imageUrl = document.getElementById('image_url').value.trim();
            const specialties = document.getElementById('specialties').value.trim();

            // Validação de campos obrigatórios
            if (!name) {
                e.preventDefault();
                alert('O nome do cabeleireiro é obrigatório!');
                document.getElementById('name').focus();
                return;
            }

            // Validação do salão
            if (!salonId) {
                e.preventDefault();
                alert('É obrigatório selecionar um salão!');
                document.getElementById('salon_id').focus();
                return;
            }

            // Validação do telefone
            const phoneDigits = phone.replace(/\D/g, '');
            if (!phone || phoneDigits.length < 10) {
                e.preventDefault();
                alert('Por favor, informe um telefone válido no formato (XX) XXXXX-XXXX');
                document.getElementById('phone').focus();
                return;
            }

            // Validação do email (obrigatório)
            if (!email) {
                e.preventDefault();
                alert('O e-mail é obrigatório!');
                document.getElementById('email').focus();
                return;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Por favor, informe um e-mail válido!');
                document.getElementById('email').focus();
                return;
            }

            // Validação da URL da imagem (se preenchida)
            if (imageUrl) {
                try {
                    const urlObj = new URL(imageUrl);
                    if (!urlObj.protocol.startsWith('http')) {
                        e.preventDefault();
                        alert('A URL da imagem deve começar com http:// ou https://');
                        document.getElementById('image_url').focus();
                        return;
                    }
                } catch (error) {
                    e.preventDefault();
                    alert('Por favor, informe uma URL válida para a imagem.');
                    document.getElementById('image_url').focus();
                    return;
                }
            }

            // Validação do tamanho das especialidades
            if (specialties && specialties.length > 500) {
                e.preventDefault();
                alert('As especialidades devem ter no máximo 500 caracteres!');
                document.getElementById('specialties').focus();
                return;
            }

            // Se chegou aqui, tudo está válido
            return true;
        });
    }
});

