(() => {
  document.documentElement.classList.add('instrument-ready');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  function scramble(el) {
    if (reduceMotion || !el || el.dataset.done) return;
    const text = el.textContent || '';
    el.dataset.done = '1';
    let step = 0;
    const total = 16;
    const timer = setInterval(() => {
      step += 1;
      const p = step / total;
      el.textContent = text.split('').map((ch, i) => {
        if (ch === ' ' || ch === '/' || ch === ':' || ch === '-') return ch;
        return i / text.length < p ? text[i] : chars[Math.floor(Math.random() * chars.length)];
      }).join('');
      if (step >= total) { clearInterval(timer); el.textContent = text; }
    }, 24);
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      entry.target.querySelectorAll('[data-scramble]').forEach(scramble);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.iv-file,.iv-row,.iv-panel,.iv-console,.paper-hero,.abstract-body,.simple-page section').forEach((el) => io.observe(el));
})();
