/* assets/scroll.js */

document.addEventListener("DOMContentLoaded", () => {
  
  // 1. Mouse tracking for card borders
  const cards = document.querySelectorAll('.paper');

  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      card.style.setProperty('--lx', `${x}px`);
      card.style.setProperty('--ly', `${y}px`);
    });
  });

  // 2. Scroll Reveal Animation
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

  const targets = document.querySelectorAll('h1, .who, .lead, .paper, footer');
  targets.forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${i * 0.05}s`;
    observer.observe(el);
  });
});
