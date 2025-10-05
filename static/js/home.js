document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado - JavaScript funcionando');
    
    const menuIcon = document.querySelector('.menu-icon');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const closeBtn = document.getElementById('closeSidebar');

    // Función para abrir menú
    menuIcon.addEventListener('click', function() {
        console.log('Abriendo menú');
        sidebar.classList.add('active');
        overlay.classList.add('active');
    });

    // Función para cerrar menú
    function closeMenu() {
        console.log('Cerrando menú');
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }

    closeBtn.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);

    // Manejar enlaces del menú - SOLUCIÓN SIMPLE
    document.querySelectorAll('.sidebar-menu a').forEach(function(link) {
        link.addEventListener('click', function(e) {
            console.log('Clic en enlace:', this.getAttribute('href'));
            // Solo cerrar el menú, la navegación ocurre naturalmente
            closeMenu();
        });
    });

    // Cerrar menú con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
});