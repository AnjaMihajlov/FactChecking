document.addEventListener('DOMContentLoaded', function() {
    // Dobijamo trenutnu putanju
    const currentPath = window.location.pathname;
    
    // Uklanjamo active klasu sa svih linkova
    document.querySelectorAll('.mobile-nav-item').forEach(link => {
        link.classList.remove('active');
    });
    
    // Dodajemo active klasu odgovarajućem linku
    document.querySelectorAll('.mobile-nav-item').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}); 