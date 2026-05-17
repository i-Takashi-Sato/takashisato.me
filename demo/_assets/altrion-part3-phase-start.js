// Part III should open from Phase 00 / Surface, not mid-sequence.
(() => {
  const resetToSurface = () => {
    const reset = document.getElementById('reset');
    if (reset) reset.click();
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => requestAnimationFrame(resetToSurface), { once: true });
  } else {
    requestAnimationFrame(resetToSurface);
  }
})();
