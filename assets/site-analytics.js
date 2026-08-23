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
