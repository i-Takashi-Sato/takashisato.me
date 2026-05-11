(() => {
  const y = document.getElementById("y");
  if (y) y.textContent = String(new Date().getFullYear());

  const cards = [...document.querySelectorAll(".v4-card")];
  if (!cards.length) return;

  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const coarsePointer = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const isInteractive = (t) => !!t.closest("a,button,input,select,textarea,[role='button']");

  const setFromEvent = (el, e) => {
    const r = el.getBoundingClientRect();
    const x = clamp(e.clientX - r.left, 0, r.width);
    const y = clamp(e.clientY - r.top, 0, r.height);
    el.style.setProperty("--x", x + "px");
    el.style.setProperty("--y", y + "px");

    if (!reduceMotion && !coarsePointer) {
      const cx = r.width / 2;
      const cy = r.height / 2;
      const rx = ((y - cy) / cy) * -1.4;
      const ry = ((x - cx) / cx) * 1.4;
      el.style.setProperty("--rx", rx + "deg");
      el.style.setProperty("--ry", ry + "deg");
    }
  };

  for (const el of cards) {
    let raf = 0;
    let latestEvent = null;

    const schedule = (e) => {
      latestEvent = e;
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        if (latestEvent) setFromEvent(el, latestEvent);
      });
    };

    if (!coarsePointer) {
      el.addEventListener("pointermove", schedule, { passive: true });
      el.addEventListener("pointerenter", schedule, { passive: true });
      el.addEventListener("pointerleave", () => {
        latestEvent = null;
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
        el.style.setProperty("--rx", "0deg");
        el.style.setProperty("--ry", "0deg");
      }, { passive: true });
    }

    el.addEventListener("click", (e) => {
      if (isInteractive(e.target)) return;
      const href = el.getAttribute("data-href");
      if (href) window.location.href = href;
    });

    el.addEventListener("keydown", (e) => {
      if (isInteractive(e.target)) return;
      if (e.key === "Enter" || e.key === " ") {
        const href = el.getAttribute("data-href");
        if (href) {
          e.preventDefault();
          window.location.href = href;
        }
      }
    });
  }
})();
