/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Award-Winning Edition
 * Sequential Reveal | Seamless Transition | Custom Cursor | Progress Line
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. スクロール・プログレスバーの生成 ---
  const header = document.querySelector('.top');
  const progressLine = document.createElement('div');
  progressLine.className = 'scroll-progress';
  if (header) header.appendChild(progressLine);

  // --- 2. カスタムカーソルの生成 (PC/非タッチデバイスのみ) ---
  if (!('ontouchstart' in window)) {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);

    document.addEventListener('mousemove', e => {
      requestAnimationFrame(() => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });
    });

    // --- 修正: .paperだけでなく、すべてのリンク(a, .pill)にも反応させる ---
    const interactiveElements = document.querySelectorAll('a, .paper, .pill');

    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-active');
        
        // 要素の種類によってラベルを変える
        if (el.classList.contains('paper')) {
          cursor.setAttribute('data-label', 'READ');
        } else {
          cursor.setAttribute('data-label', 'GO'); // リンク用ラベル
        }
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-active');
        cursor.removeAttribute('data-label');
      });
    });
  }

  // --- 3. Sequential Reveal (階層的表示) ---
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

  // --- 4. Seamless Page Transition (滑らかな画面遷移) ---
  const handleTransition = (e) => {
    const link = e.currentTarget;
    if (link.hostname === window.location.hostname && !link.target && !e.metaKey && !e.ctrlKey) {
      if (link.getAttribute('href').startsWith('#')) return; // ページ内リンクは除外
      e.preventDefault();
      const destination = link.href;
      document.body.classList.add('fade-out');
      setTimeout(() => { window.location.href = destination; }, 600);
    }
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- 5. Scroll Events (プログレス & パララックス) ---
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    
    // プログレスバーの計算
    if (maxScroll > 0) {
      const scrollPercent = (scrolled / maxScroll) * 100;
      progressLine.style.width = `${scrollPercent}%`;
    }

    // 背景ノイズのパララックス
    document.body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
