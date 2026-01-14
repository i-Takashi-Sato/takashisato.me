/* assets/scroll.js — Linear-style Spotlight Effect */

document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const cards = document.querySelectorAll('.paper');

  // 1. グローバルなマウス追従 (背景のスポットライト用)
  window.addEventListener('mousemove', (e) => {
    const x = e.clientX;
    const y = e.clientY;
    
    // CSS変数にマウス座標をセット
    body.style.setProperty('--x', `${x}px`);
    body.style.setProperty('--y', `${y}px`);
    
    // 2. カードごとのローカル座標計算 (境界線の発光用)
    cards.forEach(card => {
      const rect = card.getBoundingClientRect();
      const localX = x - rect.left;
      const localY = y - rect.top;
      
      card.style.setProperty('--local-x', `${localX}px`);
      card.style.setProperty('--local-y', `${localY}px`);
    });
  }, { passive: true });

  // 3. スクロール時のフワッとした表示 (Scroll Reveal)
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  // カードなどを初期状態で隠す
  const targets = document.querySelectorAll('.paper, footer, .entry-note');
  targets.forEach((el, index) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(40px)';
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    // 少しずつずらす
    el.style.transitionDelay = `${index * 0.1}s`;
    observer.observe(el);
  });
});
