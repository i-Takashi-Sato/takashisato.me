(() => {
  if (!document.body.classList.contains('proper-ending-index')) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const menu = document.querySelector('.pei-menu');
  if (menu) {
    menu.addEventListener('click', () => {
      const open = document.body.classList.toggle('pei-index-open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }

  const specimen = document.querySelector('.pei-specimen, [data-gdi-specimen]');
  if (specimen && !reduce) {
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) document.body.classList.toggle('gdi-active', entry.isIntersecting);
    }, { threshold: 0.42 });
    observer.observe(specimen);
  }

  const ending = document.querySelector('[data-proper-ending]');
  if (ending && !reduce) {
    const overlay = document.createElement('div');
    overlay.className = 'pei-stop-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Circuit breaker acknowledgement');
    overlay.innerHTML = '<div class="pei-stop-card"><small>Circuit Breaker</small><h2>Process suspended.</h2><p>Meaningful judgment can no longer be verified. Reactivation requires an explicit human acknowledgement.</p><button type="button">Acknowledge and continue</button></div>';
    document.body.appendChild(overlay);
    const button = overlay.querySelector('button');
    button.addEventListener('click', () => overlay.classList.remove('is-visible'));
    let shown = sessionStorage.getItem('proper-ending-acknowledged') === '1';
    const stopObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && !shown) {
          shown = true;
          sessionStorage.setItem('proper-ending-acknowledged', '1');
          overlay.classList.add('is-visible');
          setTimeout(() => button.focus(), 80);
        }
      }
    }, { threshold: 0.7 });
    stopObserver.observe(ending);
  }
})();
