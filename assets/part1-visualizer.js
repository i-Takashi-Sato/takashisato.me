(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const el = {
    app: $("altrion-app"),
    vWrap: $("alt-v-wrap"),
    canvas: $("scene"),
    controls: $("alt-controls"),
    vP: $("v-P"),
    vStatus: $("v-Status"),
  };

  if (!el.app || !el.vWrap || !el.canvas) return;

  const ctx = el.canvas.getContext("2d", { alpha: true, desynchronized: true });
  if (!ctx) return;

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  const prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const dprValue = () => Math.max(1, Math.min(2.25, window.devicePixelRatio || 1));

  const geom = { w: 0, h: 0, dpr: 1 };

  function resize() {
    const rect = el.vWrap.getBoundingClientRect();
    const w = Math.max(10, Math.floor(rect.width));
    const h = Math.max(10, Math.floor(rect.height));
    const dpr = dprValue();

    geom.w = w;
    geom.h = h;
    geom.dpr = dpr;

    el.canvas.width = Math.floor(w * dpr);
    el.canvas.height = Math.floor(h * dpr);
    el.canvas.style.width = w + "px";
    el.canvas.style.height = h + "px";

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const sim = {
    time: 0,
    last: performance.now(),
    pert: 0,

    // mode params
    A: 1.0,
    targetA: 1.0,
    W: 0.05,
    targetW: 0.05,
    gamma: 0.5,

    // output
    P: 1.0,
    status: "Productive Friction",
  };

  const modes = [
    { A: 1.0, W: 0.05, gamma: 0.5, status: "Productive Friction" },      // Crystalline
    { A: 0.65, W: 0.85, gamma: 0.5, status: "Cognitive Engagement" },     // Tension
    { A: 0.15, W: 1.0, gamma: 0.9, status: "Ritualization Collapse" },    // Ritualism
  ];

  function computeP(A, W, gamma) {
    // P_int = max(0, A * (1 - gamma * W))
    return Math.max(0, A * (1 - gamma * W));
  }

  function updateUI() {
    if (el.vP) el.vP.textContent = sim.P.toFixed(3);
    if (el.vStatus) el.vStatus.textContent = sim.status;
  }

  // Particle stream (Gemini line-flow feel)
  class Particle {
    constructor(w, h) {
      this.reset(w, h, true);
    }
    reset(w, h, first = false) {
      this.x = first ? Math.random() * w * 0.2 : -50;
      this.y = Math.random() * h;
      this.speed = 0.9 + Math.random() * 2.2;
      this.len = 28 + Math.random() * 44;
      this.history = [];
      this.phase = Math.random() * 10;
    }
    update(w, h, A, W, P, ritual, time) {
      const scale = 0.00135 * (1 + W * 3.2);
      const n = Math.sin(this.x * scale + time + this.phase) * Math.cos(this.y * scale);

      let vx = ritual ? n * 4.6 : (this.speed + n * W * 9.0);
      let vy = ritual ? Math.sin(time * 1.2 + this.y * 0.01) * 3.2 : n * W * 6.2;

      // Gate attraction lines (match overlay positions)
      if (!ritual) {
        const gates = [0.12, 0.37, 0.62, 0.87];
        for (const gx of gates) {
          const dx = gx * w - this.x;
          if (Math.abs(dx) < 200) {
            const pull = Math.cos((dx / 200) * (Math.PI / 2));
            vy += (h * 0.5 - this.y) * pull * A * 0.06;
          }
        }
        vy += (h * 0.5 - this.y) * A * 0.0105;
      }

      this.history.push({ x: this.x, y: this.y });
      if (this.history.length > this.len) this.history.shift();

      this.x += vx;
      this.y += vy;

      if (this.x > w + 120 || this.y < -120 || this.y > h + 120) {
        this.reset(w, h);
      }
    }
    draw(c, A, W, P, ritual) {
      if (this.history.length < 2) return;

      const alphaBase = ritual ? 0.010 : 0.016 + A * 0.030;
      const lum = ritual ? 80 : 210 + P * 45;

      c.beginPath();
      c.moveTo(this.history[0].x, this.history[0].y);
      for (let i = 1; i < this.history.length - 1; i++) {
        const a = this.history[i];
        const b = this.history[i + 1];
        const xc = (a.x + b.x) * 0.5;
        const yc = (a.y + b.y) * 0.5;
        c.quadraticCurveTo(a.x, a.y, xc, yc);
      }

      if (P < 0.8 && !ritual) {
        c.strokeStyle = `rgba(220,220,255,${alphaBase})`;
        c.lineWidth = 0.75 + W * 0.9;
        c.stroke();

        // dispersion fringe
        c.beginPath();
        c.moveTo(this.history[0].x + 0.9, this.history[0].y);
        for (let i = 1; i < this.history.length - 1; i++) {
          const a = this.history[i];
          const b = this.history[i + 1];
          const xc = (a.x + b.x) * 0.5 + 0.9;
          const yc = (a.y + b.y) * 0.5;
          c.quadraticCurveTo(a.x + 0.9, a.y, xc, yc);
        }
        c.strokeStyle = `rgba(255,160,255,${alphaBase * 0.55})`;
        c.lineWidth = 0.7;
        c.stroke();
      } else {
        c.strokeStyle = `rgba(${lum},${lum},${lum},${alphaBase * 2.8})`;
        c.lineWidth = ritual ? 0.55 : 0.9 + W * 0.75;
        c.stroke();
      }
    }
  }

  let particles = [];

  function particleCount() {
    // mobile throttling
    const isMobile = window.matchMedia && window.matchMedia("(max-width: 844px)").matches;
    if (prefersReducedMotion) return 0;
    return isMobile ? 900 : 1800;
  }

  function buildParticles() {
    const n = particleCount();
    particles = [];
    for (let i = 0; i < n; i++) particles.push(new Particle(geom.w, geom.h));
  }

  function setMode(idx) {
    const m = modes[idx] || modes[0];
    sim.targetA = m.A;
    sim.targetW = m.W;
    sim.gamma = m.gamma;
  }

  function bindEvents() {
    if (el.controls) {
      el.controls.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-alt-mode]");
        if (!btn) return;
        const idx = parseInt(btn.getAttribute("data-alt-mode"), 10);
        setMode(Number.isFinite(idx) ? idx : 0);

        el.controls.querySelectorAll(".altrion-btn").forEach((b) => {
          b.classList.toggle("is-active", b === btn);
        });
      });
    }

    el.vWrap.addEventListener(
      "mousemove",
      (e) => {
        const rect = el.vWrap.getBoundingClientRect();
        const w = Math.max(1, rect.width);
        sim.pert = ((e.clientX - rect.left) / w - 0.5) * 0.18;
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
        buildParticles();
      },
      { passive: true }
    );
  }

  function drawBackdrop(w, h) {
    // deep void + subtle vignette (Gemini feel)
    ctx.clearRect(0, 0, w, h);

    const g = ctx.createRadialGradient(w * 0.5, h * 0.55, 0, w * 0.5, h * 0.55, Math.max(w, h) * 0.75);
    g.addColorStop(0, "rgba(255,255,255,0.02)");
    g.addColorStop(0.55, "rgba(255,255,255,0.00)");
    g.addColorStop(1, "rgba(0,0,0,0.00)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);

    // micro grain
    ctx.save();
    ctx.globalAlpha = 0.04;
    ctx.fillStyle = "#fff";
    const n = Math.floor((w * h) / 140000);
    for (let i = 0; i < n; i++) {
      const x = Math.random() * w;
      const y = Math.random() * h;
      ctx.fillRect(x, y, 1, 1);
    }
    ctx.restore();
  }

  function loop() {
    const t = performance.now();
    const dt = clamp((t - sim.last) / 1000, 0, 0.05);
    sim.last = t;
    sim.time += dt;

    // smooth params
    sim.A += (sim.targetA - sim.A) * (0.065 + dt * 0.3);
    sim.W += (sim.targetW - sim.W) * (0.065 + dt * 0.3);

    const effA = clamp(sim.A + sim.pert, 0, 1);
    sim.P = computeP(effA, sim.W, sim.gamma);

    const ritual = sim.P < 0.25;
    if (ritual) sim.status = "Ritualization Collapse";
    else if (sim.P > 0.8) sim.status = "Productive Friction";
    else sim.status = "Cognitive Engagement";

    const w = geom.w;
    const h = geom.h;

    drawBackdrop(w, h);

    if (!prefersReducedMotion) {
      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      const time = sim.time * 0.75;

      for (const p of particles) {
        p.update(w, h, effA, sim.W, sim.P, ritual, time);
        p.draw(ctx, effA, sim.W, sim.P, ritual);
      }

      ctx.restore();
    }

    updateUI();
    requestAnimationFrame(loop);
  }

  function init() {
    resize();
    buildParticles();
    bindEvents();
    setMode(0);
    updateUI();
    requestAnimationFrame(loop);
  }

  init();
})();
