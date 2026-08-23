(function () {
  'use strict';

  const doc = document;
  const root = doc.documentElement;
  root.classList.add('js');
  const revealFallback = window.setTimeout(function () { root.classList.remove('js'); }, 3000);

  function initPointerExperience(reduceMotion) {
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    if (reduceMotion || !finePointer.matches) return;

    const dot = doc.createElement('div');
    const orbit = doc.createElement('div');
    const orbitLabel = doc.createElement('span');
    dot.className = 'cursor-dot';
    orbit.className = 'cursor-orbit';
    dot.setAttribute('aria-hidden', 'true');
    orbit.setAttribute('aria-hidden', 'true');
    orbitLabel.textContent = 'View';
    orbit.appendChild(orbitLabel);
    doc.body.append(dot, orbit);
    root.classList.add('has-custom-cursor');

    let targetX = window.innerWidth / 2;
    let targetY = window.innerHeight / 2;
    let orbitX = targetX;
    let orbitY = targetY;
    let activeMagnet = null;

    function renderCursor() {
      orbitX += (targetX - orbitX) * 0.16;
      orbitY += (targetY - orbitY) * 0.16;
      dot.style.transform = `translate3d(${targetX}px, ${targetY}px, 0)`;
      orbit.style.transform = `translate3d(${orbitX}px, ${orbitY}px, 0)`;
      window.requestAnimationFrame(renderCursor);
    }

    function resetMagnet() {
      if (!activeMagnet) return;
      activeMagnet.style.setProperty('--mag-x', '0px');
      activeMagnet.style.setProperty('--mag-y', '0px');
      activeMagnet = null;
    }

    doc.addEventListener('pointermove', function (event) {
      if (event.pointerType === 'touch') return;
      targetX = event.clientX;
      targetY = event.clientY;
      dot.classList.add('is-visible');
      orbit.classList.add('is-visible');

      const element = event.target instanceof Element ? event.target : null;
      const action = element ? element.closest('a, button, [data-cursor]') : null;
      const isAction = Boolean(action);
      dot.classList.toggle('is-active', isAction);
      orbit.classList.toggle('is-active', isAction);
      if (action) {
        const href = action.getAttribute('href') || '';
        orbitLabel.textContent = action.getAttribute('data-cursor')
          || (href.includes('.pdf') ? 'PDF' : href.startsWith('mailto:') ? 'Mail' : action.getAttribute('target') === '_blank' ? 'Open' : 'View');
      }

      const surface = element ? element.closest('.sequence-row, .metric, .fact, .series-nav a, .author-links a') : null;
      if (surface) {
        const rect = surface.getBoundingClientRect();
        surface.style.setProperty('--pointer-x', `${((event.clientX - rect.left) / rect.width * 100).toFixed(2)}%`);
        surface.style.setProperty('--pointer-y', `${((event.clientY - rect.top) / rect.height * 100).toFixed(2)}%`);
      }

      const magnet = element ? element.closest('.button') : null;
      if (activeMagnet && activeMagnet !== magnet) resetMagnet();
      if (magnet) {
        const rect = magnet.getBoundingClientRect();
        const x = (event.clientX - rect.left - rect.width / 2) * 0.13;
        const y = (event.clientY - rect.top - rect.height / 2) * 0.16;
        magnet.style.setProperty('--mag-x', `${x.toFixed(2)}px`);
        magnet.style.setProperty('--mag-y', `${y.toFixed(2)}px`);
        activeMagnet = magnet;
      }
    }, { passive: true });

    doc.addEventListener('pointerout', function (event) {
      const element = event.target instanceof Element ? event.target : null;
      const button = element ? element.closest('.button') : null;
      if (button && !(event.relatedTarget instanceof Node && button.contains(event.relatedTarget))) resetMagnet();
    }, { passive: true });

    window.addEventListener('mouseout', function (event) {
      if (event.relatedTarget) return;
      dot.classList.remove('is-visible');
      orbit.classList.remove('is-visible');
      resetMagnet();
    });
    window.addEventListener('blur', function () {
      dot.classList.remove('is-visible');
      orbit.classList.remove('is-visible');
      resetMagnet();
    });

    renderCursor();
  }

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

    initPointerExperience(reduceMotion);
    window.clearTimeout(revealFallback);
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
