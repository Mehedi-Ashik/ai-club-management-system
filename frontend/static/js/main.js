// Global JS for the Club Management System
document.addEventListener("DOMContentLoaded", () => {
    console.log("Club Management System loaded.");

    // ===== Scroll-reveal animation =====
    const revealEls = document.querySelectorAll(".reveal");
    if (revealEls.length) {
        const revealObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in-view");
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        revealEls.forEach((el) => revealObserver.observe(el));
    }

    // ===== Animated stat counters =====
    const counters = document.querySelectorAll("[data-count]");
    if (counters.length) {
        const animateCounter = (el) => {
            const target = parseInt(el.getAttribute("data-count"), 10) || 0;
            const duration = 1200;
            const startTime = performance.now();

            const step = (now) => {
                const progress = Math.min((now - startTime) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.round(eased * target);
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = target;
                }
            };
            requestAnimationFrame(step);
        };

        const counterObserver = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });

        counters.forEach((el) => counterObserver.observe(el));
    }
});