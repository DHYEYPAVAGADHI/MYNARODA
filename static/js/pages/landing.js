/**
 * landing.js — Landing Page Entry Point
 * =======================================
 * Coordinates all landing page JavaScript modules:
 *   1. Three.js Hero Forest Scene
 *   2. GSAP Scroll Animations
 *   3. Counter Animations
 *   4. Navigation scroll behavior
 *   5. FAQ Accordion
 *   6. Swiper carousels
 *   7. Navbar mobile menu
 *   8. Toast notifications
 *
 * Architecture:
 *   Each concern is isolated in its own function.
 *   All functions are called from the single DOMContentLoaded handler.
 *   No global state is mutated except through clearly named module variables.
 */

"use strict";

// ─── Utility: Check if element exists before operating ────────────────────────

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// ─── Entry Point ──────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initHeroSlider();
  initLenisScroll();
  initGSAPAnimations();
  initCounterAnimations();
  initProgressBar();
  initFAQAccordion();
  initSwiperCarousels();
  initMobileMenu();
  initToastSystem();
  initRevealOnScroll();
});


// ─── 1. Navbar — Scroll-triggered glass effect ────────────────────────────────

function initNavbar() {
  const navbar = $("#navbar");
  if (!navbar) return;

  const onScroll = () => {
    if (window.scrollY > 60) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll(); // Run once on load in case page is already scrolled
}


function initHeroSlider() {
  const slides = document.querySelectorAll(".hero-slide");
  if (slides.length === 0) return;

  let current = 0;

  function nextSlide() {
    slides[current].classList.remove("is-active");
    current = (current + 1) % slides.length;
    slides[current].classList.add("is-active");
  }

  // Change slide every 7 seconds
  setInterval(nextSlide, 7000);
}


// ─── 3. Lenis Smooth Scroll ────────────────────────────────────────────────────

function initLenisScroll() {
  if (typeof Lenis === "undefined") return;

  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    direction: "vertical",
    gestureDirection: "vertical",
    smooth: true,
    smoothTouch: false, // Disable on touch for accessibility
    touchMultiplier: 2,
  });

  // Connect Lenis to GSAP ScrollTrigger
  if (typeof ScrollTrigger !== "undefined") {
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => {
      lenis.raf(time * 1000);
    });
    gsap.ticker.lagSmoothing(0);
  } else {
    // Fallback if GSAP is not loaded
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  // Smooth scroll for all anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = anchor.getAttribute("href").slice(1);
      const target = document.getElementById(targetId);
      if (target) {
        lenis.scrollTo(target, { offset: -80, duration: 1.4 });
      }
    });
  });
}


// ─── 4. GSAP Scroll Animations ────────────────────────────────────────────────

function initGSAPAnimations() {
  return;
  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") return;

  gsap.registerPlugin(ScrollTrigger);

  // Hero content staggered entrance
  const heroItems = document.querySelectorAll("[data-gsap='fade-up']");
  heroItems.forEach((item) => {
    const delay = parseFloat(item.dataset.delay || 0) * 0.15;
    gsap.fromTo(
      item,
      { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: 1, delay, ease: "power3.out" }
    );
  });

  // Story step stagger reveal
  gsap.from(".story-step", {
    scrollTrigger: {
      trigger: "#story",
      start: "top 70%",
    },
    opacity: 0,
    y: 60,
    stagger: 0.2,
    duration: 0.9,
    ease: "power2.out",
  });

  // Stat cards stagger
  gsap.from(".stat-card", {
    scrollTrigger: {
      trigger: "#statistics",
      start: "top 75%",
    },
    opacity: 0,
    y: 40,
    scale: 0.95,
    stagger: 0.12,
    duration: 0.7,
    ease: "back.out(1.2)",
  });
}


// ─── 5. Counter Animations ────────────────────────────────────────────────────

function initCounterAnimations() {
  /**
   * Animates a number from 0 to its target value when it enters the viewport.
   * Uses IntersectionObserver for performance (no GSAP dependency).
   *
   * @param {HTMLElement} el - Element with data-counter attribute
   */
  function animateCounter(el) {
    const target = parseInt(el.dataset.counter, 10);
    if (isNaN(target) || target === 0) {
      el.textContent = "0";
      return;
    }

    const duration = 2000; // ms
    const startTime = performance.now();
    const easeOut = (t) => 1 - Math.pow(1 - t, 3);

    function updateCounter(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOut(progress);
      const current = Math.floor(easedProgress * target);

      // Format with commas for readability
      el.textContent = current.toLocaleString("en-IN");

      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        el.textContent = target.toLocaleString("en-IN");
      }
    }

    requestAnimationFrame(updateCounter);
  }

  const counterElements = $$("[data-counter]");
  if (counterElements.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target); // Animate only once
        }
      });
    },
    { threshold: 0.3 }
  );

  counterElements.forEach((el) => observer.observe(el));
}


// ─── 6. Progress Bar Animation ────────────────────────────────────────────────

function initProgressBar() {
  const progressFill = $("#mission-progress");
  if (!progressFill) return;

  const treesPlanted = parseInt(progressFill.dataset.targetWidth || 0, 10);
  const goal = 28855;
  const percentage = Math.min((treesPlanted / goal) * 100, 100);

  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        progressFill.style.width = `${percentage}%`;
        observer.unobserve(progressFill);
      }
    },
    { threshold: 0.5 }
  );

  observer.observe(progressFill);
}


// ─── 7. FAQ Accordion ─────────────────────────────────────────────────────────

function initFAQAccordion() {
  const faqItems = $$(".faq-item");
  if (faqItems.length === 0) return;

  faqItems.forEach((item) => {
    const btn = item.querySelector(".faq-question");
    const answer = item.querySelector(".faq-answer");
    if (!btn || !answer) return;

    btn.addEventListener("click", () => {
      const isOpen = item.classList.contains("open");

      // Close all other open items
      faqItems.forEach((otherItem) => {
        if (otherItem !== item && otherItem.classList.contains("open")) {
          otherItem.classList.remove("open");
          const otherBtn = otherItem.querySelector(".faq-question");
          if (otherBtn) otherBtn.setAttribute("aria-expanded", "false");
        }
      });

      // Toggle this item
      item.classList.toggle("open", !isOpen);
      btn.setAttribute("aria-expanded", String(!isOpen));
    });
  });
}


// ─── 8. Swiper Carousels ──────────────────────────────────────────────────────

function initSwiperCarousels() {
  if (typeof Swiper === "undefined") return;

  // Testimonials carousel
  const testimonialsEl = $("#testimonials-swiper");
  if (testimonialsEl) {
    new Swiper("#testimonials-swiper", {
      slidesPerView: 1,
      spaceBetween: 24,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
        pauseOnMouseEnter: true,
      },
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
      a11y: {
        prevSlideMessage: "Previous testimonial",
        nextSlideMessage: "Next testimonial",
      },
      breakpoints: {
        640:  { slidesPerView: 1 },
        768:  { slidesPerView: 2 },
        1024: { slidesPerView: 3 },
      },
    });
  }

  // Partners logo carousel
  const partnersEl = $("#partners-swiper");
  if (partnersEl) {
    new Swiper("#partners-swiper", {
      slidesPerView: 3,
      spaceBetween: 40,
      loop: true,
      speed: 3000,
      autoplay: {
        delay: 0,
        disableOnInteraction: false,
      },
      allowTouchMove: false,
      a11y: false,
      breakpoints: {
        480:  { slidesPerView: 4 },
        768:  { slidesPerView: 5 },
        1024: { slidesPerView: 6 },
      },
    });
  }
}


// ─── 9. Mobile Menu ───────────────────────────────────────────────────────────

function initMobileMenu() {
  const btn = $("#mobile-menu-btn");
  const menu = $("#mobile-menu");
  if (!btn || !menu) return;

  let isOpen = false;

  btn.addEventListener("click", () => {
    isOpen = !isOpen;

    // Animate menu height
    menu.style.maxHeight = isOpen ? `${menu.scrollHeight}px` : "0";
    menu.setAttribute("aria-hidden", String(!isOpen));
    btn.setAttribute("aria-expanded", String(isOpen));

    // Animate hamburger lines to X
    const lines = btn.querySelectorAll(".hamburger-line");
    if (isOpen) {
      lines[0].style.transform = "translateY(8px) rotate(45deg)";
      lines[1].style.opacity = "0";
      lines[2].style.transform = "translateY(-8px) rotate(-45deg)";
    } else {
      lines[0].style.transform = "";
      lines[1].style.opacity = "";
      lines[2].style.transform = "";
    }
  });

  // Close menu on link click
  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      isOpen = false;
      menu.style.maxHeight = "0";
      menu.setAttribute("aria-hidden", "true");
      btn.setAttribute("aria-expanded", "false");
    });
  });
}


// ─── 10. Toast System ─────────────────────────────────────────────────────────

function initToastSystem() {
  /**
   * Shows a dismissible toast notification.
   * Exposed as window.showToast() for use in Django message injection.
   *
   * @param {string} message - The message to display
   * @param {string} type - 'success' | 'error' | 'info'
   * @param {number} duration - Auto-dismiss after N ms (default 4000)
   */
  window.showToast = function (message, type = "info", duration = 4000) {
    const container = $("#toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");

    const icons = {
      success: "✅",
      error: "❌",
      info: "ℹ️",
      warning: "⚠️",
    };

    toast.innerHTML = `
      <span aria-hidden="true">${icons[type] || icons.info}</span>
      <span>${message}</span>
      <button onclick="this.parentElement.remove()" aria-label="Dismiss notification" style="margin-left:auto;background:none;border:none;cursor:pointer;color:#9ca3af;">✕</button>
    `;

    container.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  };
}


// ─── 11. Scroll Reveal (Fallback for non-GSAP elements) ───────────────────────

function initRevealOnScroll() {
  const revealElements = $$(".reveal");
  if (revealElements.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
      rootMargin: "0px 0px -40px 0px",
    }
  );

  revealElements.forEach((el) => observer.observe(el));
}
