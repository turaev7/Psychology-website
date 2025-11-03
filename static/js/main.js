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
    
    const selectors = [
        '.nav-text', '.hero-text', '.btn-text', '.section-text', '.feature-text',
        '.cta-text', '.page-title', '.about-text', '.contact-text', '.appointment-text',
        '.form-text', '.alert-text', '.login-text', '.info-text', '.dashboard-text',
        '.notes-text', '.tab-text', '.table-text', '.badge-text', '.modal-text',
        '.media-text', '.footer-text'
    ];
    
    selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            if (!el.dataset.i18n) {
                el.dataset.i18n = el.textContent.trim();
            }
            
            const key = el.dataset.i18n;
            if (t[key]) {
                el.textContent = t[key];
            }
        });
    });
}
