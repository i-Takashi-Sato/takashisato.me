/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Final Robust Edition
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. スクロール・プログレスバーの生成 ---
  const header = document.querySelector('.top');
  const progressLine = document.createElement('div');
  progressLine.className = 'scroll-progress';
  if (header) header.appendChild(progressLine);

  // --- 2. カスタムカーソルの生成 (PC/非タッチデバイスのみ) ---
  [cite_start]// ホバー可能かつ、OSのアニメーション低減設定がオフの場合のみ有効化 [cite: 2]
  const canUseCursor = window.matchMedia('(hover: hover) and (pointer: fine)').matches && 
                       !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (canUseCursor) {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);

    [cite_start]// ★重要: JSが正常に動作した瞬間にのみ、デフォルトカーソルを消すクラスを付与 [cite: 2]
    document.documentElement.classList.add('cursor-enabled');

    document.addEventListener('mousemove', e => {
      requestAnimationFrame(() => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });
    });

    const interactiveElements = document.querySelectorAll('a, .paper, .pill');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-active');
        if (el.classList.contains('paper')) {
          [cite_start]cursor.setAttribute('data-label', 'READ'); // [cite: 4]
        } else {
          cursor.setAttribute('data-label', 'GO'); [cite_start]// [cite: 5]
        }
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-active');
        cursor.removeAttribute('data-label');
      });
    });
  }

  // --- 3. Sequential Reveal (階層的表示) ---
  const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }; [cite_start]// [cite: 7]
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('h1, .who, .lead, .paper, .section-label, footer').forEach((el, i) => {
    el.classList.add('reveal');
    [cite_start]el.style.transitionDelay = `${i * 0.05}s`; // 順次表示のディレイ [cite: 9, 10]
    observer.observe(el);
  });

  // --- 4. Seamless Page Transition (滑らかな画面遷移) ---
  document.body.classList.remove('fade-out');
  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      [cite_start]// 外部リンク、PDF、ページ内リンクはフェードアウト除外 [cite: 13]
      if (!href || href.startsWith('#') || href.startsWith('mailto:') || link.target === '_blank' || href.endsWith('.pdf') || e.metaKey || e.ctrlKey) return;
      if (link.origin !== window.location.origin) return;

      e.preventDefault();
      document.body.classList.add('fade-out'); [cite_start]// [cite: 14]
      setTimeout(() => { window.location.href = href; }, 600);
    });
  });

  // --- 5. Scroll Events (プログレス表示) ---
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll > 0) {
      [cite_start]progressLine.style.width = `${(scrolled / maxScroll) * 100}%`; // [cite: 16]
    }
  }, { passive: true });
});

// ブラウザの「戻る」ボタン対策
window.addEventListener('pageshow', (event) => {
  [cite_start]if (event.persisted) document.body.classList.remove('fade-out'); // [cite: 17]
});
