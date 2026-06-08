/* Main JavaScript — Excellence Global School */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initAOS();
    initCounters();
    initHeroSwiper();
    initSwiper();
    initGLightbox();
    initChatWidget();
    initSmoothScroll();
    initGSAPAnimations();

    if (document.body.classList.contains('inner-page')) {
        document.querySelector('.navbar')?.classList.add('scrolled');
    }
});

/* Navbar scroll effect + dropdown auto-close */
function initNavbar() {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    let lastScroll = 0;
    let scrollTimer = null;

    const closeAllDropdowns = () => {
        navbar.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            const toggle = menu.previousElementSibling || menu.parentElement?.querySelector('[data-bs-toggle="dropdown"]');
            if (toggle && typeof bootstrap !== 'undefined') {
                bootstrap.Dropdown.getOrCreateInstance(toggle).hide();
            } else {
                menu.classList.remove('show');
                menu.parentElement?.querySelector('.dropdown-toggle')?.classList.remove('show');
            }
        });
    };

    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        navbar.classList.toggle('scrolled', y > 50);

        // Auto-close dropdowns when scrolling
        if (Math.abs(y - lastScroll) > 8) {
            closeAllDropdowns();
        }

        // Hide navbar on scroll down, show on scroll up (desktop feel)
        if (y > 200) {
            navbar.classList.toggle('navbar-hidden', y > lastScroll && y > 300);
        } else {
            navbar.classList.remove('navbar-hidden');
        }
        lastScroll = y;

        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => navbar.classList.remove('navbar-hidden'), 800);
    }, { passive: true });

    // Desktop: hover to open dropdown, auto-close on leave
    if (window.matchMedia('(min-width: 992px)').matches) {
        navbar.querySelectorAll('.nav-item.dropdown').forEach(item => {
            const toggle = item.querySelector('[data-bs-toggle="dropdown"]');
            const menu = item.querySelector('.dropdown-menu');
            if (!toggle || !menu || typeof bootstrap === 'undefined') return;

            let closeDelay;
            const dd = bootstrap.Dropdown.getOrCreateInstance(toggle, { autoClose: true });

            item.addEventListener('mouseenter', () => {
                clearTimeout(closeDelay);
                closeAllDropdowns();
                dd.show();
            });

            item.addEventListener('mouseleave', () => {
                closeDelay = setTimeout(() => dd.hide(), 180);
            });
        });
    }

    // Animate brand on load
    if (typeof gsap !== 'undefined') {
        gsap.from('.navbar-brand', { opacity: 0, x: -30, duration: 0.8, ease: 'power3.out' });
        gsap.from('.navbar-nav > li', { opacity: 0, y: -15, duration: 0.5, stagger: 0.06, delay: 0.2, ease: 'power2.out' });
    }
}

/* AOS Init */
function initAOS() {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 80 });
    }
}

/* Counter Animation */
function initCounters() {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
}

function animateCounter(el) {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';
    const duration = 2000;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(target * eased).toLocaleString() + suffix;
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

/* Hero Banner Carousel */
function initHeroSwiper() {
    const el = document.querySelector('.hero-swiper');
    if (!el || typeof Swiper === 'undefined') return;

    new Swiper('.hero-swiper', {
        slidesPerView: 1,
        loop: true,
        speed: 900,
        effect: 'slide',
        autoplay: {
            delay: 4500,
            disableOnInteraction: false,
            pauseOnMouseEnter: true,
        },
        pagination: {
            el: '.hero-swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.hero-swiper-next',
            prevEl: '.hero-swiper-prev',
        },
        grabCursor: true,
        keyboard: { enabled: true },
    });
}

/* Swiper Testimonials */
function initSwiper() {
    const el = document.querySelector('.testimonials-swiper');
    if (!el || typeof Swiper === 'undefined') return;

    new Swiper('.testimonials-swiper', {
        slidesPerView: 1,
        spaceBetween: 24,
        loop: true,
        autoplay: { delay: 5000, disableOnInteraction: false },
        pagination: { el: '.swiper-pagination', clickable: true },
        breakpoints: {
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
        },
    });
}

/* GLightbox */
function initGLightbox() {
    if (typeof GLightbox !== 'undefined') {
        GLightbox({ selector: '.glightbox', touchNavigation: true, loop: true });
    }
}

/* GSAP Animations */
function initGSAPAnimations() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    gsap.registerPlugin(ScrollTrigger);

    gsap.from('.hero-badge', { opacity: 0, y: 30, duration: 0.8, delay: 0.3 });
    gsap.from('.hero-content h1', { opacity: 0, y: 40, duration: 1, delay: 0.5 });
    gsap.from('.hero-content p', { opacity: 0, y: 30, duration: 0.8, delay: 0.7 });
    gsap.from('.hero-buttons', { opacity: 0, y: 20, duration: 0.8, delay: 0.9 });

    gsap.utils.toArray('.feature-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: { trigger: card, start: 'top 85%' },
            opacity: 0, y: 40, duration: 0.6, delay: i * 0.1,
        });
    });
}

/* Smooth Scroll */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', (e) => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/* Chat Widget */
function initChatWidget() {
    const toggle = document.getElementById('chatToggle');
    const panel = document.getElementById('chatPanel');
    const close = document.getElementById('chatClose');
    const input = document.getElementById('chatInput');
    const send = document.getElementById('chatSend');
    const messages = document.getElementById('chatMessages');
    const typing = document.getElementById('chatTyping');

    if (!toggle || !panel) return;

    toggle.addEventListener('click', () => panel.classList.toggle('active'));
    close?.addEventListener('click', () => panel.classList.remove('active'));

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        appendMessage('user', text);
        input.value = '';
        send.disabled = true;
        typing.style.display = 'flex';

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
                || document.querySelector('input[name="csrf_token"]')?.value;

            const res = await fetch('/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                body: JSON.stringify({ message: text }),
            });

            const data = await res.json();
            typing.style.display = 'none';

            if (data.response) {
                appendMessage('bot', data.response);
            } else {
                appendMessage('bot', data.error || 'Sorry, I could not process your request.');
            }
        } catch (err) {
            typing.style.display = 'none';
            appendMessage('bot', 'Connection error. Please try again.');
        }

        send.disabled = false;
        input.focus();
    }

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `chat-message ${role}`;
        div.innerHTML = `<div class="message-bubble">${escapeHtml(text)}</div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    send?.addEventListener('click', sendMessage);
    input?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

/* AI Feature Helper */
async function callAI(endpoint, payload, responseEl, loadingEl) {
    if (loadingEl) loadingEl.style.display = 'flex';
    if (responseEl) responseEl.style.display = 'none';

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
            || document.querySelector('input[name="csrf_token"]')?.value;

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || '',
            },
            body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (loadingEl) loadingEl.style.display = 'none';

        if (data.response && responseEl) {
            responseEl.textContent = data.response;
            responseEl.style.display = 'block';
        } else if (responseEl) {
            responseEl.textContent = data.error || 'An error occurred.';
            responseEl.style.display = 'block';
        }
    } catch (err) {
        if (loadingEl) loadingEl.style.display = 'none';
        if (responseEl) {
            responseEl.textContent = 'Connection error. Please try again.';
            responseEl.style.display = 'block';
        }
    }
}

window.callAI = callAI;
