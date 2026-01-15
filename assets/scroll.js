/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Stable Production Edition
 * Progress Bar | Sequential Reveal | Seamless Transition
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. スクロール・プログレスバーの生成 ---
  const header = document.querySelector('.top');
  const progressLine = document.createElement('div');
  progressLine.className = 'scroll-progress';
  if (header) header.appendChild(progressLine); [cite: 99]

  // --- 2. Sequential Reveal (階層的表示) ---
  // インラインスタイルを排除し、クラスの付与のみに徹する設計 [cite: 105]
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Reveal対象をまとめて登録（遅延はCSS側で制御）
  document.querySelectorAll('h1, .who, .lead, .paper, .section-label, footer').forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  }); [cite: 106-108]

  // --- 3. Seamless Page Transition (滑らかな画面遷移) ---
  document.body.classList.remove('fade-out');
  
  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');

      // 遷移アニメーションを除外する条件（外部リンク、PDF、ページ内リンク、メール） 
      if (!href || 
          href.startsWith('#') || 
          href.startsWith('mailto:') || 
          link.target === '_blank' || 
          href.endsWith('.pdf') || 
          e.metaKey || e.ctrlKey) return;

      if (link.origin !== window.location.origin) return;

      e.preventDefault();
      document.body.classList.add('fade-out');
      const destination = link.href;
      setTimeout(() => { window.location.href = destination; }, 600); [cite: 111]
    });
  });

  // --- 4. Scroll Events (プログレス表示) ---
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    
    if (maxScroll > 0) {
      progressLine.style.width = `${(scrolled / maxScroll) * 100}%`;
    }
  }, { passive: true }); [cite: 113]
});

// --- ブラウザの「戻る」ボタン対策 ---
window.addEventListener('pageshow', (event) => {
  if (event.persisted || document.body.classList.contains('fade-out')) {
    document.body.classList.remove('fade-out');
  }
}); [cite: 114]
