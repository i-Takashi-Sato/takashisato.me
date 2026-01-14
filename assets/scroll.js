document.addEventListener("DOMContentLoaded", () => {
  
  // Luxury Reveal: Slow and Deliberate
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px" // 少し早めに表示開始
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // 対象要素を監視
  const targets = document.querySelectorAll('h1, .who, .lead, .paper, footer');
  targets.forEach((el, i) => {
    el.classList.add('reveal');
    // 遅延を少し長めにして、順番に現れる「儀式感」を出す
    el.style.transitionDelay = `${i * 0.1}s`;
    observer.observe(el);
  });
});
