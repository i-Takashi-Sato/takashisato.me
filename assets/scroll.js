/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Stable Production Edition
 * Progress Bar | Sequential Reveal | Seamless Transition | Citation Copy
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- 1) Scroll progress bar ---
  const header = document.querySelector(".top");
  const progressLine = document.createElement("div");
  progressLine.className = "scroll-progress";
  if (header) header.appendChild(progressLine);

  // --- 2) Sequential Reveal (class付与のみ / delayはCSS側) ---
  const targets = document.querySelectorAll(
    "h1, .who, .lead, .paper, .section-label, footer"
  );

  // Reduced Motion: 演出を完全スキップし、表示欠落事故を防ぐ
  const reducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  if (reducedMotion) {
    targets.forEach((el) => {
      el.classList.add("reveal", "is-visible");

      // 念のため“見えない”事故を潰す（ただしカード傾きは保持）
      el.style.opacity = "1";
      el.style.animation = "none";
      el.style.transition = "none";

      // .paper の rotate() は CSS 側の静的造形なので上書きしない
      if (!el.classList.contains("paper")) {
        el.style.transform = "none";
      } else {
        // 既に何か入っていた場合も想定して除去（CSSのrotateを復活させる）
        el.style.removeProperty("transform");
      }
    });
  }

  // IntersectionObserver 非対応の環境では即表示
  // ※ Reduced Motion 時は observer を一切使わない（上で可視化済）
  if (reducedMotion) {
    // already visible (skip observers)
  } else if (!("IntersectionObserver" in window)) {
    targets.forEach((el) => {
      el.classList.add("reveal", "is-visible");
    });
  } else {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        }
      });
    }, observerOptions);

    targets.forEach((el) => {
      el.classList.add("reveal");
      observer.observe(el);
    });
  }

  // --- 3) Seamless Page Transition ---
  document.body.classList.remove("fade-out");

  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", (e) => {
      // 修飾キー・別操作（新規タブ/ウィンドウ等）は邪魔しない
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      // 右クリック等を邪魔しない（clickでは通常0だが保険）
      if (typeof e.button === "number" && e.button !== 0) return;

      const hrefAttr = link.getAttribute("href");
      if (!hrefAttr) return;

      // 除外：ページ内/メール/PDF/明示別タブ/ダウンロード
      if (hrefAttr.startsWith("#")) return;
      if (hrefAttr.startsWith("mailto:")) return;
      if (hrefAttr.toLowerCase().endsWith(".pdf")) return;
      if (link.target === "_blank") return;
      if (link.hasAttribute("download")) return;

      // 外部判定（URLで安全に判定）
      let url;
      try {
        url = new URL(hrefAttr, window.location.href);
      } catch {
        return;
      }
      if (url.origin !== window.location.origin) return;

      e.preventDefault();

      // Reduced Motion: 待ち時間ゼロで即遷移
      const isReduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;
      if (isReduced) {
        window.location.href = url.href;
        return;
      }

      document.body.classList.add("fade-out");

      setTimeout(() => {
        window.location.href = url.href;
      }, 600);
    });
  });

  // --- 4) Citation Copy (BibTeX) ---
  // HTML例:
  // <button class="copy" type="button" data-copy-target="#bibtex-part3">Copy</button>
  // <pre id="bibtex-part3" class="citation-text">...</pre>

  const setCopyButtonState = (btn, text, ms = 1200) => {
    const original = btn.textContent;
    btn.textContent = text;
    btn.disabled = true;
    window.setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
    }, ms);
  };

  const copyText = async (text) => {
    // Clipboard API が使えるなら優先
    if (
      navigator.clipboard &&
      typeof navigator.clipboard.writeText === "function"
    ) {
      await navigator.clipboard.writeText(text);
      return;
    }

    // フォールバック（古い環境）
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-9999px";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();

    const ok = document.execCommand("copy");
    document.body.removeChild(ta);

    if (!ok) {
      throw new Error("execCommand copy failed");
    }
  };

  // イベント委譲（将来ボタンが増えてもOK）
  document.addEventListener("click", async (e) => {
    const btn =
      e.target && e.target.closest ? e.target.closest("button.copy") : null;
    if (!btn) return;

    const selector = btn.getAttribute("data-copy-target");
    if (!selector) return;

    const target = document.querySelector(selector);
    if (!target) {
      setCopyButtonState(btn, "Not found", 1400);
      return;
    }

    const text = (target.innerText || target.textContent || "").trim();
    if (!text) {
      setCopyButtonState(btn, "Empty", 1400);
      return;
    }

    try {
      await copyText(text);
      setCopyButtonState(btn, "Copied", 1200);
    } catch {
      setCopyButtonState(btn, "Failed", 1600);
    }
  });

  // --- 5) Scroll Events (progress update) ---
  const updateProgress = () => {
    if (!progressLine || !progressLine.isConnected) return;

    const scrolled =
      window.pageYOffset || document.documentElement.scrollTop || 0;
    const maxScroll =
      document.documentElement.scrollHeight - window.innerHeight;

    if (maxScroll > 0) {
      const pct = (scrolled / maxScroll) * 100;
      progressLine.style.width = `${pct}%`;
    } else {
      progressLine.style.width = "0%";
    }
  };

  // 初期表示でも正しい値に
  updateProgress();

  // 連続スクロール負荷を下げる（rAF）
  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        updateProgress();
        ticking = false;
      });
    },
    { passive: true }
  );
});

// --- bfcache / 戻るボタン対策 ---
window.addEventListener("pageshow", (event) => {
  if (event.persisted || document.body.classList.contains("fade-out")) {
    document.body.classList.remove("fade-out");
  }
});
