/* assets/scroll.js — The Monolith Progress Bar */

document.addEventListener("DOMContentLoaded", () => {
  // プログレスバーの要素を作成して挿入
  const bar = document.createElement('div');
  bar.id = 'monolith-progress';
  Object.assign(bar.style, {
    position: 'fixed',
    top: '0',
    left: '0',
    height: '4px', // 少し太く
    width: '0%',
    background: '#ff0000', // 警告色
    zIndex: '9999',
    transition: 'width 0.1s linear' // 機械的な動き
  });
  document.body.prepend(bar);

  // スクロール監視
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    const max = document.body.scrollHeight - window.innerHeight;
    const progress = (scrolled / max) * 100;
    bar.style.width = `${progress}%`;
  }, { passive: true });
  
  // 以前のScroll Reveal用の初期化スタイルがあれば解除（念の為）
  document.querySelectorAll('.paper, footer, .hero').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
  });
});
