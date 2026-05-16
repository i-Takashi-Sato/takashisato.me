(() => {
  const stage = document.querySelector('.wcz-stage');
  if (!stage) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  stage.addEventListener('pointermove', (event) => {
    const rect = stage.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    stage.style.setProperty('--mx', `${x.toFixed(2)}%`);
    stage.style.setProperty('--my', `${y.toFixed(2)}%`);
    document.body.style.setProperty('--mx', `${x.toFixed(2)}%`);
    document.body.style.setProperty('--my', `${y.toFixed(2)}%`);
  }, { passive: true });
})();
