/**
 * Takashi Sato · Interaction Engine v3.0
 * Refined for Academic Trust and Global Standards
 */

document.addEventListener("DOMContentLoaded", () => {
  const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- 1. Sequential Reveal ---
  if (!isReducedMotion) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

    // Target mapping without inline delays
    document.querySelectorAll('.hero > *, .paper, footer').forEach((el, i) => {
      el.classList.add('reveal');
      // Using CSS Classes for delays would be P1, for now keeping logic clean
      el.style.setProperty('--delay', `${i * 0.1}s`); 
      observer.observe(el);
    });
  }

  // --- 2. Scoped Transitions ---
  const handleTransition = (e) => {
    const link = e.currentTarget;
    const isInternal = link.hostname === window.location.hostname;
    const isSamePage = link.pathname === window.location.pathname;
    const isHash = link.hash !== "";

    if (isInternal && !link.target && !isHash && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
      document.body.classList.add('fade-out');
      setTimeout(() => { window.location.href = link.href; }, 600);
    }
  };

  // Only apply to actual page links, avoiding anchors and external
  document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- 3. Progress Line ---
  const progressLine = document.querySelector('.scroll-progress');
  if (progressLine) {
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll > 0) {
        progressLine.style.width = `${(scrolled / maxScroll) * 100}%`;
      }
    }, { passive: true });
  }
});
