/**
 * Lenis Smooth Scroll — Green Naroda Portal
 * Initialises Lenis and syncs it with GSAP's ScrollTrigger.
 *
 * DISABLED: Lenis's eased/inertial wheel scroll was reported as slow and
 * laggy on desktop Chrome, and repeated attempts to fix its interaction
 * with the site's popups (which lock background scroll while open) did
 * not resolve it. Disabling it falls back to normal native browser
 * scrolling everywhere — anchor links (`href="#section"`) still animate
 * via the site's `scroll-behavior: smooth` CSS (main.css), so that
 * behavior isn't lost. `window.__lenis` simply stays undefined; other
 * scripts already guard every use of it with `?.`, so this is safe.
 */

(function () {
  "use strict";

  // Only initialise when DOM is ready
  document.addEventListener("DOMContentLoaded", function () {
    return; // Lenis disabled — see note above.
    // eslint-disable-next-line no-unreachable
    if (typeof Lenis === "undefined") return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: function (t) {
        return Math.min(1, 1.001 - Math.pow(2, -10 * t));
      },
      smooth: true,
      smoothTouch: false,
      touchMultiplier: 2,
    });

    // Expose globally so other scripts can use lenis.scrollTo()
    window.__lenis = lenis;

    // RAF loop
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Sync with GSAP ScrollTrigger if available
    if (typeof ScrollTrigger !== "undefined") {
      lenis.on("scroll", ScrollTrigger.update);
      ScrollTrigger.defaults({ scroller: document.documentElement });
    }

    // Handle anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener("click", function (e) {
        var target = document.querySelector(this.getAttribute("href"));
        if (target) {
          e.preventDefault();
          lenis.scrollTo(target, { offset: -80, duration: 1.4 });
        }
      });
    });
  });
})();
