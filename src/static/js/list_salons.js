// Vi Beauty - List Salons Page JavaScript

function confirmDelete(salonId, salonName) {
    const confirmed = confirm(
        `Tem certeza que deseja excluir o salão "${salonName}"?\n\n` +
        `Esta ação não pode ser desfeita!`
    );
    
    if (confirmed) {
        // Cria e submete o formulário de exclusão
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/delete_salon/${salonId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Adiciona animação suave aos cards
    const salonCards = document.querySelectorAll('.salon-card');
    salonCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        }, index * 50);
    });

    // Lazy loading para imagens
    const images = document.querySelectorAll('.salon-image img');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.src; // Força o carregamento
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Adiciona hover effect nos cards
    salonCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

