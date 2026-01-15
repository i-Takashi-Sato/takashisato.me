/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Final World-Class Edition
 * Includes: Plasma Beam, Custom Cursor, Indigo Shutter, Data Scramble, Sequential Reveal
 */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. Plasma Beam (Scroll Progress) ---
  // HTML側に既に要素がある場合は取得、なければ生成（安全策）
  let progressLine = document.querySelector('.scroll-progress');
  if (!progressLine) {
    const header = document.querySelector('.top');
    if (header) {
      progressLine = document.createElement('div');
      progressLine.className = 'scroll-progress';
      header.appendChild(progressLine);
    }
  }

  // --- 2. Custom Cursor (PC/非タッチデバイスのみ) ---
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    let cursor = document.querySelector('.custom-cursor');
    if (!cursor) {
      cursor = document.createElement('div');
      cursor.className = 'custom-cursor';
      document.body.appendChild(cursor);
    }

    document.addEventListener('mousemove', e => {
      // requestAnimationFrameで滑らかに追従
      requestAnimationFrame(() => {
        cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
        // 中心座標を合わせるためのCSS側 translate(-50%, -50%) と競合しないよう注意
        // CSS側で transform: translate(-50%, -50%) がある場合、JSでは left/top を操作する方が安全だが
        // ここではCSSのtransformを上書きするため、CSS側の .custom-cursor に `left: 0; top: 0;` を前提として
        // `style.left`, `style.top` で制御する方式に変更します（安定性重視）
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
        cursor.style.transform = 'translate(-50%, -50%)'; // 常に中心配置
      });
    });

    // インタラクティブ要素への反応
    const interactiveElements = document.querySelectorAll('a, .paper, .pill, .scramble-effect');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('cursor-active'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('cursor-active'));
    });
  }

  // --- 3. Sequential Reveal (階層的表示) ---
  const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -50px 0px" };
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // 監視対象の追加
  document.querySelectorAll('h1, .who, .lead, .paper, .section-label, footer').forEach((el, i) => {
    el.classList.add('reveal');
    // 順番に遅延させる（簡易的な千鳥配置）
    el.style.transitionDelay = `${i * 0.05}s`; 
    observer.observe(el);
  });

  // --- 4. Indigo Shutter (Page Transition) ---
  // ページ読み込み完了時: 幕を開ける
  document.body.classList.add('is-loaded');

  const handleTransition = (e) => {
    const link = e.currentTarget;
    const href = link.getAttribute('href');

    // 除外条件: 外部リンク、PDF、ページ内リンク、Modifierキー押し
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || link.target === '_blank' || href.endsWith('.pdf') || e.metaKey || e.ctrlKey) return;
    
    // 異なるオリジン（ドメイン）へのリンクも除外
    if (link.origin !== window.location.origin) return;

    e.preventDefault();
    
    // 幕を閉じる (is-loadedを消し、is-leavingを付与)
    document.body.classList.remove('is-loaded');
    document.body.classList.add('is-leaving');

    // アニメーション完了後に遷移 (0.5s)
    setTimeout(() => { window.location.href = href; }, 500);
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- 5. Data Scramble (Hacker Text Effect) ---
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";
  const headers = document.querySelectorAll(".scramble-effect");

  headers.forEach(header => {
    header.addEventListener("mouseover", event => {
      let iteration = 0;
      clearInterval(header.interval);

      header.interval = setInterval(() => {
        event.target.innerText = event.target.innerText
          .split("")
          .map((letter, index) => {
            if (index < iteration) {
              return event.target.dataset.value[index];
            }
            return letters[Math.floor(Math.random() * letters.length)];
          })
          .join("");

        if (iteration >= event.target.dataset.value.length) { 
          clearInterval(header.interval);
        }
        
        iteration += 1 / 3; 
      }, 30);
    });
  });

  // --- 6. Scroll Events (Update Plasma Beam) ---
  window.addEventListener('scroll', () => {
    if (!progressLine) return;
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
    const clientHeight = document.documentElement.clientHeight || document.body.clientHeight;
    
    const scrolled = (scrollTop / (scrollHeight - clientHeight)) * 100;
    progressLine.style.width = `${scrolled}%`;
  }, { passive: true });

});

// --- 7. BFCache Fix (ブラウザの戻るボタン対策) ---
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    document.body.classList.remove('is-leaving');
    document.body.classList.add('is-loaded');
  }
});
