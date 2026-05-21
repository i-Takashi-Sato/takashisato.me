(() => {
  if (!document.body.classList.contains('proper-ending-index')) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const path = window.location.pathname;
  const isHome = path === '/' || path.endsWith('/index.html');
  if (isHome) document.body.classList.add('home-forensic-chamber');
  if (path.includes('/papers/part1')) document.body.classList.add('pei-part-1');
  if (path.includes('/papers/part2')) document.body.classList.add('pei-part-2');
  if (path.includes('/papers/part3')) document.body.classList.add('pei-part-3');

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
  loadLateStylesheet('/assets/brand-signature-polish.css');
  loadLateStylesheet('/assets/catalogue-read-kill.css');
  loadLateStylesheet('/assets/mobile-scroll-fix.css');
  loadLateStylesheet('/assets/home-mobile-scroll-fix.css');
  loadLateStylesheet('/assets/mobile-capture-blackout.css');

  if (isHome) {
    loadLateStylesheet('/assets/home-forensic-chamber.css?v=1');
  } else {
    loadLateStylesheet('/assets/archive-reading-density.css');
    loadLateStylesheet('/assets/archive-balance-v8.css');
    loadLateStylesheet('/assets/rejouice-immersive-overhaul.css?v=1');
  }
  loadLateStylesheet('/assets/archive-v77-fixes.css?v=77');
  loadLateStylesheet('/assets/archive-v78-corrections.css?v=78');

  const setScrolled = () => document.body.classList.toggle('v77-scrolled', window.scrollY > 12);
  setScrolled();
  window.addEventListener('scroll', setScrolled, { passive: true });

  const brand = document.querySelector('.pei-brand');
  if (brand) {
    brand.setAttribute('role', 'link');
    brand.setAttribute('tabindex', '0');
    brand.setAttribute('aria-label', 'Return to Takashi Sato research index');
    brand.addEventListener('click', () => { window.location.href = '/'; });
    brand.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        window.location.href = '/';
      }
    });
  }

  const menu = document.querySelector('.pei-menu');
  if (menu) {
    menu.addEventListener('click', () => {
      const open = document.body.classList.toggle('pei-index-open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }

  if (!reduce && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('v77-motion');
    const revealTargets = document.querySelectorAll('main > section, main > figure, .catalogue-row, .a3-paper-row, .paper-map article, .protocol, .access-card, .failure-timeline li, .failure-signal-index article, .a3-plate, .a3-route, .research-position article');
    revealTargets.forEach((el) => el.classList.add('v77-reveal'));
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('v77-in');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealTargets.forEach((el) => revealObserver.observe(el));
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