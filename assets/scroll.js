// assets/scroll.js — Black Porcelain (quiet motion)
// - Updates --scroll for progress + subtle background response
// - Optional pointer highlight (very subtle), respects reduced motion

(function () {
  const root = document.documentElement;

  // Inject progress bar (no HTML edits needed)
  const bar = document.createElement("div");
  bar.className = "progress";
  bar.setAttribute("aria-hidden", "true");
  document.addEventListener("DOMContentLoaded", () => {
    document.body.prepend(bar);
  });

  let ticking = false;

  function updateScrollVars() {
    const h = Math.max(1, document.body.scrollHeight - innerHeight);
    const v = Math.min(1, Math.max(0, scrollY / h));
    root.style.setProperty("--scroll", v.toFixed(4));
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      updateScrollVars();
      ticking = false;
    });
  }

  // Subtle pointer highlight (disable for reduced motion)
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function onMove(e) {
    if (reduceMotion) return;
    const x = Math.round((e.clientX / innerWidth) * 100);
    const y = Math.round((e.clientY / innerHeight) * 100);
    root.style.setProperty("--mx", `${x}%`);
    root.style.setProperty("--my", `${y}%`);
  }

  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("pointermove", onMove, { passive: true });

  // Init
  updateScrollVars();
})();
