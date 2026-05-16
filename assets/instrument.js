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
  document.querySelectorAll('.bp-protocol-row,.bp-routes,.bp-signal-table a,.bp-intro,.bp-reader,.iv-file,.iv-row,.iv-panel,.iv-console,.paper-hero,.abstract-body,.simple-page section').forEach((el) => io.observe(el));

  let audioOn = false;
  let ctx;
  function tone(freq = 112, dur = 0.055, gain = 0.018) {
    if (!audioOn) return;
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const amp = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, now);
    osc.frequency.exponentialRampToValueAtTime(freq * 0.72, now + dur);
    amp.gain.setValueAtTime(0.0001, now);
    amp.gain.exponentialRampToValueAtTime(gain, now + 0.01);
    amp.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.connect(amp).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + dur + 0.02);
  }
  function paperClick() { tone(82, 0.075, 0.014); setTimeout(() => tone(146, 0.04, 0.01), 42); }
  function hoverTick() { tone(168, 0.035, 0.006); }
  document.querySelectorAll('[data-sound-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      audioOn = !audioOn;
      btn.setAttribute('aria-pressed', String(audioOn));
      btn.textContent = audioOn ? 'Sound On' : 'Sound Off';
      if (audioOn) { ctx = ctx || new (window.AudioContext || window.webkitAudioContext)(); ctx.resume(); tone(110, 0.11, 0.018); setTimeout(() => tone(74, 0.08, 0.012), 90); }
    });
  });
  document.addEventListener('click', (event) => {
    if (event.target.closest('a,button')) paperClick();
  }, { passive: true });
  let last = 0;
  document.addEventListener('pointerover', (event) => {
    if (!event.target.closest('.bp-protocol-row,.bp-route-list a,.bp-signal-table a,.bp-link')) return;
    const now = performance.now();
    if (now - last < 120) return;
    last = now;
    hoverTick();
  }, { passive: true });
})();
