(function () {
  'use strict';

  const doc = document;
  const root = doc.documentElement;
  root.classList.add('js');
  const revealFallback = window.setTimeout(function () { root.classList.remove('js'); }, 3000);

  function init() {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function updateScrollMeter() {
      const max = root.scrollHeight - window.innerHeight;
      const value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      root.style.setProperty('--scroll', value.toFixed(4));
    }

    let ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        updateScrollMeter();
        ticking = false;
      });
    }, { passive: true });
    updateScrollMeter();

    const revealItems = Array.from(doc.querySelectorAll('[data-reveal]'));
    if (reduceMotion || !('IntersectionObserver' in window)) {
      revealItems.forEach(function (item) { item.classList.add('is-visible'); });
    } else {
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });
      revealItems.forEach(function (item) { observer.observe(item); });
    }

    doc.querySelectorAll('a[target="_blank"]').forEach(function (anchor) {
      const rel = new Set((anchor.getAttribute('rel') || '').split(/\s+/).filter(Boolean));
      rel.add('noopener');
      rel.add('noreferrer');
      anchor.setAttribute('rel', Array.from(rel).join(' '));
    });

    window.clearTimeout(revealFallback);
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
