// Desktop-only performance cap for canvas-heavy instruments.
// Keeps mobile behavior intact while reducing desktop pixel-fill pressure.
(() => {
  const coarse = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  if (coarse) return;

  const nativeDpr = Number(window.devicePixelRatio || 1);
  const cappedDpr = Math.min(nativeDpr, 1.22);

  try {
    Object.defineProperty(window, 'devicePixelRatio', {
      configurable: true,
      get: () => cappedDpr
    });
    document.documentElement.dataset.instrumentDprCap = String(cappedDpr);
  } catch {
    document.documentElement.dataset.instrumentDprCap = 'native';
  }
})();
