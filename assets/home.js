(() => {
  const cards = [...document.querySelectorAll(".v4-card")];
  if (!cards.length) return;

  const isInteractive = (t) => !!t.closest("a,button,input,select,textarea,[role='button']");

  for (const el of cards) {
    el.addEventListener("click", (e) => {
      if (isInteractive(e.target)) return;
      const href = el.getAttribute("data-href");
      if (href) window.location.href = href;
    });

    el.addEventListener("keydown", (e) => {
      if (isInteractive(e.target)) return;
      if (e.key === "Enter" || e.key === " ") {
        const href = el.getAttribute("data-href");
        if (!href) return;
        e.preventDefault();
        window.location.href = href;
      }
    });
  }
})();
