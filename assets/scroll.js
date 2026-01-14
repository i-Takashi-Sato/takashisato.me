/**
 * Takashi Sato · Research Archive System
 * High-End Interaction Engine v2.0
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. Sequential Reveal (階層的表示) ---
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -80px 0px" // 少し早めに読み込みを開始
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // A. Hero Section: ゆっくりと、沈み込むような重厚な登場
  document.querySelectorAll('h1, .who, .lead').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-hero');
    el.style.transitionDelay = `${0.3 + (i * 0.25)}s`;
    observer.observe(el);
  });

  // B. Research Cards: リストとしてのスキャン感を出すテンポの良い登場
  document.querySelectorAll('.paper').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-card');
    el.style.transitionDelay = `${0.1 + (i * 0.15)}s`;
    observer.observe(el);
  });

  // C. Essential Elements: フッターやラベル
  document.querySelectorAll('.section-label, footer').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });

  // --- 2. Seamless Page Transition (滑らかな画面遷移) ---
  const handleTransition = (e) => {
    const link = e.currentTarget;
    // 内部リンクかつ target="_blank" でない場合のみ適用
    if (link.hostname === window.location.hostname && !link.target && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
      const destination = link.href;
      
      // 画面をズームアウトしながらフェードアウト
      document.body.classList.add('fade-out');
      
      setTimeout(() => {
        window.location.href = destination;
      }, 600); // CSSのアニメーション時間と同期
    }
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- 3. Intelligent Micro-Parallax (微細なパララックス) ---
  // 背景のノイズ粒子をスクロールに合わせてわずかに動かし、奥行きを出す
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    document.body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
