/* The Proper Ending Index — progressive enhancement.
 *
 * Research content is complete before this script runs. JavaScript adds only
 * orientation, pointer response, reveal timing, and terminal settling.
 */
(() => {
  'use strict';

  const doc = document;
  const root = doc.documentElement;
  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));

  root.classList.add('js');

  // If initialization fails, return to the complete no-JavaScript presentation.
  const initializationFallback = setTimeout(() => root.classList.remove('js'), 3000);

  function initReadingState() {
    const sections = [...doc.querySelectorAll('.content > section[id]')];
    const links = [...doc.querySelectorAll('.toc a[href^="#"]')];
    if (!sections.length || !links.length || !window.IntersectionObserver) return;

    const linksById = new Map(links.map((link) => [link.hash.slice(1), link]));

    function setCurrent(section) {
      sections.forEach((item) => item.classList.toggle('is-current', item === section));
      links.forEach((link) => link.removeAttribute('aria-current'));
      linksById.get(section.id)?.setAttribute('aria-current', 'location');
    }

    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top));
      if (visible[0]) setCurrent(visible[0].target);
    }, {
      rootMargin: '-18% 0px -66% 0px',
      threshold: [0, 0.08, 0.2],
    });

    sections.forEach((section) => observer.observe(section));
    setCurrent(sections[0]);
  }

  function cursorLabel(control) {
    const href = control.getAttribute('href') || '';
    const text = (control.textContent || '').toLowerCase();
    if (control.dataset.cursor) return control.dataset.cursor;
    if (href.includes('.pdf')) return 'PDF';
    if (href.includes('ssrn.com')) return 'SSRN';
    if (href.includes('doi.org')) return 'DOI';
    if (href.includes('orcid.org')) return 'ORCID';
    if (href.includes('scholar.google')) return 'Scholar';
    if (href.startsWith('mailto:')) return 'Mail';
    if (text.includes('author')) return 'Author';
    if (text.includes('paper') || text.includes('trilogy')) return 'Read';
    return control.target === '_blank' ? 'Open' : 'View';
  }

  function initAuthorityCursor(reduceMotion) {
    if (reduceMotion || !matchMedia('(hover:hover) and (pointer:fine)').matches) return;

    const dot = doc.createElement('div');
    const orbit = doc.createElement('div');
    const label = doc.createElement('span');
    dot.className = 'cursor-dot';
    orbit.className = 'cursor-orbit';
    dot.ariaHidden = 'true';
    orbit.ariaHidden = 'true';
    label.textContent = 'View';
    orbit.append(label);
    doc.body.append(dot, orbit);
    root.classList.add('has-custom-cursor');

    const magneticControls = [...doc.querySelectorAll('.button')];
    const paperHero = doc.querySelector('.paper-hero');
    let pointerX = innerWidth / 2;
    let pointerY = innerHeight / 2;
    let orbitX = pointerX;
    let orbitY = pointerY;
    let previousX = pointerX;
    let previousY = pointerY;
    let previousTime = performance.now();
    let velocity = 0;
    let angle = 0;
    let dirty = false;
    let nearest = null;

    function renderFrame() {
      orbitX += (pointerX - orbitX) * (0.135 + velocity * 0.055);
      orbitY += (pointerY - orbitY) * (0.135 + velocity * 0.055);
      dot.style.transform = `translate3d(${pointerX}px,${pointerY}px,0)`;
      orbit.style.transform = `translate3d(${orbitX}px,${orbitY}px,0)`;

      if (dirty) {
        dirty = false;
        const now = performance.now();
        const dx = pointerX - previousX;
        const dy = pointerY - previousY;
        const speed = Math.hypot(dx, dy) / Math.max(8, now - previousTime);
        velocity += (clamp(speed / 2.1) - velocity) * 0.28;
        if (Math.abs(dx) + Math.abs(dy) > 0.25) angle = Math.atan2(dy, dx) * 180 / Math.PI + 90;
        orbit.style.setProperty('--cursor-v', velocity.toFixed(3));
        orbit.style.setProperty('--cursor-r', `${angle.toFixed(1)}deg`);
        previousX = pointerX;
        previousY = pointerY;
        previousTime = now;

        let nextNearest = null;
        let nearestDistance = Infinity;
        let nearestProximity = 0;
        let nearestRect = null;

        magneticControls.forEach((control) => {
          const rect = control.getBoundingClientRect();
          if (rect.bottom < -100 || rect.top > innerHeight + 100) return;
          const distance = Math.hypot(
            pointerX - rect.left - rect.width / 2,
            pointerY - rect.top - rect.height / 2,
          );
          const radius = Math.max(86, Math.min(150, Math.max(rect.width, rect.height) * 1.15));
          const proximity = clamp(1 - distance / radius);
          control.style.setProperty('--prox', proximity.toFixed(3));
          control.style.setProperty('--pointer-x', `${clamp((pointerX - rect.left) / rect.width * 100, 0, 100).toFixed(1)}%`);
          control.style.setProperty('--pointer-y', `${clamp((pointerY - rect.top) / rect.height * 100, 0, 100).toFixed(1)}%`);
          control.classList.toggle('is-near', proximity > 0.05);
          if (proximity > 0.05 && distance < nearestDistance) {
            nextNearest = control;
            nearestDistance = distance;
            nearestProximity = proximity;
            nearestRect = rect;
          }
        });

        if (nearest && nearest !== nextNearest) {
          nearest.style.setProperty('--mag-x', '0px');
          nearest.style.setProperty('--mag-y', '0px');
        }
        nearest = nextNearest;
        orbit.classList.toggle('is-near', Boolean(nearest));
        if (nearest && nearestRect) {
          nearest.style.setProperty('--mag-x', `${((pointerX - nearestRect.left - nearestRect.width / 2) * 0.11 * nearestProximity).toFixed(1)}px`);
          nearest.style.setProperty('--mag-y', `${((pointerY - nearestRect.top - nearestRect.height / 2) * 0.13 * nearestProximity).toFixed(1)}px`);
        }

        if (paperHero) {
          const rect = paperHero.getBoundingClientRect();
          if (pointerY >= rect.top && pointerY <= rect.bottom) {
            paperHero.style.setProperty('--stage-x', `${(clamp((pointerX - rect.left) / rect.width - 0.5, -0.5, 0.5) * -18).toFixed(1)}px`);
            paperHero.style.setProperty('--stage-y', `${(clamp((pointerY - rect.top) / rect.height - 0.5, -0.5, 0.5) * -11).toFixed(1)}px`);
          }
        }
      }
      requestAnimationFrame(renderFrame);
    }

    doc.addEventListener('pointermove', (event) => {
      if (event.pointerType === 'touch') return;
      pointerX = event.clientX;
      pointerY = event.clientY;
      dirty = true;
      dot.classList.add('is-visible');
      orbit.classList.add('is-visible');

      const element = event.target instanceof Element ? event.target : null;
      const control = element?.closest('a,button,[data-cursor]');
      dot.classList.toggle('is-active', Boolean(control));
      orbit.classList.toggle('is-active', Boolean(control));
      if (control) {
        const kind = cursorLabel(control);
        label.textContent = kind;
        orbit.dataset.kind = kind.toLowerCase().replace(/[^a-z]/g, '');
      } else {
        delete orbit.dataset.kind;
      }

      const surface = element?.closest('.sequence-row,.metric,.fact,.series-nav a,.author-links a');
      if (surface) {
        const rect = surface.getBoundingClientRect();
        surface.style.setProperty('--pointer-x', `${clamp((pointerX - rect.left) / rect.width * 100, 0, 100).toFixed(1)}%`);
        surface.style.setProperty('--pointer-y', `${clamp((pointerY - rect.top) / rect.height * 100, 0, 100).toFixed(1)}%`);
      }
    }, { passive: true });

    function resetCursor() {
      dot.classList.remove('is-visible');
      orbit.classList.remove('is-visible');
      delete orbit.dataset.kind;
      magneticControls.forEach((control) => {
        control.style.setProperty('--mag-x', '0px');
        control.style.setProperty('--mag-y', '0px');
        control.style.setProperty('--prox', '0');
        control.classList.remove('is-near');
      });
      nearest = null;
    }

    addEventListener('mouseout', (event) => {
      if (!event.relatedTarget) resetCursor();
    });
    addEventListener('blur', resetCursor);
    renderFrame();
  }

  function initScrollState(reduceMotion) {
    const homeHero = doc.querySelector('body[data-page="home"] .hero');
    const footer = doc.querySelector('.site-footer');
    let scheduled = false;

    function update() {
      const maximum = root.scrollHeight - innerHeight;
      root.style.setProperty('--scroll', (maximum ? clamp(scrollY / maximum) : 0).toFixed(4));
      if (homeHero && !reduceMotion) {
        const progress = clamp(scrollY / Math.max(homeHero.offsetHeight * 1.15, innerHeight));
        root.style.setProperty('--home-scroll', progress.toFixed(4));
      }
      if (footer) {
        const ending = clamp(1 - footer.getBoundingClientRect().top / innerHeight);
        root.style.setProperty('--ending', ending.toFixed(4));
        root.classList.toggle('is-ending', ending > 0.48);
      }
    }

    addEventListener('scroll', () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(() => {
        update();
        scheduled = false;
      });
    }, { passive: true });
    addEventListener('resize', () => requestAnimationFrame(update), { passive: true });
    update();
  }

  function initReveal(reduceMotion) {
    const items = [...doc.querySelectorAll('[data-reveal]')];
    if (reduceMotion || !window.IntersectionObserver) {
      items.forEach((item) => item.classList.add('is-visible'));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });
    items.forEach((item) => observer.observe(item));
  }

  function hardenExternalLinks() {
    doc.querySelectorAll('a[target="_blank"]').forEach((anchor) => {
      const rel = new Set((anchor.rel || '').split(/\s+/).filter(Boolean));
      rel.add('noopener');
      rel.add('noreferrer');
      anchor.rel = [...rel].join(' ');
    });
  }

  function initArchive() {
    const reduceMotion = matchMedia('(prefers-reduced-motion:reduce)').matches;
    initScrollState(reduceMotion);
    initReveal(reduceMotion);
    hardenExternalLinks();
    initReadingState();
    initAuthorityCursor(reduceMotion);
    clearTimeout(initializationFallback);
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', initArchive, { once: true });
  } else {
    initArchive();
  }
})();

/* Part I — Typed Gate conceptual probe.
 *
 * This is a research instrument for declared routing semantics, not an
 * operational decision engine. Missing capacity never becomes missing evidence.
 */
(() => {
  'use strict';

  const doc = document;

  function initGateProbe() {
    const root = doc.querySelector('[data-gate-probe]');
    if (!root) return;

    const gates = [...root.querySelectorAll('[data-gate]')];
    const route = root.querySelector('[data-route]');
    const note = root.querySelector('[data-route-note]');
    const routeBox = root.querySelector('.probe-route');
    if (!routeBox || !route || !note) return;

    const inputs = doc.createElement('fieldset');
    inputs.className = 'probe-flags';
    inputs.innerHTML = `
      <legend>Route-local institutional inputs</legend>
      <p>These are separate case-time availability inputs, not substitutes for the three diagnostic gates.</p>
      <div class="probe-flag-grid">
        <button type="button" data-flag="r" aria-pressed="true"><span>Review authority</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="c" aria-pressed="true"><span>Review capacity</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="b" aria-pressed="true"><span>Fallback authorization</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="f" aria-pressed="true"><span>Fallback readiness</span><b>READY</b></button>
      </div>`;
    routeBox.before(inputs);

    const inputButtons = [...inputs.querySelectorAll('button[data-flag]')];

    function gateStates() {
      return gates.map((gate) => (
        gate.querySelector('button[aria-pressed="true"]')?.dataset.state || 'UNKNOWN'
      ));
    }

    function inputAvailable(key) {
      return inputButtons.find((button) => button.dataset.flag === key)
        ?.getAttribute('aria-pressed') === 'true';
    }

    function renderRoute() {
      const states = gateStates();
      const hasUnknown = states.includes('UNKNOWN');
      const hasNonPass = states.some((state) => state === 'REVIEW' || state === 'BLOCK');
      const reviewAuthority = inputAvailable('r');
      const reviewCapacity = inputAvailable('c');
      const fallbackAuthorized = inputAvailable('b');
      const fallbackReady = inputAvailable('f');

      let label;
      let explanation;

      if (states.every((state) => state === 'PASS')) {
        label = 'EXECUTION ELIGIBLE';
        explanation = 'All three diagnostics PASS. This is eligibility to enter the domain-defined execution control, not the execution event itself.';
      } else if (hasUnknown && reviewAuthority && reviewCapacity) {
        label = 'EVIDENCE HOLD';
        explanation = 'UNKNOWN has priority when authorized, resourced review exists: complete required evidence and rerun rather than imputing PASS.';
      } else if (!hasUnknown && hasNonPass && reviewAuthority && reviewCapacity) {
        label = 'AUTHORIZED REVIEW';
        explanation = 'A REVIEW or preliminary BLOCK routes judgment to an authorized, resourced reviewer. The routing status is not a final institutional act.';
      } else if (fallbackAuthorized && fallbackReady) {
        label = 'FALLBACK';
        explanation = 'The required primary evidence/review route is unavailable; fallback is both authorized and operationally ready.';
      } else {
        label = 'UNRESOLVED';
        explanation = 'No permissible operational route exists under the declared inputs. Missing capacity is not missing evidence, and no state is silently converted into approval or denial.';
      }

      route.textContent = label;
      note.textContent = explanation;
      root.dataset.route = label.toLowerCase().replace(/[^a-z]+/g, '-');

      inputButtons.forEach((button) => {
        const enabled = button.getAttribute('aria-pressed') === 'true';
        const output = button.querySelector('b');
        if (!output) return;
        output.textContent = button.dataset.flag === 'f'
          ? (enabled ? 'READY' : 'NOT READY')
          : (enabled ? 'AVAILABLE' : 'UNAVAILABLE');
      });
    }

    root.addEventListener('click', (event) => {
      const stateButton = event.target.closest('button[data-state]');
      if (stateButton && root.contains(stateButton)) {
        const gate = stateButton.closest('[data-gate]');
        gate.querySelectorAll('button[data-state]').forEach((button) => {
          button.setAttribute('aria-pressed', String(button === stateButton));
        });
        renderRoute();
        return;
      }

      const inputButton = event.target.closest('button[data-flag]');
      if (inputButton && root.contains(inputButton)) {
        inputButton.setAttribute(
          'aria-pressed',
          String(inputButton.getAttribute('aria-pressed') !== 'true'),
        );
        renderRoute();
      }
    });

    root.querySelector('[data-probe-reset]')?.addEventListener('click', () => {
      gates.forEach((gate) => {
        gate.querySelectorAll('button[data-state]').forEach((button) => {
          button.setAttribute('aria-pressed', String(button.dataset.state === 'UNKNOWN'));
        });
      });
      inputButtons.forEach((button) => button.setAttribute('aria-pressed', 'true'));
      renderRoute();
    });

    renderRoute();
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', initGateProbe, { once: true });
  } else {
    initGateProbe();
  }
})();


(function () {
  'use strict';

  const win = window;
  const doc = document;

  function cleanText(value) {
    return (value || '').replace(/\s+/g, ' ').trim().slice(0, 120);
  }

  function pageId() {
    return doc.body?.dataset?.page || location.pathname.replace(/^\/|\/$/g, '') || 'home';
  }

  function linkKind(url) {
    const path = url.pathname.toLowerCase();
    const host = url.hostname.toLowerCase();
    if (path.endsWith('.pdf')) return 'pdf';
    if (host.includes('ssrn.com')) return 'ssrn';
    if (host.includes('doi.org')) return 'doi';
    if (host.includes('orcid.org')) return 'orcid';
    if (host.includes('scholar.google')) return 'scholar';
    if (path.startsWith('/papers/')) return 'paper';
    if (path === '/' || path === '') return 'home';
    if (url.protocol === 'mailto:') return 'email';
    return url.origin === location.origin ? 'internal' : 'external';
  }

  function emit(name, detail) {
    const payload = {
      page_id: pageId(),
      page_path: location.pathname,
      page_title: doc.title,
      ...detail,
    };
    win.dispatchEvent(new CustomEvent('site-analytics:event', {
      detail: { name, payload },
    }));
    if (typeof win.gtag === 'function') win.gtag('event', name, payload);
    if (typeof win.plausible === 'function') win.plausible(name, { props: payload });
  }

  doc.addEventListener('click', function (event) {
    const anchor = event.target.closest?.('a[href]');
    if (!anchor) return;
    const href = anchor.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
    const url = new URL(href, location.href);
    emit('link_open', {
      link_kind: linkKind(url),
      link_url: url.href,
      link_text: cleanText(anchor.textContent || anchor.getAttribute('aria-label')),
      outbound: url.origin !== location.origin,
    });
  }, { capture: true });

  win.takashisatoTrack = emit;
  emit('page_view', {});
})();
