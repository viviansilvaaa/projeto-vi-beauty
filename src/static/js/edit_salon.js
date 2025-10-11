// Vi Beauty - Edit Salon Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto foco no campo nome
    const nameField = document.getElementById('name');
    if (nameField) {
        nameField.focus();
    }

    // Contador de caracteres para descrição
    const descriptionField = document.getElementById('description');
    if (descriptionField) {
        // Atualiza contador no carregamento
        updateCharacterCount();
        
        descriptionField.addEventListener('input', updateCharacterCount);
    }

    function updateCharacterCount() {
        const remaining = 255 - descriptionField.value.length;
        const noteElement = descriptionField.nextElementSibling;
        if (noteElement?.classList.contains('field-note')) {
            noteElement.textContent = `${remaining} caracteres restantes (máximo 255)`;
            if (remaining < 50) {
                noteElement.style.color = '#e74c3c';
            } else {
                noteElement.style.color = '';
            }
        }
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

    // Preview da imagem em tempo real
    const imageUrlInput = document.getElementById('image_url');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageUrlInput && imagePreview) {
        imageUrlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url) {
                // Atualiza o preview
                imagePreview.src = url;
                
                // Valida a URL
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

        // Atualiza preview enquanto digita (com debounce)
        let debounceTimer;
        imageUrlInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const url = this.value.trim();
                if (url && url.startsWith('http')) {
                    imagePreview.src = url;
                }
            }, 500);
        });
    }

    // Validação do formulário ao submeter
    const editSalonForm = document.getElementById('editSalonForm');
    if (editSalonForm) {
        editSalonForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const address = document.getElementById('address').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const imageUrl = document.getElementById('image_url').value.trim();
            const description = document.getElementById('description').value.trim();

            // Validação de campos obrigatórios
            if (!name) {
                e.preventDefault();
                alert('O nome do salão é obrigatório!');
                document.getElementById('name').focus();
                return;
            }

            if (!address) {
                e.preventDefault();
                alert('O endereço é obrigatório!');
                document.getElementById('address').focus();
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

            // Validação da URL
            if (!imageUrl) {
                e.preventDefault();
                alert('A URL da imagem é obrigatória!');
                document.getElementById('image_url').focus();
                return;
            }

            try {
                const urlObj = new URL(imageUrl);
                if (!urlObj.protocol.startsWith('http')) {
                    e.preventDefault();
                    alert('A URL da imagem deve começar com http:// ou https://');
                    document.getElementById('image_url').focus();
                    return;
                }
            } catch (error) {
                // URL inválida
                e.preventDefault();
                alert('Por favor, informe uma URL válida para a imagem.');
                document.getElementById('image_url').focus();
                return;
            }

            // Validação do tamanho da descrição
            if (description && description.length > 255) {
                e.preventDefault();
                alert('A descrição deve ter no máximo 255 caracteres!');
                document.getElementById('description').focus();
                return;
            }

            // Confirmação antes de salvar
            const confirmed = confirm('Deseja salvar as alterações realizadas?');
            if (!confirmed) {
                e.preventDefault();
                return;
            }

            // Se chegou aqui, tudo está válido
            return true;
        });
    }
});

