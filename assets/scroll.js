/* assets/scroll.js — Kinetic Engine (Progress + Reveal)
   - No dependencies, CSP-safe (no inline eval)
   - Features:
     1) Top scroll progress bar (.scroll-progress)
     2) IntersectionObserver reveal for cards/articles (.reveal -> .is-visible)
*/

(() => {
  const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const onReady = () => {
    // 1) Scroll progress bar
    const mount = document.querySelector(".top") || document.body;
    let bar = document.querySelector(".scroll-progress");
    if (!bar) {
      bar = document.createElement("div");
      bar.className = "scroll-progress";
      mount.appendChild(bar);
    }

    const updateProgress = () => {
      const doc = document.documentElement;
      const scrollTop = window.scrollY || doc.scrollTop || 0;
      const max = Math.max(1, (doc.scrollHeight - window.innerHeight));
      const pct = Math.min(100, Math.max(0, (scrollTop / max) * 100));
      bar.style.width = pct.toFixed(3) + "%";
    };

    // rAF throttle
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(() => {
        updateProgress();
        ticking = false;
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();

    // 2) Reveal animation (home cards + any element that already has .reveal)
    // Home cards: <article class="paper"> ... </article>
    const candidates = new Set();
    document.querySelectorAll(".reveal").forEach(el => candidates.add(el));
    document.querySelectorAll("#archive article.paper").forEach(el => candidates.add(el));

    const targets = Array.from(candidates);
    if (targets.length === 0) return;

    // Ensure they start hidden only when motion is allowed
    if (prefersReducedMotion) {
      targets.forEach(el => el.classList.add("is-visible"));
      return;
    } else {
      targets.forEach(el => el.classList.add("reveal"));
    }

    if (!("IntersectionObserver" in window)) {
      targets.forEach(el => el.classList.add("is-visible"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px" }
    );

    targets.forEach(el => io.observe(el));
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady, { once: true });
  } else {
    onReady();
  }
})();
