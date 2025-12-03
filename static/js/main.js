document.addEventListener('DOMContentLoaded', function () {
    // Detect current language: URL ?lang=, then <html lang>, then 'en'
    const urlParams = new URLSearchParams(window.location.search);
    const currentLang = urlParams.get('lang') || document.documentElement.lang || 'en';

    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // Theme: load saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Theme toggle handler
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = body.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggle) return; // in case button is missing on some pages
        const icon = themeToggle.querySelector('i');
        if (!icon) return;

        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // Apply translations
    translatePage(currentLang);

    // Language selector click handler (keep URL params, just update lang)
    document.querySelectorAll('.lang-option').forEach(option => {
        option.addEventListener('click', function (e) {
            e.preventDefault();
            const newLang = this.getAttribute('data-lang');
            const url = new URL(window.location);
            url.searchParams.set('lang', newLang);
            window.location.href = url.toString();
        });
    });

    // ---------- MEDIA FILTER & SEARCH ----------
    const mediaFilterButtons = document.querySelectorAll('[data-media-filter]');
    const mediaSearchInput = document.getElementById('mediaSearch');
    const mediaItems = document.querySelectorAll('.media-item');
    const mediaEmpty = document.getElementById('mediaEmpty');

    if (mediaItems.length > 0) {
        let activeFilter = 'all';
        let searchTerm = '';

        function applyMediaFilters() {
            let visibleCount = 0;
            const term = searchTerm.trim().toLowerCase();

            mediaItems.forEach(item => {
                const type = (item.dataset.type || '').toLowerCase();
                const title = (item.dataset.title || '').toLowerCase();
                const desc = (item.dataset.description || '').toLowerCase();

                const matchesFilter = activeFilter === 'all' || type === activeFilter;
                const matchesSearch =
                    term === '' ||
                    title.includes(term) ||
                    desc.includes(term);

                if (matchesFilter && matchesSearch) {
                    item.classList.remove('d-none');
                    visibleCount++;
                } else {
                    item.classList.add('d-none');
                }
            });

            if (mediaEmpty) {
                if (visibleCount === 0) {
                    mediaEmpty.classList.remove('d-none');
                } else {
                    mediaEmpty.classList.add('d-none');
                }
            }
        }

        // Filter buttons
        mediaFilterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                mediaFilterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeFilter = btn.getAttribute('data-media-filter') || 'all';
                applyMediaFilters();
            });
        });

        // Search input
        if (mediaSearchInput) {
            mediaSearchInput.addEventListener('input', () => {
                searchTerm = mediaSearchInput.value;
                applyMediaFilters();
            });
        }

        // Initial apply
        applyMediaFilters();
    }
});

function translatePage(lang) {
    if (typeof translations === 'undefined') return;

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
            // Store original key in data-i18n on first run
            if (!el.dataset.i18n) {
                el.dataset.i18n = el.textContent.trim();
            }

            const key = el.dataset.i18n;
            let translated = null;

            // Special case: table headers use translations.table.*
            if (el.classList.contains('table-text') && t.table && t.table[key]) {
                translated = t.table[key];
            } else if (t[key]) {
                translated = t[key];
            }

            if (translated !== null && translated !== undefined) {
                el.textContent = translated;
            }
        });
    });

    // Search placeholder for media page
    const mediaSearchInput = document.getElementById('mediaSearch');
    if (mediaSearchInput && t.media_search_placeholder) {
        mediaSearchInput.placeholder = t.media_search_placeholder;
    }
}
// static/js/main.js
document.addEventListener("DOMContentLoaded", function () {
  const revealEls = document.querySelectorAll(".reveal-on-scroll");

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            obs.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
      }
    );

    revealEls.forEach((el) => observer.observe(el));
  } else {
    // Fallback for very old browsers: just show everything
    revealEls.forEach((el) => el.classList.add("is-visible"));
  }
});

