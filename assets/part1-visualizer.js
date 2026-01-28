(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  // DOM (Absolute Protocol 100)
  const el = {
    app: $("altrion-app"),
    canvas: $("scene"),
    vWrap: $("alt-v-wrap"),
    controls: $("alt-controls"),
    vP: $("v-P"),
    vStatus: $("v-Status"),
  };

  if (!el.canvas || !el.app || !el.vWrap) return;

  const ctx = el.canvas.getContext("2d", { alpha: true, desynchronized: true });

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smoothstep = (t) => t * t * (3 - 2 * t);
  const now = () => performance.now();
  const rand = (a = 0, b = 1) => a + Math.random() * (b - a);

  const fmtPct = (x01) => `${Math.round(clamp(x01, 0, 1) * 100)}%`;

  const prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Use container tokens if present (CSS: --alt-*)
  const cssVar = (name, fallback) => {
    const root = el.app || document.documentElement;
    const v = getComputedStyle(root).getPropertyValue(name).trim();
    return v || fallback;
  };

  const palette = () => ({
    ink: cssVar("--alt-ink", "rgba(242,242,242,0.94)"),
    dim: cssVar("--alt-dim", "rgba(255,255,255,0.56)"),
    dimmer: cssVar("--alt-dimmer", "rgba(255,255,255,0.36)"),
    line: cssVar("--alt-line", "rgba(255,255,255,0.095)"),
    line2: cssVar("--alt-line-2", "rgba(255,255,255,0.145)"),
    accent: cssVar("--alt-accent", "rgba(217,4,41,0.92)"),
  });

  const mono =
    `"Space Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`;

  function roundedRectPath(c, x, y, w, h, r) {
    const rr = Math.min(r, w * 0.5, h * 0.5);
    c.beginPath();
    c.moveTo(x + rr, y);
    c.arcTo(x + w, y, x + w, y + h, rr);
    c.arcTo(x + w, y + h, x, y + h, rr);
    c.arcTo(x, y + h, x, y, rr);
    c.arcTo(x, y, x + w, y, rr);
    c.closePath();
  }

  function dprValue() {
    return Math.max(1, Math.min(2.5, window.devicePixelRatio || 1));
  }

  const geom = { dpr: 1, w: 0, h: 0, cw: 0, ch: 0 };

  function resize() {
    const rect = el.vWrap.getBoundingClientRect();
    const dpr = dprValue();
    const w = Math.max(10, Math.floor(rect.width));
    const h = Math.max(10, Math.floor(rect.height));

    geom.dpr = dpr;
    geom.w = w;
    geom.h = h;

    el.canvas.width = Math.floor(w * dpr);
    el.canvas.height = Math.floor(h * dpr);
    el.canvas.style.width = `${w}px`;
    el.canvas.style.height = `${h}px`;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    geom.cw = w;
    geom.ch = h;
  }

  // Simulation state
  const sim = {
    running: true,
    last: now(),
    time: 0,

    // params (0..1) — modes adjust these
    gamma: 0.48,
    work: 0.55,
    friction: 0.62,
    criticalNC: 0.4,

    // outputs
    nc: 0.12,
    err: 0.06,
    eng: 0.66,

    // pointer perturbation (from viewport mouse)
    pert: 0,
  };

  function logistic(x) {
    return 1 / (1 + Math.exp(-x));
  }

  function updateRates(dt) {
    const w = sim.work;
    const g = sim.gamma;
    const f = sim.friction;

    const fatigue = clamp(0.15 + 0.95 * g, 0, 1);
    const load = clamp(0.1 + 1.1 * w, 0, 1.25);
    const friction = clamp(f, 0, 1);

    const baseNC = logistic((load * 1.35 + fatigue * 1.15 - friction * 1.25) * 2.6 - 1.25);
    const noise =
      (Math.sin(sim.time * 0.9) + Math.sin(sim.time * 0.37 + 1.7)) * 0.007 +
      sim.pert * 0.02;

    const ncTarget = clamp(baseNC + noise, 0, 1);
    sim.nc = lerp(sim.nc, ncTarget, clamp(dt * 2.2, 0, 1));

    const below = clamp(1 - sim.nc / sim.criticalNC, 0, 1);
    const regime = smoothstep(below);

    const errorBase = 0.18 + 0.62 * sim.nc;
    const benefit = 0.22 * friction * regime;

    const collapse = smoothstep(clamp((sim.nc - sim.criticalNC) / 0.18, 0, 1));
    const collapsePenalty = 0.4 * collapse;

    const errTarget = clamp(errorBase - benefit + collapsePenalty, 0.01, 0.98);
    sim.err = lerp(sim.err, errTarget, clamp(dt * 1.8, 0, 1));

    const engTarget = clamp(0.85 - 0.55 * sim.nc + 0.25 * friction - 0.1 * collapse, 0.05, 0.98);
    sim.eng = lerp(sim.eng, engTarget, clamp(dt * 1.4, 0, 1));
  }

  // Particles: “workflow objects” moving through the gates
  const particles = [];

  function desiredParticleCount() {
    // Gemini-like density: desktop ~1200–1600, mobile ~700–1100
    const base = prefersReducedMotion ? 520 : 1250;
    const s = Math.sqrt(Math.max(1, (geom.cw * geom.ch) / (720 * 420)));
    const n = Math.floor(base * clamp(s, 0.75, 1.35));
    return clamp(n, prefersReducedMotion ? 420 : 700, prefersReducedMotion ? 700 : 1700);
  }

  function seedParticles(n) {
    particles.length = 0;
    for (let i = 0; i < n; i++) {
      particles.push({
        x: rand(0, 1),
        y: rand(0.12, 0.92),
        v: rand(0.05, 0.17),
        r: rand(0.9, 1.9),
        a: rand(0.12, 0.92),
        hue: rand(0, 1),
      });
    }
  }

  function rescaleParticlesIfNeeded() {
    const target = desiredParticleCount();
    if (particles.length === 0) {
      seedParticles(target);
      return;
    }
    const diff = target - particles.length;
    if (Math.abs(diff) < 60) return; // avoid churn

    if (diff > 0) {
      for (let i = 0; i < diff; i++) {
        particles.push({
          x: rand(-0.06, 1.02),
          y: rand(0.12, 0.92),
          v: rand(0.05, 0.17),
          r: rand(0.9, 1.9),
          a: rand(0.12, 0.92),
          hue: rand(0, 1),
        });
      }
    } else {
      particles.length = target;
    }
  }

  function stepParticles(dt) {
    const speed = lerp(0.06, 0.24, sim.eng) * lerp(0.78, 1.20, sim.work);
    const drift = 0.012 + 0.022 * (1 - sim.eng);

    for (const p of particles) {
      p.x += (p.v + speed) * dt;
      p.y += (Math.sin((p.x + p.hue) * 9.0) * 0.002 + rand(-1, 1) * drift) * dt * 18.0;

      if (p.y < 0.12) p.y = 0.12;
      if (p.y > 0.92) p.y = 0.92;

      if (p.x > 1.06) {
        p.x = rand(-0.08, 0.02);
        p.y = rand(0.14, 0.9);
        p.v = rand(0.05, 0.17);
        p.r = rand(0.9, 1.9);
        p.a = rand(0.12, 0.92);
        p.hue = rand(0, 1);
      }
    }
  }

  function ellipsize(c, text, maxW) {
    const ell = "…";
    if (c.measureText(text).width <= maxW) return text;
    let lo = 0;
    let hi = text.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      const s = text.slice(0, mid) + ell;
      if (c.measureText(s).width <= maxW) lo = mid;
      else hi = mid - 1;
    }
    return text.slice(0, Math.max(0, lo)) + ell;
  }

  function drawTextFit(c, text, x, y, maxW) {
    c.fillText(ellipsize(c, text, maxW), x, y);
  }

  function uiRegimeLabel() {
    if (sim.nc >= sim.criticalNC) return "Ritualized Compliance";
    if (sim.nc >= sim.criticalNC * 0.78) return "Shear Layer";
    if (sim.nc >= sim.criticalNC * 0.55) return "Transitional";
    return "Laminar Flow";
  }

  function uiIntegrityP() {
    const collapse = smoothstep(clamp((sim.nc - sim.criticalNC) / 0.18, 0, 1));
    const p = clamp(1 - (0.75 * sim.err + 0.35 * sim.nc + 0.25 * collapse), 0.001, 0.999);
    return p;
  }

  function updateConsoleUI() {
    const p = uiIntegrityP();
    if (el.vP) el.vP.textContent = p.toFixed(3);
    if (el.vStatus) el.vStatus.textContent = uiRegimeLabel();
  }

  function drawScene() {
    const P = palette();
    const W = geom.cw;
    const H = geom.ch;

    ctx.clearRect(0, 0, W, H);

    // Phi-based composition
    const pad = Math.max(14, Math.round(Math.min(W, H) * 0.03));
    const phiInv = 0.6180339887;
    const split = Math.round(W * (0.5 + 0.12 * phiInv));
    const left = { x: pad, y: pad, w: split - pad * 1.25, h: H - pad * 2 };
    const right = { x: split + pad * 0.25, y: pad, w: W - split - pad * 1.25, h: H - pad * 2 };

    const cardR = 18;

    // Material frames
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    roundedRectPath(ctx, left.x, left.y, left.w, left.h, cardR);
    ctx.stroke();
    roundedRectPath(ctx, right.x, right.y, right.w, right.h, cardR);
    ctx.stroke();
    ctx.restore();

    // HUD line (instrument readout)
    const hudX = left.x + 14;
    const hudY = left.y + 18;

    ctx.save();
    ctx.font = `600 12.5px ${mono}`;
    ctx.fillStyle = P.dim;
    ctx.textBaseline = "alphabetic";

    const nc = fmtPct(sim.nc);
    const err = fmtPct(sim.err);
    const eng = fmtPct(sim.eng);

    const gamma = Math.round(sim.gamma * 100);
    const lambda = Math.round(sim.work * 100);
    const f = Math.round(sim.friction * 100);

    const hud = `NC:${nc}  ERR:${err}  ENG:${eng}  γ:${gamma}  λ:${lambda}  f:${f}`;
    drawTextFit(ctx, hud, hudX, hudY, left.w - 28);
    ctx.restore();

    // Left plot region
    const plotTop = left.y + 38;
    const plotBottom = left.y + left.h - 18;
    const plotLeft = left.x + 18;
    const plotRight = left.x + left.w - 18;

    // Gate partitions (4 gates)
    const bands = 4;
    for (let i = 1; i < bands; i++) {
      const gx = plotLeft + ((plotRight - plotLeft) * i) / bands;
      ctx.save();
      ctx.strokeStyle = "rgba(255,255,255,0.055)";
      ctx.setLineDash([6, 10]);
      ctx.beginPath();
      ctx.moveTo(gx, plotTop);
      ctx.lineTo(gx, plotBottom);
      ctx.stroke();
      ctx.restore();
    }

    // Clip
    ctx.save();
    ctx.beginPath();
    ctx.rect(plotLeft, plotTop, plotRight - plotLeft, plotBottom - plotTop);
    ctx.clip();

    // Collapse region tint
    const cCollapse = clamp((sim.nc - sim.criticalNC) / 0.18, 0, 1);
    if (cCollapse > 0.01) {
      const x0 = plotLeft + (plotRight - plotLeft) * 0.82;
      const w = (plotRight - plotLeft) * 0.18;
      const t = smoothstep(cCollapse);
      const a = 0.08 + 0.24 * t;
      ctx.fillStyle = `rgba(217,4,41,${a})`;
      ctx.fillRect(x0, plotTop, w, plotBottom - plotTop);

      ctx.save();
      ctx.globalAlpha = 0.22 * t;
      ctx.strokeStyle = "rgba(255,255,255,0.10)";
      ctx.setLineDash([2, 10]);
      for (let k = 0; k < 6; k++) {
        const yy = plotTop + ((plotBottom - plotTop) * (k + 1)) / 7;
        ctx.beginPath();
        ctx.moveTo(x0, yy);
        ctx.lineTo(x0 + w, yy);
        ctx.stroke();
      }
      ctx.restore();
    }

    // Particles (platinum + collapse accent)
    const hot = sim.nc >= sim.criticalNC;
    for (const p of particles) {
      const px = plotLeft + p.x * (plotRight - plotLeft);
      const py = plotTop + p.y * (plotBottom - plotTop);
      const alpha = 0.12 + 0.68 * p.a;

      // Outer bloom
      ctx.fillStyle = hot
        ? `rgba(217,4,41,${0.10 * alpha})`
        : `rgba(255,255,255,${0.08 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, p.r + 2.0, 0, Math.PI * 2);
      ctx.fill();

      // Core dot
      ctx.fillStyle = hot
        ? `rgba(255,255,255,${0.44 * alpha})`
        : `rgba(255,255,255,${0.40 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, p.r, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();

    // Right: NC vs Error curve
    const rp = 18;
    const rx0 = right.x + rp;
    const ry0 = right.y + 14;
    const rw = right.w - rp * 2;
    const rh = right.h - 28;

    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.07)";
    ctx.lineWidth = 1;
    roundedRectPath(ctx, rx0, ry0, rw, rh, 18);
    ctx.stroke();
    ctx.restore();

    const ax = {
      x0: rx0 + 18,
      y0: ry0 + 26,
      x1: rx0 + rw - 18,
      y1: ry0 + rh - 18,
    };

    // inner grid
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 1;
    for (let i = 1; i < 4; i++) {
      const gx = lerp(ax.x0, ax.x1, i / 4);
      const gy = lerp(ax.y0, ax.y1, i / 4);
      ctx.beginPath();
      ctx.moveTo(gx, ax.y0);
      ctx.lineTo(gx, ax.y1);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(ax.x0, gy);
      ctx.lineTo(ax.x1, gy);
      ctx.stroke();
    }
    ctx.restore();

    const toX = (ncV) => lerp(ax.x0, ax.x1, clamp(ncV, 0, 1));
    const toY = (erV) => lerp(ax.y1, ax.y0, clamp(erV, 0, 1));

    // curve samples
    const curve = [];
    for (let i = 0; i <= 80; i++) {
      const x = i / 80;
      const below = clamp(1 - x / sim.criticalNC, 0, 1);
      const regime = smoothstep(below);
      const errorBase = 0.18 + 0.62 * x;
      const benefit = 0.22 * sim.friction * regime;
      const cc = smoothstep(clamp((x - sim.criticalNC) / 0.18, 0, 1));
      const collapsePenalty = 0.4 * cc;
      const y = clamp(errorBase - benefit + collapsePenalty, 0.01, 0.98);
      curve.push([toX(x), toY(y)]);
    }

    const splitIdx = Math.max(1, Math.floor(sim.criticalNC * 80));

    // pre-collapse segment
    ctx.save();
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = "rgba(255,255,255,0.18)";
    ctx.beginPath();
    ctx.moveTo(curve[0][0], curve[0][1]);
    for (let i = 1; i <= splitIdx; i++) ctx.lineTo(curve[i][0], curve[i][1]);
    ctx.stroke();
    ctx.restore();

    // collapse segment
    ctx.save();
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = "rgba(217,4,41,0.62)";
    ctx.beginPath();
    ctx.moveTo(curve[splitIdx][0], curve[splitIdx][1]);
    for (let i = splitIdx + 1; i < curve.length; i++) ctx.lineTo(curve[i][0], curve[i][1]);
    ctx.stroke();
    ctx.restore();

    // current point
    const cX = toX(sim.nc);
    const cY = toY(sim.err);

    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.20)";
    ctx.beginPath();
    ctx.arc(cX, cY, 11, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "rgba(255,255,255,0.78)";
    ctx.beginPath();
    ctx.arc(cX, cY, 4.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // critical line + labels
    const critX = toX(sim.criticalNC);

    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.16)";
    ctx.setLineDash([6, 10]);
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(critX, ax.y0);
    ctx.lineTo(critX, ax.y1);
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.font = `600 12.5px ${mono}`;
    ctx.fillStyle = P.dim;
    ctx.textBaseline = "alphabetic";
    drawTextFit(ctx, `x: Non-Compliance (NC)`, rx0 + 18, ry0 + 18, rw - 36);
    ctx.fillStyle = P.dimmer;
    drawTextFit(ctx, `y: Critical Error`, rx0 + 18, ry0 + 34, rw - 36);
    ctx.restore();

    // Fine grain (very subtle)
    if (!prefersReducedMotion) {
      ctx.save();
      ctx.globalAlpha = 0.028;
      ctx.fillStyle = "rgba(255,255,255,1)";
      const n = Math.floor((W * H) / 110000);
      for (let i = 0; i < n; i++) {
        ctx.fillRect(rand(0, W), rand(0, H), 1, 1);
      }
      ctx.restore();
    }
  }

  function setMode(modeIdx) {
    // 0: Crystalline (stable)
    // 1: Tension (higher load)
    // 2: Ritualism (collapse-prone)
    if (modeIdx === 1) {
      sim.gamma = 0.62;
      sim.work = 0.82;
      sim.friction = 0.44;
    } else if (modeIdx === 2) {
      sim.gamma = 0.84;
      sim.work = 0.74;
      sim.friction = 0.18;
    } else {
      sim.gamma = 0.48;
      sim.work = 0.55;
      sim.friction = 0.62;
    }
  }

  function bindEvents() {
    if (el.controls) {
      el.controls.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-alt-mode]");
        if (!btn) return;

        const modeIdx = parseInt(btn.getAttribute("data-alt-mode"), 10);
        setMode(Number.isFinite(modeIdx) ? modeIdx : 0);

        el.controls.querySelectorAll(".altrion-btn").forEach((b) => {
          b.classList.toggle("is-active", b === btn);
        });

        updateConsoleUI();
      });
    }

    el.vWrap.addEventListener(
      "mousemove",
      (e) => {
        const rect = el.vWrap.getBoundingClientRect();
        const w = Math.max(1, rect.width);
        sim.pert = ((e.clientX - rect.left) / w - 0.5) * 0.2;
      },
      { passive: true }
    );

    el.vWrap.addEventListener(
      "mouseleave",
      () => {
        sim.pert = 0;
      },
      { passive: true }
    );

    window.addEventListener(
      "resize",
      () => {
        resize();
        rescaleParticlesIfNeeded();
        drawScene();
      },
      { passive: true }
    );
  }

  function loop() {
    const t = now();
    const dt = clamp((t - sim.last) / 1000, 0, 0.05);
    sim.last = t;

    if (sim.running) {
      sim.time += dt;
      updateRates(dt);
      stepParticles(dt);
    }

    drawScene();
    updateConsoleUI();
    requestAnimationFrame(loop);
  }

  function init() {
    setMode(0); // Crystalline default
    resize();
    seedParticles(desiredParticleCount());
    bindEvents();
    sim.last = now();
    updateConsoleUI();
    requestAnimationFrame(loop);
  }

  init();
})();
