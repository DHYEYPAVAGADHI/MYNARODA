/**
 * Lenis Smooth Scroll — Green Naroda Portal
 * Initialises Lenis and syncs it with GSAP's ScrollTrigger.
 */

(function () {
  "use strict";

  // Only initialise when DOM is ready
  document.addEventListener("DOMContentLoaded", function () {
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
