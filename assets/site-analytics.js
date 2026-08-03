(function () {
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
    if (host.includes('orcid.org')) return 'orcid';
    if (path.startsWith('/demo/')) return 'visualizer';
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

    if (typeof win.gtag === 'function') {
      win.gtag('event', name, payload);
    }

    if (typeof win.plausible === 'function') {
      win.plausible(name, { props: payload });
    }
  }

  function trackLink(anchor) {
    const href = anchor.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

    const url = new URL(href, location.href);
    const kind = linkKind(url);
    emit('link_open', {
      link_kind: kind,
      link_url: url.href,
      link_text: cleanText(anchor.textContent || anchor.getAttribute('aria-label')),
      outbound: url.origin !== location.origin,
    });
  }

  doc.addEventListener('click', function (event) {
    const anchor = event.target.closest?.('a[href]');
    if (!anchor) return;
    trackLink(anchor);
  }, { capture: true });

  win.takashisatoTrack = emit;
  emit('page_view', {});
})();
