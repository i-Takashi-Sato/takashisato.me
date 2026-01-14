/* assets/scroll.js — Linear Glow Engine */

document.addEventListener("DOMContentLoaded", () => {
  
  // 1. マウス連動ボーダー (Glow Effect)
  const cards = document.querySelectorAll('.paper');

  // カードの上でマウスが動いた時だけ計算する（パフォーマンス重視）
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      // カードの左上を原点(0,0)としたマウス座標を計算
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // CSS変数に渡す
      card.style.setProperty('--lx', `${x}px`);
      card.style.setProperty('--ly', `${y}px`);
    });
  });

  // 2. 出現アニメーション (Fade In)
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
    // 少しずつ遅れて出現させる
    el.style.transitionDelay = `${i * 0.05}s`;
    observer.observe(el);
  });
});
