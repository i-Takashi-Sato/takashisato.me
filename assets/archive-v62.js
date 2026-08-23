(function () {
  'use strict';

  const doc = document;
  const root = doc.documentElement;
  root.classList.add('js');

  /* Progressive v6.6 visual layer. The archive remains complete without it. */
  if (!doc.querySelector('link[data-archive-v66]')) {
    const enhancementStyles = doc.createElement('link');
    enhancementStyles.rel = 'stylesheet';
    enhancementStyles.href = '/assets/archive-v66.css?v=6.6.0';
    enhancementStyles.dataset.archiveV66 = '';
    doc.head.appendChild(enhancementStyles);
  }

  const revealFallback = window.setTimeout(function () { root.classList.remove('js'); }, 3000);
  const clamp = function (value, min, max) { return Math.min(max, Math.max(min, value)); };

  function cursorLabelFor(action) {
    const explicit = action.getAttribute('data-cursor');
    if (explicit) return explicit;
    const href = action.getAttribute('href') || '';
    const text = (action.textContent || '').toLowerCase();
    if (href.includes('.pdf')) return 'PDF';
    if (href.includes('ssrn.com')) return 'SSRN';
    if (href.includes('doi.org')) return 'DOI';
    if (href.includes('orcid.org')) return 'ORCID';
    if (href.includes('scholar.google')) return 'Scholar';
    if (href.startsWith('mailto:')) return 'Mail';
    if (text.includes('author')) return 'Author';
    if (text.includes('paper') || text.includes('trilogy')) return 'Read';
    if (action.getAttribute('target') === '_blank') return 'Open';
    return 'View';
  }

  function initReadingOrientation() {
    const sections = Array.from(doc.querySelectorAll('.content > section[id]'));
    const tocLinks = Array.from(doc.querySelectorAll('.toc a[href^="#"]'));
    if (!sections.length || !tocLinks.length || !('IntersectionObserver' in window)) return;

    const linksById = new Map();
    tocLinks.forEach(function (link) {
      linksById.set(link.getAttribute('href').slice(1), link);
    });

    function activate(section) {
      sections.forEach(function (item) { item.classList.toggle('is-current', item === section); });
      tocLinks.forEach(function (link) { link.removeAttribute('aria-current'); });
      const active = linksById.get(section.id);
      if (active) active.setAttribute('aria-current', 'location');
    }

    const observer = new IntersectionObserver(function (entries) {
      const visible = entries
        .filter(function (entry) { return entry.isIntersecting; })
        .sort(function (a, b) { return Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top); });
      if (visible[0]) activate(visible[0].target);
    }, { rootMargin: '-18% 0px -66% 0px', threshold: [0, 0.08, 0.2] });

    sections.forEach(function (section) { observer.observe(section); });
    activate(sections[0]);
  }

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

    const magnets = Array.from(doc.querySelectorAll('.button'));
    const paperHero = doc.querySelector('.paper-hero');
    let targetX = window.innerWidth / 2;
    let targetY = window.innerHeight / 2;
    let orbitX = targetX;
    let orbitY = targetY;
    let previousX = targetX;
    let previousY = targetY;
    let previousTime = performance.now();
    let cursorVelocity = 0;
    let cursorAngle = 0;
    let pointerDirty = false;
    let activeMagnet = null;
    let activeRelated = null;

    function resetMagnet() {
      magnets.forEach(function (button) {
        button.style.setProperty('--mag-x', '0px');
        button.style.setProperty('--mag-y', '0px');
        button.style.setProperty('--prox', '0');
        button.classList.remove('is-near');
      });
      activeMagnet = null;
      orbit.classList.remove('is-near');
    }

    function setRelated(element) {
      const related = element ? element.closest('.sequence-row, .metric, .fact, .series-nav a, .author-links a') : null;
      if (activeRelated && activeRelated !== related) activeRelated.classList.remove('is-related');
      if (related) related.classList.add('is-related');
      activeRelated = related;
    }

    function updatePointerField() {
      if (!pointerDirty) return;
      pointerDirty = false;
      const now = performance.now();
      const dt = Math.max(8, now - previousTime);
      const dx = targetX - previousX;
      const dy = targetY - previousY;
      const speed = Math.sqrt(dx * dx + dy * dy) / dt;
      const normalized = clamp(speed / 2.1, 0, 1);
      cursorVelocity += (normalized - cursorVelocity) * .28;
      if (Math.abs(dx) + Math.abs(dy) > .25) cursorAngle = Math.atan2(dy, dx) * 180 / Math.PI + 90;
      orbit.style.setProperty('--cursor-v', cursorVelocity.toFixed(3));
      orbit.style.setProperty('--cursor-r', cursorAngle.toFixed(2) + 'deg');
      previousX = targetX;
      previousY = targetY;
      previousTime = now;

      let nearest = null;
      let nearestDistance = Infinity;
      magnets.forEach(function (button) {
        const rect = button.getBoundingClientRect();
        if (rect.bottom < -100 || rect.top > window.innerHeight + 100) return;
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const distance = Math.hypot(targetX - cx, targetY - cy);
        const radius = Math.max(86, Math.min(150, Math.max(rect.width, rect.height) * 1.15));
        const proximity = clamp(1 - distance / radius, 0, 1);
        button.style.setProperty('--prox', proximity.toFixed(3));
        button.style.setProperty('--pointer-x', clamp((targetX - rect.left) / rect.width * 100, 0, 100).toFixed(2) + '%');
        button.style.setProperty('--pointer-y', clamp((targetY - rect.top) / rect.height * 100, 0, 100).toFixed(2) + '%');
        button.classList.toggle('is-near', proximity > .05);
        if (distance < nearestDistance && proximity > .05) {
          nearest = button;
          nearestDistance = distance;
        }
      });

      if (activeMagnet && activeMagnet !== nearest) {
        activeMagnet.style.setProperty('--mag-x', '0px');
        activeMagnet.style.setProperty('--mag-y', '0px');
      }
      activeMagnet = nearest;
      orbit.classList.toggle('is-near', Boolean(nearest));
      if (nearest) {
        const rect = nearest.getBoundingClientRect();
        const strength = parseFloat(getComputedStyle(nearest).getPropertyValue('--prox')) || 0;
        const x = (targetX - rect.left - rect.width / 2) * .11 * strength;
        const y = (targetY - rect.top - rect.height / 2) * .13 * strength;
        nearest.style.setProperty('--mag-x', x.toFixed(2) + 'px');
        nearest.style.setProperty('--mag-y', y.toFixed(2) + 'px');
      }

      if (paperHero) {
        const rect = paperHero.getBoundingClientRect();
        if (targetY >= rect.top && targetY <= rect.bottom) {
          const nx = clamp((targetX - rect.left) / rect.width - .5, -.5, .5);
          const ny = clamp((targetY - rect.top) / rect.height - .5, -.5, .5);
          paperHero.style.setProperty('--stage-x', (nx * -18).toFixed(2) + 'px');
          paperHero.style.setProperty('--stage-y', (ny * -11).toFixed(2) + 'px');
        }
      }
    }

    function renderCursor() {
      const lag = .135 + cursorVelocity * .055;
      orbitX += (targetX - orbitX) * lag;
      orbitY += (targetY - orbitY) * lag;
      dot.style.transform = 'translate3d(' + targetX + 'px, ' + targetY + 'px, 0)';
      orbit.style.transform = 'translate3d(' + orbitX + 'px, ' + orbitY + 'px, 0)';
      updatePointerField();
      window.requestAnimationFrame(renderCursor);
    }

    doc.addEventListener('pointermove', function (event) {
      if (event.pointerType === 'touch') return;
      targetX = event.clientX;
      targetY = event.clientY;
      pointerDirty = true;
      dot.classList.add('is-visible');
      orbit.classList.add('is-visible');

      const element = event.target instanceof Element ? event.target : null;
      const action = element ? element.closest('a, button, [data-cursor]') : null;
      const isAction = Boolean(action);
      dot.classList.toggle('is-active', isAction);
      orbit.classList.toggle('is-active', isAction);
      if (action) orbitLabel.textContent = cursorLabelFor(action);

      const surface = element ? element.closest('.sequence-row, .metric, .fact, .series-nav a, .author-links a') : null;
      if (surface) {
        const rect = surface.getBoundingClientRect();
        surface.style.setProperty('--pointer-x', clamp((event.clientX - rect.left) / rect.width * 100, 0, 100).toFixed(2) + '%');
        surface.style.setProperty('--pointer-y', clamp((event.clientY - rect.top) / rect.height * 100, 0, 100).toFixed(2) + '%');
      }
      setRelated(element);
    }, { passive: true });

    doc.addEventListener('pointerout', function (event) {
      const element = event.target instanceof Element ? event.target : null;
      const related = event.relatedTarget instanceof Element ? event.relatedTarget : null;
      if (element && activeRelated && !(related && activeRelated.contains(related))) {
        activeRelated.classList.remove('is-related');
        activeRelated = null;
      }
    }, { passive: true });

    window.addEventListener('mouseout', function (event) {
      if (event.relatedTarget) return;
      dot.classList.remove('is-visible');
      orbit.classList.remove('is-visible');
      if (activeRelated) activeRelated.classList.remove('is-related');
      activeRelated = null;
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
    const homeHero = doc.querySelector('body[data-page="home"] .hero');
    const footer = doc.querySelector('.site-footer');
    let lastScrollY = window.scrollY;

    function updateScrollState() {
      const max = root.scrollHeight - window.innerHeight;
      const value = max > 0 ? clamp(window.scrollY / max, 0, 1) : 0;
      root.style.setProperty('--scroll', value.toFixed(4));
      root.dataset.scrollDir = window.scrollY > lastScrollY + 2 ? 'down' : window.scrollY < lastScrollY - 2 ? 'up' : (root.dataset.scrollDir || 'down');
      lastScrollY = window.scrollY;

      if (homeHero && !reduceMotion) {
        const extent = Math.max(homeHero.offsetHeight * 1.15, window.innerHeight);
        root.style.setProperty('--home-scroll', clamp(window.scrollY / extent, 0, 1).toFixed(4));
      }

      if (footer) {
        const rect = footer.getBoundingClientRect();
        const ending = clamp(1 - rect.top / window.innerHeight, 0, 1);
        root.style.setProperty('--ending', ending.toFixed(4));
        root.classList.toggle('is-ending', ending > .48);
      }
    }

    let ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        updateScrollState();
        ticking = false;
      });
    }, { passive: true });
    window.addEventListener('resize', function () {
      window.requestAnimationFrame(updateScrollState);
    }, { passive: true });
    updateScrollState();

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

    initReadingOrientation();
    initPointerExperience(reduceMotion);
    window.clearTimeout(revealFallback);
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();