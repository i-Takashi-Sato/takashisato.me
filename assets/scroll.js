document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector('.top');
  const progressLine = document.createElement('div');
  progressLine.className = 'scroll-progress';
  if (header) header.appendChild(progressLine);

  if (!('ontouchstart' in window)) {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);

    document.addEventListener('mousemove', e => {
      requestAnimationFrame(() => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });
    });

    // すべてのリンク（aタグ）と論文カード、ボタンを反応対象にする
    const interactiveElements = document.querySelectorAll('a, .paper, .pill');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-active');
        if (el.classList.contains('paper')) {
          cursor.setAttribute('data-label', 'READ');
        } else {
          cursor.setAttribute('data-label', 'GO');
        }
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-active');
        cursor.removeAttribute('data-label');
      });
    });
  }

  const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -80px 0px" };
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('h1, .who, .lead').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-hero');
    el.style.transitionDelay = `${0.3 + (i * 0.25)}s`;
    observer.observe(el);
  });

  document.querySelectorAll('.paper').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-card');
    el.style.transitionDelay = `${0.1 + (i * 0.15)}s`;
    observer.observe(el);
  });

  document.querySelectorAll('.section-label, footer').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });

  const handleTransition = (e) => {
    const link = e.currentTarget;
    if (link.hostname === window.location.hostname && !link.target && !e.metaKey && !e.ctrlKey) {
      if (link.getAttribute('href').startsWith('#')) return; 
      e.preventDefault();
      const destination = link.href;
      document.body.classList.add('fade-out');
      setTimeout(() => { window.location.href = destination; }, 600);
    }
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll > 0) {
      const scrollPercent = (scrolled / maxScroll) * 100;
      progressLine.style.width = `${scrollPercent}%`;
    }
    document.body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
