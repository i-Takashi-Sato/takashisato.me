(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  // Minimal DOM only
  const el = {
    canvas: $("scene"),
    toggle: $("toggle"),
    reset: $("reset"),
    gamma: $("gamma"),
    work: $("work"),
    friction: $("friction"),
  };

  if (!el.canvas) return;

  const ctx = el.canvas.getContext("2d", { alpha: true, desynchronized: true });

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smoothstep = (t) => t * t * (3 - 2 * t);
  const now = () => performance.now();
  const rand = (a = 0, b = 1) => a + Math.random() * (b - a);

  const fmtPct = (x) => `${Math.round(x * 100)}%`;

  // Use visualizer tokens if present (your CSS is --v-*)
  const cssVar = (name, fallback) => {
    const root = el.canvas.closest(".altrion-viz") || document.documentElement;
    const v = getComputedStyle(root).getPropertyValue(name).trim();
    return v || fallback;
  };

  const palette = () => ({
    ink: cssVar("--v-ink", "rgba(212,212,212,.88)"),
    dim: cssVar("--v-dim", "rgba(212,212,212,.52)"),
    dimmer: cssVar("--v-dimmer", "rgba(212,212,212,.26)"),
    line: cssVar("--v-line", "rgba(255,255,255,.10)"),
    line2: cssVar("--v-line-2", "rgba(255,255,255,.06)"),
    accent: cssVar("--v-accent", "rgba(217,4,41,.95)"),
  });

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
    // The canvas is inside .altrion-vizpane which is sized by CSS.
    const parent = el.canvas.parentElement;
    if (!parent) return;

    const rect = parent.getBoundingClientRect();
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

  // Simulation state (kept minimal but coherent)
  const sim = {
    running: true,
    last: now(),
    time: 0,
    // params in 0..1
    gamma: 0.5,
    work: 0.55,
    friction: 0.62,
    criticalNC: 0.4,

    // outputs
    nc: 0.12,
    err: 0.06,
    eng: 0.66,
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
    const noise = (Math.sin(sim.time * 0.9) + Math.sin(sim.time * 0.37 + 1.7)) * 0.007;
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

  const particles = [];

  function seedParticles(n = 70) {
    particles.length = 0;
    for (let i = 0; i < n; i++) {
      particles.push({
        x: rand(0, 1),
        y: rand(0.12, 0.92),
        v: rand(0.06, 0.18),
        r: rand(1.3, 2.4),
        a: rand(0.25, 0.95),
        hue: rand(0, 1),
      });
    }
  }

  function stepParticles(dt) {
    const speed = lerp(0.06, 0.22, sim.eng) * lerp(0.78, 1.15, sim.work);
    const drift = 0.01 + 0.02 * (1 - sim.eng);

    for (const p of particles) {
      p.x += (p.v + speed) * dt;
      p.y += (Math.sin((p.x + p.hue) * 9.0) * 0.002 + (rand(-1, 1) * drift)) * dt * 18.0;

      if (p.y < 0.12) p.y = 0.12;
      if (p.y > 0.92) p.y = 0.92;

      if (p.x > 1.06) {
        p.x = rand(-0.08, 0.02);
        p.y = rand(0.14, 0.9);
        p.v = rand(0.06, 0.18);
        p.r = rand(1.2, 2.4);
        p.a = rand(0.25, 0.95);
        p.hue = rand(0, 1);
      }
    }
  }

  function drawTextFit(c, text, x, y, maxW) {
    // simple ellipsis fit
    const ell = "…";
    if (c.measureText(text).width <= maxW) {
      c.fillText(text, x, y);
      return;
    }
    let lo = 0;
    let hi = text.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      const s = text.slice(0, mid) + ell;
      if (c.measureText(s).width <= maxW) lo = mid;
      else hi = mid - 1;
    }
    c.fillText(text.slice(0, Math.max(0, lo)) + ell, x, y);
  }

  function drawScene() {
    const P = palette();
    const W = geom.cw;
    const H = geom.ch;

    ctx.clearRect(0, 0, W, H);

    const pad = Math.max(14, Math.round(Math.min(W, H) * 0.03));
    const split = Math.round(W * 0.62);

    const left = { x: pad, y: pad, w: split - pad * 1.25, h: H - pad * 2 };
    const right = { x: split + pad * 0.25, y: pad, w: W - split - pad * 1.25, h: H - pad * 2 };
    const cardR = 18;

    // Cards
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    roundedRectPath(ctx, left.x, left.y, left.w, left.h, cardR);
    ctx.stroke();
    roundedRectPath(ctx, right.x, right.y, right.w, right.h, cardR);
    ctx.stroke();
    ctx.restore();

    const mono = `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`;

    // HUD line
    ctx.save();
    ctx.font = `600 13px ${mono}`;
    ctx.fillStyle = P.dim;
    ctx.textBaseline = "alphabetic";
    const hud = `NC:${fmtPct(sim.nc)}  ERR:${fmtPct(sim.err)}  ENG:${fmtPct(sim.eng)}  γ:${Math.round(sim.gamma * 100)}  λ:${Math.round(sim.work * 100)}  f:${Math.round(sim.friction * 100)}`;
    drawTextFit(ctx, hud, left.x + 14, left.y + 18, left.w - 28);
    ctx.restore();

    // Left panel: particle flow
    const plotTop = left.y + 38;
    const plotBottom = left.y + left.h - 18;
    const plotLeft = left.x + 18;
    const plotRight = left.x + left.w - 18;

    // Band grid
    const bands = 4;
    for (let i = 1; i < bands; i++) {
      const gx = plotLeft + ((plotRight - plotLeft) * i) / bands;
      ctx.save();
      ctx.strokeStyle = "rgba(255,255,255,0.06)";
      ctx.setLineDash([6, 10]);
      ctx.beginPath();
      ctx.moveTo(gx, plotTop);
      ctx.lineTo(gx, plotBottom);
      ctx.stroke();
      ctx.restore();
    }

    // clip
    ctx.save();
    ctx.beginPath();
    ctx.rect(plotLeft, plotTop, plotRight - plotLeft, plotBottom - plotTop);
    ctx.clip();

    // collapse region tint
    const cCollapse = clamp((sim.nc - sim.criticalNC) / 0.18, 0, 1);
    if (cCollapse > 0.02) {
      const x0 = plotLeft + (plotRight - plotLeft) * 0.84;
      const w = (plotRight - plotLeft) * 0.16;
      const t = smoothstep(cCollapse);
      const a = 0.10 + 0.28 * t;
      ctx.fillStyle = `rgba(138,44,44,${a})`;
      ctx.fillRect(x0, plotTop, w, plotBottom - plotTop);
    }

    for (const p of particles) {
      const px = plotLeft + p.x * (plotRight - plotLeft);
      const py = plotTop + p.y * (plotBottom - plotTop);
      const alpha = 0.22 + 0.55 * p.a;
      const hot = sim.nc >= sim.criticalNC ? 1 : 0;

      ctx.fillStyle = hot ? `rgba(255,209,139,${0.16 * alpha})` : `rgba(212,212,212,${0.22 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, p.r + 2.3, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = hot ? `rgba(255,255,255,${0.55 * alpha})` : `rgba(255,255,255,${0.42 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, p.r, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();

    // Right panel: curve plot (NC vs Error)
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

    const toX = (nc) => lerp(ax.x0, ax.x1, clamp(nc, 0, 1));
    const toY = (er) => lerp(ax.y1, ax.y0, clamp(er, 0, 1));

    // curve
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

    ctx.save();
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = "rgba(138,44,44,0.62)";
    ctx.beginPath();
    ctx.moveTo(curve[0][0], curve[0][1]);
    for (let i = 1; i < curve.length; i++) ctx.lineTo(curve[i][0], curve[i][1]);
    ctx.stroke();
    ctx.restore();

    // current dot
    const cX = toX(sim.nc);
    const cY = toY(sim.err);
    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.22)";
    ctx.beginPath();
    ctx.arc(cX, cY, 11, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,0.75)";
    ctx.beginPath();
    ctx.arc(cX, cY, 4.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // critical line
    const critX = toX(sim.criticalNC);
    ctx.save();
    ctx.strokeStyle = "rgba(255,209,139,0.22)";
    ctx.setLineDash([6, 10]);
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(critX, ax.y0);
    ctx.lineTo(critX, ax.y1);
    ctx.stroke();
    ctx.restore();

    // labels
    ctx.save();
    ctx.font = `600 13px ${mono}`;
    ctx.fillStyle = P.dim;
    ctx.textBaseline = "alphabetic";
    drawTextFit(ctx, `x: Non-Compliance (NC)`, rx0 + 18, ry0 + 18, rw - 36);
    ctx.fillStyle = P.dimmer;
    drawTextFit(ctx, `y: Critical Error`, rx0 + 18, ry0 + 34, rw - 36);
    ctx.restore();
  }

  function readParamsFromInputs() {
    sim.gamma = clamp((Number(el.gamma?.value || 50) || 50) / 100, 0, 1);
    sim.work = clamp((Number(el.work?.value || 55) || 55) / 100, 0, 1);
    sim.friction = clamp((Number(el.friction?.value || 62) || 62) / 100, 0, 1);
  }

  function wire() {
    const onToggle = () => {
      sim.running = !sim.running;
      if (el.toggle) el.toggle.textContent = sim.running ? "Pause" : "Resume";
    };

    const onReset = () => {
      sim.nc = 0.12;
      sim.err = 0.06;
      sim.eng = 0.66;
      sim.time = 0;
      seedParticles(70);
      drawScene();
    };

    const onParam = () => {
      readParamsFromInputs();
    };

    if (el.toggle) el.toggle.addEventListener("click", onToggle);
    if (el.reset) el.reset.addEventListener("click", onReset);
    if (el.gamma) el.gamma.addEventListener("input", onParam);
    if (el.work) el.work.addEventListener("input", onParam);
    if (el.friction) el.friction.addEventListener("input", onParam);

    window.addEventListener(
      "resize",
      () => {
        resize();
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
    requestAnimationFrame(loop);
  }

  function init() {
    resize();
    readParamsFromInputs();
    wire();
    seedParticles(70);
    sim.last = now();
    requestAnimationFrame(loop);
  }

  init();
})();
