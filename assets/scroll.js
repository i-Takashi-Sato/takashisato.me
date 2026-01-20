/**
 * Takashi Sato · Research Archive System
 * Interaction Engine: Stable Production Edition
 * Progress Bar | Sequential Reveal | Seamless Transition | Citation Copy
 */

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector(".top");
  const progressLine = document.createElement("div");
  progressLine.className = "scroll-progress";
  if (header) header.appendChild(progressLine);

  const targets = document.querySelectorAll(
    "h1, .who, .lead, .paper, .section-label, footer"
  );

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reducedMotion) {
    targets.forEach((el) => {
      el.classList.add("reveal", "is-visible");
      el.style.opacity = "1";
      el.style.animation = "none";
      el.style.transition = "none";
    });
  }

  if (reducedMotion) {
    // no-op
  } else if (!("IntersectionObserver" in window)) {
    targets.forEach((el) => {
      el.classList.add("reveal", "is-visible");
    });
  } else {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
    );

    targets.forEach((el) => {
      el.classList.add("reveal");
      observer.observe(el);
    });
  }

  document.body.classList.remove("fade-out");

  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (typeof e.button === "number" && e.button !== 0) return;

      const hrefAttr = link.getAttribute("href");
      if (!hrefAttr) return;

      if (hrefAttr.startsWith("#")) return;
      if (hrefAttr.startsWith("mailto:")) return;
      if (hrefAttr.toLowerCase().endsWith(".pdf")) return;
      if (link.target === "_blank") return;
      if (link.hasAttribute("download")) return;

      let url;
      try {
        url = new URL(hrefAttr, window.location.href);
      } catch {
        return;
      }
      if (url.origin !== window.location.origin) return;

      e.preventDefault();

      const isReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
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
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      await navigator.clipboard.writeText(text);
      return;
    }

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

    if (!ok) throw new Error("execCommand copy failed");
  };

  document.addEventListener("click", async (e) => {
    const btn = e.target && e.target.closest ? e.target.closest("button.copy") : null;
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

  const updateProgress = () => {
    if (!progressLine || !progressLine.isConnected) return;

    const scrolled = window.pageYOffset || document.documentElement.scrollTop || 0;
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

    progressLine.style.width = maxScroll > 0 ? `${(scrolled / maxScroll) * 100}%` : "0%";
  };

  updateProgress();

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

window.addEventListener("pageshow", (event) => {
  if (event.persisted || document.body.classList.contains("fade-out")) {
    document.body.classList.remove("fade-out");
  }
});
