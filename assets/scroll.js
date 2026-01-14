/* assets/scroll.js — Elegant Reveal */

document.addEventListener("DOMContentLoaded", () => {
  
  // 監視対象：見出し、カード、引用など
  const targets = document.querySelectorAll('h1, .who, .lead, .meta, .paper, .fragment, footer');
  
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // 表示範囲に入ったらクラス付与
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, {
    root: null,
    threshold: 0.05, // 少しでも見えたら開始
    rootMargin: "0px 0px -50px 0px" // 画面の下の方で発火
  });

  targets.forEach((el, index) => {
    // 初期状態（透明）にするクラスを追加
    el.classList.add('fade-in');
    
    // 順番に表示させるための遅延（Stagger Effect）をCSS変数で渡すか、JSで制御
    // ここではシンプルにCSS transitionに任せる
    observer.observe(el);
  });
});
