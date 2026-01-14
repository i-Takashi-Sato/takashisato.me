/**
 * Takashi Sato · Research Archive System
 * Interaction Engine v3.2
 */

document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;

  // --- ⑤ ブラウザバック時の不具合修正 ---
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
      body.classList.remove('fade-out');
    }
  });

  // --- ⑤ カスタムカーソル (静的なドットのみ) ---
  if (!('ontouchstart' in window)) {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    body.appendChild(cursor);

    document.addEventListener('mousemove', e => {
      requestAnimationFrame(() => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });
    });
  }

  // --- 出現アニメーション ---
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.hero > *, .paper, footer').forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${i * 0.1}s`;
    observer.observe(el);
  });

  // --- ページ遷移 ---
  document.querySelectorAll('a:not([target="_blank"]):not([href^="#"])').forEach(link => {
    link.addEventListener('click', e => {
      if (link.hostname === window.location.hostname) {
        e.preventDefault();
        body.classList.add('fade-out');
        setTimeout(() => { window.location.href = link.href; }, 600);
      }
    });
  });

  // --- ① 1px プログレスバー & パララックス ---
  const progressLine = document.querySelector('.scroll-progress');
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll > 0 && progressLine) {
      progressLine.style.width = `${(scrolled / maxScroll) * 100}%`;
    }
    body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
