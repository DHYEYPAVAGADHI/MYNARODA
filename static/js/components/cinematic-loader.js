document.addEventListener("DOMContentLoaded", () => {
    // If GSAP is not available, just hide the loader immediately.
    if (typeof gsap === 'undefined') {
        const loader = document.getElementById('global-preloader');
        if (loader) loader.style.display = 'none';
        return;
    }

    const tl = gsap.timeline({
        onComplete: () => {
            gsap.to("#global-preloader", {
                yPercent: -100,
                duration: 0.8,
                ease: "power3.inOut",
                onComplete: () => {
                    document.getElementById('global-preloader').style.display = 'none';
                    // Trigger ScrollTrigger refresh after loader is gone
                    if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.refresh();
                }
            });
        }
    });

    // 1. Seed appears
    tl.to(".loader-seed", { y: 0, opacity: 1, duration: 0.4, ease: "back.out(1.7)" })
      // 2. Soil appears
      .to(".loader-soil", { scaleX: 1, duration: 0.4, ease: "power2.out" }, "-=0.2")
      // 3. Sprout grows (stem)
      .to(".loader-stem", { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut" })
      // 4. Leaves appear
      .to(".loader-leaf", { scale: 1, duration: 0.4, stagger: 0.1, ease: "back.out(2)" }, "-=0.2")
      // 5. Logo and text fades in
      .to([".loader-logo", ".loader-text"], { opacity: 1, y: -10, duration: 0.4, stagger: 0.1 }, "+=0.1")
      // Hold for a moment to let user read
      .to({}, { duration: 0.4 });
});
