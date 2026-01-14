/**
 * Takashi Sato · Research Archive System
 * Interaction Engine v3.1 (Stability & Precision Edition)
 * Sequential Reveal | Seamless Transition | Custom Cursor | Progress Line
 */

document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;

  // --- ① ブラウザバック時の「真っ暗画面」を防止 ---
  // bfcache（ブラウザの戻る/進むキャッシュ）から復帰した際にフェードアウトを解除する
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
      body.classList.remove('fade-out');
    }
  });

  // --- ② カスタムカーソル (PC/非タッチデバイスのみ) ---
  if (!('ontouchstart' in window)) {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    body.appendChild(cursor);

    document.addEventListener('mousemove', e => {
      // requestAnimationFrameで描画を最適化（高リフレッシュレート対応）
      requestAnimationFrame(() => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });
    });

    // 拡大インタラクションは「論文カード（.paper）」のみに限定
    // リード文やその他の要素では拡大（READラベル表示）は行わない
    document.querySelectorAll('.paper').forEach(card => {
      card.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-active');
        cursor.setAttribute('data-label', 'READ');
      });
      card.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-active');
        cursor.removeAttribute('data-label');
      });
    });
  }

  // --- ③ Sequential Reveal (階層的表示) ---
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

  // ヒーロー、論文、フッターを順番に出現させる
  document.querySelectorAll('h1, .who, .lead, .paper, .section-label, footer').forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${i * 0.15}s`;
    observer.observe(el);
  });

  // --- ④ Seamless Page Transition (滑らかな画面遷移) ---
  const handleTransition = (e) => {
    const link = e.currentTarget;
    // 内部リンクかつ target="_blank" でない場合、かつアンカーリンクでない場合のみ
    if (link.hostname === window.location.hostname && !link.target && !link.hash && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
      const destination = link.href;
      
      // 画面を暗転（CSSで定義された transition が作動）
      body.classList.add('fade-out');
      
      // アニメーション完了後に遷移
      setTimeout(() => {
        window.location.href = destination;
      }, 600);
    }
  };

  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', handleTransition);
  });

  // --- ⑤ Scroll Events (プログレスバー) ---
  const progressLine = document.querySelector('.scroll-progress');
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    
    // プログレスバー（1px）の計算
    if (maxScroll > 0 && progressLine) {
      const scrollPercent = (scrolled / maxScroll) * 100;
      progressLine.style.width = `${scrollPercent}%`;
    }

    // 背景ノイズのパララックス
    body.style.backgroundPositionY = `${scrolled * 0.08}px`;
  }, { passive: true });
});
