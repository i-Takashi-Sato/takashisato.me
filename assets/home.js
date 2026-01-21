(() => {
  const rm = window.matchMedia("(prefers-reduced-motion: reduce)");
  const coarse = window.matchMedia("(pointer: coarse)");
  if (rm.matches || coarse.matches) return;

  const root = document.documentElement;
  const works = document.getElementById("archive");
  if (!works) return;

  let active = false;
  let ticking = false;
  let lastX = -999,
    lastY = -999;

  const DRIFT_MAX = 16;     // px
  const DEADZONE = 0.02;    // fraction of viewport (2%)

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

  const park = () => {
    root.style.setProperty("--mouse-x", "-999px");
    root.style.setProperty("--mouse-y", "-999px");
    root.style.setProperty("--drift-x", "0px");
    root.style.setProperty("--drift-y", "0px");
  };

  const setVars = (x, y) => {
    root.style.setProperty("--mouse-x", x + "px");
    root.style.setProperty("--mouse-y", y + "px");

    const nx = (x / window.innerWidth) * 2 - 1;   // -1..1
    const ny = (y / window.innerHeight) * 2 - 1;  // -1..1

    const sx = Math.abs(nx) < DEADZONE ? 0 : nx;
    const sy = Math.abs(ny) < DEADZONE ? 0 : ny;

    const xMove = clamp(sx, -1, 1) * DRIFT_MAX;
    const yMove = clamp(sy, -1, 1) * DRIFT_MAX;

    root.style.setProperty("--drift-x", xMove.toFixed(2) + "px");
    root.style.setProperty("--drift-y", yMove.toFixed(2) + "px");
  };

  const onMove = (e) => {
    lastX = e.clientX;
    lastY = e.clientY;
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      if (active) setVars(lastX, lastY);
      ticking = false;
    });
  };

  const activate = () => {
    if (active) return;
    active = true;
    document.body.classList.add("glow-active");
    window.addEventListener("pointermove", onMove, { passive: true });
  };

  const deactivate = () => {
    if (!active) return;
    active = false;
    document.body.classList.remove("glow-active");
    window.removeEventListener("pointermove", onMove);
    park();
  };

  works.addEventListener("pointerenter", activate);
  works.addEventListener("pointerleave", deactivate);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) deactivate();
  });

  park();
})();
