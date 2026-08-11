/**
 * landing-premium.js — Green Naroda • Clean Naroda Campaign
 * Premium homepage interactions — production grade
 */

(function () {
  'use strict';

  // ── Wait for DOM ──────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    initHeroSwiper();
    initScrollReveal();
    initCounterAnimation();
    initGalleryFilter();
    initGalleryLightbox();
    initFAQAccordion();
    initFAQSearch();
    initStickyHeader();
    initContactForm();
    initActiveNavSection();
  });

  // ── Hero Swiper ───────────────────────────────────────────
  function initHeroSwiper() {
    if (!document.querySelector('.hero-swiper')) return;
    const heroSwiper = new Swiper('.hero-swiper', {
      loop: true,
      speed: 900,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
        pauseOnMouseEnter: true,
      },
      pagination: {
        el: '.hero-swiper .swiper-pagination',
        clickable: true,
      },

    });
    return heroSwiper;
  }

  // ── Scroll Reveal ─────────────────────────────────────────
  function initScrollReveal() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    els.forEach(function (el) { observer.observe(el); });
  }

  // ── Counter Animation ─────────────────────────────────────
  function initCounterAnimation() {
    const counters = document.querySelectorAll('.counter-num');
    if (!counters.length) return;

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.target || el.textContent.replace(/[^0-9]/g, ''));
          const suffix = el.dataset.suffix || '';
          const prefix = el.dataset.prefix || '';
          const duration = 2000;
          const start = performance.now();

          function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(eased * target);
            el.textContent = prefix + current.toLocaleString() + suffix;
            if (progress < 1) requestAnimationFrame(update);
          }

          requestAnimationFrame(update);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(function (el) { observer.observe(el); });
  }

  // ── Gallery Filter ────────────────────────────────────────
  function initGalleryFilter() {
    const pills = document.querySelectorAll('.gallery-pill');
    const items = document.querySelectorAll('.gallery-grid-item[data-category]');
    if (!pills.length) return;

    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        pills.forEach(function (p) { p.classList.remove('active'); });
        pill.classList.add('active');

        const cat = pill.dataset.filter;
        items.forEach(function (item) {
          if (cat === 'all' || item.dataset.category === cat) {
            item.style.display = '';
            setTimeout(function () { item.style.opacity = '1'; }, 10);
          } else {
            item.style.opacity = '0';
            setTimeout(function () { item.style.display = 'none'; }, 300);
          }
        });
      });
    });
  }

  // ── Gallery Lightbox ──────────────────────────────────────
  function initGalleryLightbox() {
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lightbox-img');
    if (!lb || !lbImg) return;

    document.querySelectorAll('.gallery-grid-item').forEach(function (item) {
      item.addEventListener('click', function () {
        const img = item.querySelector('img');
        if (!img) return;
        lbImg.src = img.src;
        lb.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    });

    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target.id === 'lightbox-close') {
        lb.classList.remove('active');
        document.body.style.overflow = '';
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        lb.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // ── FAQ Accordion ─────────────────────────────────────────
  function initFAQAccordion() {
    const questions = document.querySelectorAll('.faq-question');
    if (!questions.length) return;

    questions.forEach(function (q) {
      q.addEventListener('click', function () {
        const isActive = q.classList.contains('active');
        // Close all
        questions.forEach(function (other) {
          other.classList.remove('active');
          const ans = other.nextElementSibling;
          if (ans && ans.classList.contains('faq-answer')) {
            ans.classList.remove('open');
          }
        });
        // Open clicked (if was not active)
        if (!isActive) {
          q.classList.add('active');
          const ans = q.nextElementSibling;
          if (ans && ans.classList.contains('faq-answer')) {
            ans.classList.add('open');
          }
        }
      });
    });
  }

  // ── FAQ Search ────────────────────────────────────────────
  function initFAQSearch() {
    const searchInput = document.getElementById('faq-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
      const query = searchInput.value.toLowerCase().trim();
      const items = document.querySelectorAll('.faq-item');
      items.forEach(function (item) {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }

  // ── Sticky Header ─────────────────────────────────────────
  function initStickyHeader() {
    const header = document.querySelector('.main-navbar');
    if (!header) return;
    // Already handled by CSS, but we can add scroll class for opacity transitions
    window.addEventListener('scroll', function () {
      if (window.scrollY > 80) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  // ── Contact Form ──────────────────────────────────────────
  function initContactForm() {
    const form = document.getElementById('homepage-contact-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = form.querySelector('[type="submit"]');
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Sending...';

      const data = new FormData(form);
      fetch('/contact/', {
        method: 'POST',
        body: data,
        headers: { 'X-CSRFToken': getCsrf() }
      })
        .then(function (r) {
          btn.disabled = false;
          btn.innerHTML = '<i class="fa-solid fa-check mr-2"></i> Message Sent!';
          form.reset();
          setTimeout(function () { btn.innerHTML = originalText; }, 3000);
        })
        .catch(function () {
          btn.disabled = false;
          btn.innerHTML = originalText;
        });
    });
  }

  // ── Active Nav Section ────────────────────────────────────
  function initActiveNavSection() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link-active-aware');
    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach(function (link) {
            link.classList.remove('active-section');
            if (link.getAttribute('href') === '#' + id || link.dataset.section === id) {
              link.classList.add('active-section');
            }
          });
        }
      });
    }, { threshold: 0.4 });

    sections.forEach(function (s) { observer.observe(s); });
  }

  // ── Utility ───────────────────────────────────────────────
  function getCsrf() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

})();
