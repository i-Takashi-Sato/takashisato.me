/* assets/scroll.js — Kinetic Engine */

document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  
  // 1. マウス追従ライト (Lighting Logic)
  // パフォーマンス重視で requestAnimationFrame を使用
  let mouseX = 0, mouseY = 0;
  let currentX = 0, currentY = 0;
  
  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animateLight() {
    // 慣性をつけて遅れてついてくる演出 (Lerp)
    currentX += (mouseX - currentX) * 0.1;
    currentY += (mouseY - currentY) * 0.1;
    
    root.style.setProperty('--mouse-x', `${currentX}px`);
    root.style.setProperty('--mouse-y', `${currentY}px`);
    
    requestAnimationFrame(animateLight);
  }
  animateLight();

  // 2. スクロール連動の出現アニメーション (Observer)
  const targets = document.querySelectorAll('.hero, .paper, .section-label, footer');
  
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.05, rootMargin: "0px 0px -10% 0px" });

  targets.forEach((el, i) => {
    el.classList.add('reveal');
    // 少し遅延をつける
    el.style.transitionDelay = `${i * 0.05}s`;
    observer.observe(el);
  });
});
