(() => {
  if (!document.body.classList.contains('proper-ending-index')) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const loadLateStylesheet = (href) => {
    if (document.querySelector(`link[href="${href}"]`)) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  };

  loadLateStylesheet('/assets/mobile-paper-topbar-fix.css');
  loadLateStylesheet('/assets/paper-cta-hierarchy.css');
  loadLateStylesheet('/assets/proper-ending-material-system.css');

  const menu = document.querySelector('.pei-menu');
  if (menu) {
    menu.addEventListener('click', () => {
      const open = document.body.classList.toggle('pei-index-open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }

  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  const format = (n) => n.toFixed(2).replace(/^0/, '0');

  const specimen = document.querySelector('.pei-specimen, [data-gdi-specimen]');
  if (specimen && !reduce) {
    const readout = document.createElement('div');
    readout.className = 'gdi-readout';
    readout.setAttribute('aria-label', 'Governance Drift Indicator readout');
    readout.innerHTML = [
      ['SED', 'Semantic Entropy'],
      ['TC', 'Temporal Compression'],
      ['ED', 'Dissent Exhaustion'],
      ['CB', 'Circuit Breaker']
    ].map(([abbr, label]) => `<span><small>${abbr}</small><b>0.00</b><span class="bar"><i style="--value:0"></i></span><em>${label}</em></span>`).join('');
    specimen.appendChild(readout);
    const values = [...readout.querySelectorAll('b')];
    const bars = [...readout.querySelectorAll('.bar i')];

    let active = false;
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        active = entry.isIntersecting;
        document.body.classList.toggle('gdi-active', active);
      }
    }, { threshold: 0.34 });
    observer.observe(specimen);

    const tick = () => {
      const rect = specimen.getBoundingClientRect();
      const viewport = window.innerHeight || 1;
      const raw = 1 - ((rect.top + rect.height * 0.22) / (viewport + rect.height * 0.56));
      const progress = clamp(raw, 0, 1);
      const entropy = clamp(0.12 + progress * 0.72, 0, 1);
      const compression = clamp(0.10 + progress * 0.78, 0, 1);
      const dissent = clamp(0.92 - progress * 0.82, 0, 1);
      const risk = clamp((entropy + compression + (1 - dissent)) / 3, 0, 1);
      document.documentElement.style.setProperty('--gdi-entropy', entropy.toFixed(3));
      document.documentElement.style.setProperty('--gdi-compression', compression.toFixed(3));
      document.documentElement.style.setProperty('--gdi-dissent', dissent.toFixed(3));
      document.documentElement.style.setProperty('--gdi-risk', risk.toFixed(3));
      document.body.classList.toggle('gdi-critical', active && risk > 0.68);
      const nums = [entropy, compression, 1 - dissent, risk];
      nums.forEach((value, index) => {
        if (values[index]) values[index].textContent = format(value);
        if (bars[index]) bars[index].style.setProperty('--value', value.toFixed(3));
      });
    };
    tick();
    window.addEventListener('scroll', tick, { passive: true });
    window.addEventListener('resize', tick);
  }

  const ending = document.querySelector('[data-proper-ending]');
  if (ending && !reduce) {
    const stopObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        document.body.classList.toggle('circuit-armed', entry.isIntersecting);
      }
    }, { threshold: 0.56 });
    stopObserver.observe(ending);
  }
})();