(() => {
  // V57 Kinetic Engine
  const rm = window.matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = window.matchMedia('(pointer: coarse)');
  if (rm.matches || coarse.matches) return;

  const root = document.documentElement;
  const works = document.getElementById('archive');
  if (!works) return;

  let active = false;
  let ticking = false;
  let lastX = -999, lastY = -999;

  const park = () => {
    root.style.setProperty('--mouse-x', '-999px');
    root.style.setProperty('--mouse-y', '-999px');
    root.style.setProperty('--drift-x', '0px');
    root.style.setProperty('--drift-y', '0px');
  };

  const setVars = (x, y) => {
    root.style.setProperty('--mouse-x', x + 'px');
    root.style.setProperty('--mouse-y', y + 'px');
    const xMove = (x / window.innerWidth  - 0.5) * 25;
    const yMove = (y / window.innerHeight - 0.5) * 25;
    root.style.setProperty('--drift-x', xMove + 'px');
    root.style.setProperty('--drift-y', yMove + 'px');
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
    document.body.classList.add('glow-active');
    window.addEventListener('pointermove', onMove, { passive: true });
  };

  const deactivate = () => {
    if (!active) return;
    active = false;
    document.body.classList.remove('glow-active');
    window.removeEventListener('pointermove', onMove);
    park();
  };

  works.addEventListener('pointerenter', activate);
  works.addEventListener('pointerleave', deactivate);
  document.addEventListener('visibilitychange', () => { if (document.hidden) deactivate(); });
  park();
})();
