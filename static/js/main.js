document.addEventListener('DOMContentLoaded', function() {
    const currentLang = new URLSearchParams(window.location.search).get('lang') || 'en';
    
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    const savedTheme = localStorage.getItem('theme') || 'light';
    body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
    
    translatePage(currentLang);
    
    document.querySelectorAll('.lang-option').forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const newLang = this.getAttribute('data-lang');
            const url = new URL(window.location);
            url.searchParams.set('lang', newLang);
            window.location.href = url.toString();
        });
    });
});

function translatePage(lang) {
    const t = translations[lang] || translations['en'];
    
    document.querySelectorAll('.nav-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.hero-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.btn-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.section-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.feature-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.cta-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.page-title').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.about-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.contact-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.appointment-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.form-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.alert-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.login-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.info-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.dashboard-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.notes-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.tab-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.table-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.badge-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.modal-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.media-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
    
    document.querySelectorAll('.footer-text').forEach(el => {
        const key = el.textContent.trim();
        if (t[key]) el.textContent = t[key];
    });
}
