document.addEventListener("DOMContentLoaded", () => {
  
  // 1. Text Splitter for "Redaction" effect
  // 対象の要素をラップして、アニメーション用のクラスを付与する準備
  const revealElements = document.querySelectorAll('h1, .lead, .paper-title');
  
  revealElements.forEach(el => {
    el.classList.add('reveal-text');
  });

  // 2. Intersection Observer (The Unveiling)
  const observerOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -10% 0px"
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // 遅延を入れて、順次「黒塗り」が剥がれるようにする
        setTimeout(() => {
          entry.target.classList.add('is-visible');
        }, 100);
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.reveal-text, .paper, .who').forEach(el => {
    observer.observe(el);
  });

  // 3. Custom Cursor Logic (Optional but recommended for brutalism)
  // カーソル付近のグリッドを少し歪ませるなどの高度な処理はここに入るが、
  // 今回はCSSの cursor: crosshair で世界観を作っているので、過度なJSは不要。
});
