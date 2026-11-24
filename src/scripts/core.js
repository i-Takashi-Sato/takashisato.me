/* The Proper Ending Index — progressive enhancement.
 *
 * The document is complete before this script runs. JavaScript only adds
 * orientation, research-state motion fallbacks, and terminal settling.
 */
(() => {
  'use strict';

  const doc = document;
  const root = doc.documentElement;
  const desktopPaper = matchMedia('(min-width:44.01rem)');
  const reducedMotion = matchMedia('(prefers-reduced-motion:reduce)');
  const nativeScrollTimeline = Boolean(
    window.CSS?.supports?.('animation-timeline: scroll()'),
  );

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
        .sort((a, b) => (
          Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top)
        ));
      if (visible[0]) setCurrent(visible[0].target);
    }, {
      rootMargin: '-18% 0px -66% 0px',
      threshold: [0, 0.08, 0.2],
    });

    sections.forEach((section) => observer.observe(section));
    setCurrent(sections[0]);
  }

  function initScrollState(reduceMotion) {
    const homeHero = doc.querySelector('body[data-page="home"] .hero');
    const paperHero = doc.querySelector('.paper-hero');
    const apparatus = paperHero?.querySelector('.paper-apparatus');
    const paperTone = doc.body?.dataset?.tone || '';
    const footer = doc.querySelector('.site-footer');
    let scheduled = false;

    function clearPaperFallback() {
      if (!apparatus) return;
      apparatus.style.removeProperty('--trace-a');
      apparatus.style.removeProperty('--trace-b');
      apparatus.style.removeProperty('--trace-c');
      apparatus.style.removeProperty('--capacity-opacity');
      apparatus.style.removeProperty('--closure-scale');
      apparatus.style.removeProperty('--closure-opacity');
      apparatus.style.removeProperty('transform');
    }

    function updatePaperMechanism() {
      if (
        !paperHero
        || !apparatus
        || reduceMotion
        || !desktopPaper.matches
        || nativeScrollTimeline
      ) {
        clearPaperFallback();
        return;
      }

      const travel = Math.max(paperHero.offsetHeight * 0.82, innerHeight * 0.72);
      const progress = clamp(scrollY / travel);

      // Part I remains fixed: measurement depends on a stable datum.
      if (paperTone === 'part-2') {
        // Only the internal traces drift; the procedural frame itself stays fixed.
        apparatus.style.setProperty('--trace-a', `${(progress * 10).toFixed(2)}px`);
        apparatus.style.setProperty('--trace-b', `${(progress * -6).toFixed(2)}px`);
        apparatus.style.setProperty('--trace-c', `${(progress * 4).toFixed(2)}px`);
        apparatus.style.setProperty('--capacity-opacity', (1 - progress * 0.14).toFixed(4));
      } else if (paperTone === 'part-3') {
        // Accountable exit contracts rather than expands: motion spends energy.
        apparatus.style.setProperty('--closure-scale', (1 - progress * 0.12).toFixed(4));
        apparatus.style.setProperty('--closure-opacity', (0.74 - progress * 0.20).toFixed(4));
      } else {
        clearPaperFallback();
      }
    }

    function update() {
      const maximum = root.scrollHeight - innerHeight;
      root.style.setProperty('--scroll', (maximum ? clamp(scrollY / maximum) : 0).toFixed(4));

      if (homeHero && !reduceMotion) {
        const progress = clamp(scrollY / Math.max(homeHero.offsetHeight * 1.15, innerHeight));
        root.style.setProperty('--home-scroll', progress.toFixed(4));
      }

      updatePaperMechanism();

      if (footer) {
        const footerRect = footer.getBoundingClientRect();
        const terminalTravel = Math.max(1, Math.min(innerHeight, footerRect.height));
        const ending = clamp((innerHeight - footerRect.top) / terminalTravel);
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
    }, {
      rootMargin: '0px 0px -9% 0px',
      threshold: 0.08,
    });

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

  function initCitationCopy() {
    const citation = doc.querySelector('#citation .citation');
    const actions = doc.querySelector('#citation .paper-actions');
    if (!citation || !actions || !navigator.clipboard?.writeText) return;
    const button = doc.createElement('button');
    button.type = 'button';
    button.className = 'button';
    button.textContent = 'Copy citation';
    button.dataset.citationCopy = '';
    const status = doc.createElement('span');
    status.setAttribute('role', 'status');
    status.className = 'sr-only';
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(citation.textContent.trim());
        button.textContent = 'Citation copied';
        status.textContent = 'Citation copied to clipboard.';
      } catch {
        const selection = window.getSelection();
        if (selection) {
          const range = doc.createRange();
          range.selectNodeContents(citation);
          selection.removeAllRanges();
          selection.addRange(range);
          status.textContent = 'Citation selected. Copy it manually.';
        } else {
          status.textContent = 'Copy unavailable. Select the citation manually.';
        }
        button.textContent = 'Copy citation';
      }
    });
    actions.prepend(button);
    actions.append(status);
  }

  function initArchive() {
    const reduceMotion = reducedMotion.matches;
    initScrollState(reduceMotion);
    initReveal(reduceMotion);
    hardenExternalLinks();
    initReadingState();
    initCitationCopy();
    clearTimeout(initializationFallback);
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', initArchive, { once: true });
  } else {
    initArchive();
  }
})();
