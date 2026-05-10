(() => {
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) {
    document.documentElement.classList.add("motion-reduced");
    return;
  }

  document.documentElement.classList.add("motion-safe");

  const isModifiedClick = (event) =>
    event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0;

  const shouldBypass = (anchor) => {
    if (!anchor || anchor.target || anchor.hasAttribute("download")) return true;
    const raw = anchor.getAttribute("href") || "";
    if (!raw || raw.startsWith("#") || raw.startsWith("mailto:") || raw.startsWith("tel:")) return true;
    const url = new URL(raw, window.location.href);
    if (url.origin !== window.location.origin) return true;
    if (url.pathname === window.location.pathname && url.hash) return true;
    return false;
  };

  window.addEventListener("pageshow", () => {
    document.body.classList.remove("page-exit");
    document.body.classList.add("page-ready");
  });

  document.addEventListener("click", (event) => {
    if (isModifiedClick(event)) return;
    const anchor = event.target.closest && event.target.closest("a[href]");
    if (shouldBypass(anchor)) return;

    event.preventDefault();
    document.body.classList.add("page-exit");

    window.setTimeout(() => {
      window.location.href = anchor.href;
    }, 180);
  });
})();