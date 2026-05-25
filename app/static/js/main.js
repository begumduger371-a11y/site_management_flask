document.addEventListener('DOMContentLoaded', function () {
    // Mobile Navigation Menu Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
            
            // Toggle hamburger icon animation/character if desired
            const icon = navToggle.querySelector('i');
            if (icon) {
                if (navMenu.classList.contains('active')) {
                    icon.className = 'fas fa-times';
                } else {
                    icon.className = 'fas fa-bars';
                }
            }
        });
    }

    // Auto-dismiss Flash Messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.6s ease';
            setTimeout(function () {
                alert.remove();
            }, 600);
        }, 5000);
    });

    // Close Flash Messages on click
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const alert = this.parentElement;
            alert.remove();
        });
    });

    // AI Assistant Loading Spinner Trigger
    const assistantForm = document.getElementById('assistant-form');
    const responseBox = document.getElementById('ai-response-box');
    const loader = document.getElementById('ai-loader');

    if (assistantForm && loader) {
        assistantForm.addEventListener('submit', function () {
            // Hide previous response if any
            if (responseBox) {
                responseBox.style.display = 'none';
            }
            // Show loader
            loader.style.display = 'block';
            loader.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }
});
