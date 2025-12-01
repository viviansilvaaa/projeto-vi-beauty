// Vi Beauty - Edit Hairdresser Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto foco no campo nome
    const nameField = document.getElementById('name');
    if (nameField) {
        nameField.focus();
    }

    // Mascara para telefone
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

    // Validacao da URL da imagem (opcional)
    const imageUrlInput = document.getElementById('image_url');
    if (imageUrlInput) {
        imageUrlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url) {
                try {
                    const urlObj = new URL(url);
                    if (!urlObj.protocol.startsWith('http')) {
                        alert('A URL da imagem deve comecar com http:// ou https://');
                        this.focus();
                    }
                } catch (error) {
                    // URL invalida
                    alert('Por favor, informe uma URL valida para a imagem.');
                    this.focus();
                }
            }
        });
    }

    // Validacao do formulario ao submeter
    const editHairdresserForm = document.getElementById('editHairdresserForm');
    if (editHairdresserForm) {
        editHairdresserForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const salonId = document.getElementById('salon_id').value;
            const phone = document.getElementById('phone').value.trim();
            const email = document.getElementById('email').value.trim();
            const imageUrl = document.getElementById('image_url').value.trim();

            // Validacao de campos obrigatorios
            if (!name) {
                e.preventDefault();
                alert('O nome do cabeleireiro e obrigatorio!');
                document.getElementById('name').focus();
                return;
            }

            // Validacao do salao
            if (!salonId) {
                e.preventDefault();
                alert('E obrigatorio selecionar um salao!');
                document.getElementById('salon_id').focus();
                return;
            }

            // Validacao do telefone
            const phoneDigits = phone.replace(/\D/g, '');
            if (!phone || phoneDigits.length < 10) {
                e.preventDefault();
                alert('Por favor, informe um telefone valido no formato (XX) XXXXX-XXXX');
                document.getElementById('phone').focus();
                return;
            }

            // Validacao do email (obrigatorio)
            if (!email) {
                e.preventDefault();
                alert('O e-mail e obrigatorio!');
                document.getElementById('email').focus();
                return;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Por favor, informe um e-mail valido!');
                document.getElementById('email').focus();
                return;
            }

            // Validacao da URL da imagem (se preenchida)
            if (imageUrl) {
                try {
                    const urlObj = new URL(imageUrl);
                    if (!urlObj.protocol.startsWith('http')) {
                        e.preventDefault();
                        alert('A URL da imagem deve comecar com http:// ou https://');
                        document.getElementById('image_url').focus();
                        return;
                    }
                } catch (error) {
                    e.preventDefault();
                    alert('Por favor, informe uma URL valida para a imagem.');
                    document.getElementById('image_url').focus();
                    return;
                }
            }

            // Se chegou aqui, tudo esta valido
            return true;
        });
    }
});
