/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Sequential & Seamless
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. Sequential Reveal (階層的表示) ---
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -80px 0px"
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // A. Hero要素: 重厚にゆっくりと登場
  document.querySelectorAll('h1, .who, .lead').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-hero');
    el.style.transitionDelay = `${0.3 + (i * 0.25)}s`;
    observer.observe(el);
  });

  // B. 論文カード: テンポよくリストアップ
  document.querySelectorAll('.paper').forEach((el, i) => {
    el.classList.add('reveal', 'reveal-card');
    el.style.transitionDelay = `${0.1 + (i * 0.15)}s`;
    observer.observe(el);
  });

  // C. ラベル・フッター
  document.querySelectorAll('.section-label, footer').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });

  // --- 2. Seamless Page Transition (滑らかな画面遷移) ---
  const handleTransition = (e) => {
    const link = e.currentTarget;
    // 内部リンクかつ target="_blank" でない場合
    if (link.hostname === window.location.hostname && !link.target && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
      const destination = link.href;
      
      document.body.classList.add('fade-out'); // 暗転開始
      
      setTimeout(() => {
        window.location.href = destination;
      }, 600); // CSSアニメーションと同期
    }
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- 3. Intelligent Micro-Parallax (奥行きの演出) ---
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    // 背景ノイズをわずかに動かして奥行きを出す
    document.body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
