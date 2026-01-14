document.addEventListener("DOMContentLoaded", () => {
  
  // Platinum Reveal: Slow, Deliberate, and Elegant
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // 監視対象：見出し、リード文、論文カード、フッター
  const targets = document.querySelectorAll('h1, .who, .lead, .paper, footer');
  
  targets.forEach((el, i) => {
    el.classList.add('reveal');
    // 遅延をかけて、一つずつ順番に表示させる（儀式感）
    el.style.transitionDelay = `${i * 0.1}s`;
    observer.observe(el);
  });
});
