(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const el = {
    canvas: $("scene"),
    veil: $("veil"),
    banner: $("banner"),
    bannerDesc: $("bannerDesc"),
    bannerState: $("bannerState"),
    bannerReadout: $("bannerReadout"),
    dotSys: $("dotSys"),
    pillSys: $("pillSys"),
    pillCrit: $("pillCrit"),
    pillMode: $("pillMode"),
    dotReg: $("dotReg"),

    presetCombo: $("presetCombo"),
    presetBtn: $("presetBtn"),
    presetList: $("presetList"),
    presetLabelText: $("presetLabelText"),
    presetOpt0: $("presetOpt0"),
    presetOpt1: $("presetOpt1"),
    presetOpt2: $("presetOpt2"),

    toggle: $("toggle"),
    reset: $("reset"),
    gamma: $("gamma"),
    work: $("work"),
    friction: $("friction"),

    telMeta: $("telMeta"),

    g1Dot: $("g1Dot"),
    g1State: $("g1State"),
    g1Rate: $("g1Rate"),
    g1Badge: $("g1Badge"),

    g2Dot: $("g2Dot"),
    g2State: $("g2State"),
    g2Rate: $("g2Rate"),
    g2Badge: $("g2Badge"),

    g3Dot: $("g3Dot"),
    g3State: $("g3State"),
    g3Rate: $("g3Rate"),
    g3Badge: $("g3Badge"),

    g4Dot: $("g4Dot"),
    g4State: $("g4State"),
    g4Req: $("g4Req"),
    g4Badge: $("g4Badge"),

    caseId: $("caseId"),
    cDeltaM: $("cDeltaM"),
    cDeltaP: $("cDeltaP"),
    cAge: $("cAge"),
    cDecision: $("cDecision"),

    adrJson: $("adrJson"),
    copyAdr: $("copyAdr"),
    newCase: $("newCase"),
  };

  if (!el.canvas) return;

  const ctx = el.canvas.getContext("2d", { alpha: true, desynchronized: true });

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smoothstep = (t) => t * t * (3 - 2 * t);
  const now = () => performance.now();

  const fmtPct = (x) => `${Math.round(x * 100)}%`;
  const fmtNum = (x, d = 0) => `${x.toFixed(d)}`;
  const rand = (a = 0, b = 1) => a + Math.random() * (b - a);

  const cssVar = (name, fallback) => {
    const v = getComputedStyle(el.canvas.closest(".altrion-viz") || document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  };

  const palette = () => ({
    ink: cssVar("--c-ink", "rgba(212,212,212,.88)"),
    sub: cssVar("--c-sub", "rgba(212,212,212,.52)"),
    faint: cssVar("--c-faint", "rgba(212,212,212,.26)"),
    warn: cssVar("--c-warn", "rgba(255,209,139,.82)"),
    rust: cssVar("--c-rust-active", "rgba(138,44,44,.72)"),
    line: cssVar("--line", "rgba(255,255,255,.10)"),
    line2: cssVar("--line2", "rgba(255,255,255,.06)"),
  });

  function setDot(dotEl, mode) {
    if (!dotEl) return;
    dotEl.classList.remove("warn", "danger");
    if (mode === "warn") dotEl.classList.add("warn");
    if (mode === "danger") dotEl.classList.add("danger");
  }

  function setBadgeKind(badgeEl, kind) {
    if (!badgeEl) return;
    badgeEl.classList.remove("ok", "warn", "danger");
    if (kind) badgeEl.classList.add(kind);
  }

  function setBanner(mode, stateText, descText) {
    if (!el.banner) return;
    el.banner.classList.remove("ok", "warn", "collapse");
    el.banner.classList.add(mode);
    if (el.bannerState) el.bannerState.textContent = stateText;
    if (el.bannerDesc) el.bannerDesc.textContent = descText;
  }

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

  function measureTextWidth(c, text) {
    return c.measureText(text).width;
  }

  function ellipsize(c, text, maxW) {
    if (measureTextWidth(c, text) <= maxW) return text;
    const ell = "…";
    let lo = 0;
    let hi = text.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      const s = text.slice(0, mid) + ell;
      if (measureTextWidth(c, s) <= maxW) lo = mid;
      else hi = mid - 1;
    }
    return text.slice(0, Math.max(0, lo)) + ell;
  }

  function drawTextFit(c, text, x, y, maxW, align = "left") {
    c.textAlign = align;
    const t = ellipsize(c, text, maxW);
    c.fillText(t, x, y);
    return t;
  }

  function splitLinesByWidth(c, text, maxW) {
    const words = text.split(/\s+/).filter(Boolean);
    if (!words.length) return [""];
    const lines = [];
    let line = words[0];
    for (let i = 1; i < words.length; i++) {
      const next = `${line} ${words[i]}`;
      if (measureTextWidth(c, next) <= maxW) line = next;
      else {
        lines.push(line);
        line = words[i];
      }
    }
    lines.push(line);
    return lines;
  }

  function drawMultiline(c, text, x, y, maxW, lh, align = "left", maxLines = 3) {
    const lines = splitLinesByWidth(c, text, maxW);
    const out = lines.slice(0, maxLines);
    if (lines.length > maxLines) out[maxLines - 1] = ellipsize(c, out[maxLines - 1], maxW);
    c.textAlign = align;
    for (let i = 0; i < out.length; i++) c.fillText(out[i], x, y + i * lh);
    return out.length;
  }

  function dprValue() {
    return Math.max(1, Math.min(2.5, window.devicePixelRatio || 1));
  }

  const geom = {
    dpr: 1,
    w: 0,
    h: 0,
    cw: 0,
    ch: 0,
  };

  function resize() {
    const parent = el.canvas.parentElement;
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

  const sim = {
    running: true,
    t0: now(),
    last: now(),
    time: 0,
    preset: "steady",
    gamma: 0.50,
    work: 0.55,
    friction: 0.62,
    criticalNC: 0.40,
    nc: 0.12,
    err: 0.06,
    eng: 0.66,
    rej: 0.00,
    warn: 0.00,
    rationaleRequired: false,
  };

  function presetParams(key) {
    if (key === "high") return { work: 0.78, gamma: 0.58, friction: 0.58 };
    if (key === "strained") return { work: 0.72, gamma: 0.74, friction: 0.50 };
    return { work: 0.55, gamma: 0.50, friction: 0.62 };
  }

  function applyPreset(key) {
    const p = presetParams(key);
    sim.preset = key;
    sim.work = p.work;
    sim.gamma = p.gamma;
    sim.friction = p.friction;
    if (el.work) el.work.value = `${Math.round(sim.work * 100)}`;
    if (el.gamma) el.gamma.value = `${Math.round(sim.gamma * 100)}`;
    if (el.friction) el.friction.value = `${Math.round(sim.friction * 100)}`;
    if (el.presetCombo) el.presetCombo.dataset.value = key;
    if (el.presetLabelText) {
      el.presetLabelText.textContent =
        key === "high" ? "High-volume (queue pressure)" :
        key === "strained" ? "Strained (thin staffing)" :
        "Steady (moderate workload)";
    }
    if (el.presetOpt0) el.presetOpt0.setAttribute("aria-selected", key === "steady" ? "true" : "false");
    if (el.presetOpt1) el.presetOpt1.setAttribute("aria-selected", key === "high" ? "true" : "false");
    if (el.presetOpt2) el.presetOpt2.setAttribute("aria-selected", key === "strained" ? "true" : "false");
  }

  function logistic(x) {
    return 1 / (1 + Math.exp(-x));
  }

  function updateRates(dt) {
    const w = sim.work;
    const g = sim.gamma;
    const f = sim.friction;

    const fatigue = clamp(0.15 + 0.95 * g, 0, 1);
    const load = clamp(0.10 + 1.10 * w, 0, 1.25);
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
    const collapsePenalty = 0.40 * collapse;

    const errTarget = clamp(errorBase - benefit + collapsePenalty, 0.01, 0.98);
    sim.err = lerp(sim.err, errTarget, clamp(dt * 1.8, 0, 1));

    const engTarget = clamp(0.85 - 0.55 * sim.nc + 0.25 * friction - 0.10 * collapse, 0.05, 0.98);
    sim.eng = lerp(sim.eng, engTarget, clamp(dt * 1.4, 0, 1));

    const rejTarget = clamp(0.02 + 0.22 * friction * regime, 0, 0.40);
    sim.rej = lerp(sim.rej, rejTarget, clamp(dt * 1.0, 0, 1));

    const warnTarget = clamp(0.04 + 0.26 * (1 - regime) + 0.10 * friction, 0, 0.55);
    sim.warn = lerp(sim.warn, warnTarget, clamp(dt * 1.0, 0, 1));

    sim.rationaleRequired = sim.nc >= sim.criticalNC * 0.92 || sim.warn > 0.22;
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
        gate: 0,
      });
    }
  }

  function stepParticles(dt) {
    const speed = lerp(0.06, 0.22, sim.eng) * lerp(0.78, 1.15, sim.work);
    const drift = 0.010 + 0.020 * (1 - sim.eng);

    for (const p of particles) {
      p.x += (p.v + speed) * dt;
      p.y += (Math.sin((p.x + p.hue) * 9.0) * 0.002 + (rand(-1, 1) * drift)) * dt * 18.0;

      if (p.y < 0.12) p.y = 0.12;
      if (p.y > 0.92) p.y = 0.92;

      if (p.x > 1.06) {
        p.x = rand(-0.08, 0.02);
        p.y = rand(0.14, 0.90);
        p.v = rand(0.06, 0.18);
        p.r = rand(1.2, 2.4);
        p.a = rand(0.25, 0.95);
        p.hue = rand(0, 1);
        p.gate = 0;
      }
    }
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

    ctx.save();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;

    roundedRectPath(ctx, left.x, left.y, left.w, left.h, cardR);
    ctx.stroke();

    roundedRectPath(ctx, right.x, right.y, right.w, right.h, cardR);
    ctx.stroke();
    ctx.restore();

    const hudTop = left.y + 14;
    const hudX = left.x + 14;

    const mono = `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`;

    ctx.save();
    ctx.font = `600 13px ${mono}`;
    ctx.fillStyle = "rgba(212,212,212,0.70)";
    const hudLine = `NC:${fmtPct(sim.nc)}  ERR:${fmtPct(sim.err)}  ENG:${fmtPct(sim.eng)}  γ:${Math.round(sim.gamma * 100)}  λ:${Math.round(sim.work * 100)}`;
    drawTextFit(ctx, hudLine, hudX, hudTop, left.w - 28, "left");
    ctx.restore();

    const pillY = hudTop + 18;
    const pillH = 30;
    const pillPadX = 12;
    const pillGap = 10;
    const pillNames = ["G1  BASELINE", "G2  VALUE", "G3  TEMPORAL", "G4  ARBITRATE"];

    ctx.save();
    ctx.font = `600 12px ${mono}`;

    const maxRowW = left.w - 28;
    let fontSize = 12;
    let rows = 1;

    for (let attempt = 0; attempt < 6; attempt++) {
      ctx.font = `600 ${fontSize}px ${mono}`;

      let total = 0;
      for (const s of pillNames) total += measureTextWidth(ctx, s) + pillPadX * 2;
      total += pillGap * (pillNames.length - 1);

      if (total <= maxRowW) { rows = 1; break; }

      if (attempt < 3) {
        fontSize -= 1;
      } else {
        rows = 2;
        break;
      }
    }

    ctx.font = `600 ${fontSize}px ${mono}`;
    ctx.textBaseline = "middle";

    const pillWList = pillNames.map((s) => Math.ceil(measureTextWidth(ctx, s) + pillPadX * 2));

    const drawPill = (x, y, w, text, active) => {
      roundedRectPath(ctx, x, y, w, pillH, 999);
      ctx.fillStyle = active ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.18)";
      ctx.fill();
      ctx.strokeStyle = active ? "rgba(255,255,255,0.16)" : "rgba(255,255,255,0.10)";
      ctx.stroke();

      ctx.fillStyle = active ? "rgba(212,212,212,0.86)" : "rgba(212,212,212,0.62)";
      const tx = x + pillPadX;
      drawTextFit(ctx, text, tx, y + pillH / 2, w - pillPadX * 2, "left");
    };

    const activeGate = clamp(Math.floor(sim.time * 0.8) % 4, 0, 3);

    if (rows === 1) {
      let x = hudX;
      for (let i = 0; i < pillNames.length; i++) {
        const w = pillWList[i];
        drawPill(x, pillY, w, pillNames[i], i === activeGate);
        x += w + pillGap;
      }
    } else {
      const row1 = [0, 1];
      const row2 = [2, 3];
      const rowsIdx = [row1, row2];
      for (let r = 0; r < 2; r++) {
        const indices = rowsIdx[r];
        let total = 0;
        for (const idx of indices) total += pillWList[idx];
        total += pillGap * (indices.length - 1);
        let x = hudX;
        const y = pillY + r * (pillH + 10);
        for (let k = 0; k < indices.length; k++) {
          const idx = indices[k];
          const w = pillWList[idx];
          drawPill(x, y, w, pillNames[idx], idx === activeGate);
          x += w + pillGap;
        }
      }
    }

    ctx.restore();

    const plotTop = left.y + 70;
    const plotBottom = left.y + left.h - 18;
    const plotLeft = left.x + 18;
    const plotRight = left.x + left.w - 18;

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

    const gW = (plotRight - plotLeft) / bands;

    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.02)";
    for (let i = 0; i < bands; i++) {
      const x0 = plotLeft + i * gW;
      ctx.fillRect(x0, plotTop, gW, plotBottom - plotTop);
    }
    ctx.restore();

    ctx.save();
    ctx.beginPath();
    ctx.rect(plotLeft, plotTop, plotRight - plotLeft, plotBottom - plotTop);
    ctx.clip();

    for (const p of particles) {
      const px = plotLeft + p.x * (plotRight - plotLeft);
      const py = plotTop + p.y * (plotBottom - plotTop);
      const alpha = 0.22 + 0.55 * p.a;
      const hot = sim.nc >= sim.criticalNC ? 1 : 0;
      const dotR = p.r;
      ctx.fillStyle = hot ? `rgba(255,209,139,${0.16 * alpha})` : `rgba(212,212,212,${0.22 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, dotR + 2.3, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = hot ? `rgba(255,255,255,${0.55 * alpha})` : `rgba(255,255,255,${0.42 * alpha})`;
      ctx.beginPath();
      ctx.arc(px, py, dotR, 0, Math.PI * 2);
      ctx.fill();
    }

    const collapse = clamp((sim.nc - sim.criticalNC) / 0.18, 0, 1);
    if (collapse > 0.02) {
      const x0 = plotLeft + (plotRight - plotLeft) * 0.84;
      const w = (plotRight - plotLeft) * 0.16;
      const t = smoothstep(collapse);
      const a = 0.10 + 0.28 * t;
      ctx.fillStyle = `rgba(138,44,44,${a})`;
      ctx.fillRect(x0, plotTop, w, plotBottom - plotTop);
    }

    ctx.restore();

    const plotPad = 18;
    const rx0 = right.x + plotPad;
    const ry0 = right.y + 18;
    const rw = right.w - plotPad * 2;
    const rh = right.h - 36;

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

    const gridN = 4;
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.lineWidth = 1;
    for (let i = 1; i < gridN; i++) {
      const gx = lerp(ax.x0, ax.x1, i / gridN);
      const gy = lerp(ax.y0, ax.y1, i / gridN);
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

    const curve = [];
    for (let i = 0; i <= 80; i++) {
      const x = i / 80;
      const below = clamp(1 - x / sim.criticalNC, 0, 1);
      const regime = smoothstep(below);
      const errorBase = 0.18 + 0.62 * x;
      const benefit = 0.22 * sim.friction * regime;
      const collapse = smoothstep(clamp((x - sim.criticalNC) / 0.18, 0, 1));
      const collapsePenalty = 0.40 * collapse;
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

    const titleX = rx0 + 18;
    const titleY = ry0 + 18;
    ctx.save();
    ctx.font = `600 13px ${mono}`;
    ctx.fillStyle = "rgba(212,212,212,0.70)";
    const maxW = rw - 36;
    drawTextFit(ctx, `x: Non-Compliance (NC)`, titleX, titleY, maxW, "left");
    ctx.fillStyle = "rgba(212,212,212,0.55)";
    drawTextFit(ctx, `y: Critical Error`, titleX, titleY + 16, maxW, "left");
    ctx.restore();

    ctx.save();
    ctx.font = `600 12px ${mono}`;
    ctx.fillStyle = "rgba(255,209,139,0.62)";
    const critLabel = `critical @ ${Math.round(sim.criticalNC * 100)}%`;
    const cx = clamp(critX + 10, rx0 + 18, rx0 + rw - 18);
    drawTextFit(ctx, critLabel, cx, ax.y0 + 14, Math.max(60, rx0 + rw - 18 - cx), "left");
    ctx.restore();
  }

  function updateUI() {
    const collapse = sim.nc >= sim.criticalNC;
    const near = sim.nc >= sim.criticalNC * 0.80;

    if (el.pillCrit) el.pillCrit.textContent = `${Math.round(sim.criticalNC * 100)}% NC`;
    if (el.pillMode) el.pillMode.textContent = sim.running ? "SIM" : "PAUSE";

    if (el.pillSys) el.pillSys.textContent = collapse ? "COLLAPSE" : near ? "RISK" : "STABLE";
    setDot(el.dotSys, collapse ? "danger" : near ? "warn" : "");

    if (el.bannerReadout) el.bannerReadout.textContent = `NC: ${fmtPct(sim.nc)} · Error: ${fmtPct(sim.err)}`;
    setDot(el.dotReg, collapse ? "danger" : near ? "warn" : "");

    if (collapse) {
      setBanner("collapse", "COLLAPSE", "Oversight has degraded into procedure (ritualization).");
      if (el.veil) el.veil.classList.add("on");
    } else if (near) {
      setBanner("warn", "RISK", "Approaching critical region (oversight integrity weakening).");
      if (el.veil) el.veil.classList.remove("on");
    } else {
      setBanner("ok", "PRODUCTIVE", "Region of productive friction (oversight remains substantive).");
      if (el.veil) el.veil.classList.remove("on");
    }

    const g1pass = sim.rej < 0.12 || sim.friction > 0.35;
    const g2warn = sim.warn > 0.18;
    const g3warn = sim.warn > 0.22;
    const g4sub = !collapse;

    if (el.g1State) el.g1State.textContent = g1pass ? "PASS" : "HARD";
    if (el.g2State) el.g2State.textContent = g2warn ? "FLAG" : "CLEAR";
    if (el.g3State) el.g3State.textContent = g3warn ? "WARN" : "FRESH";
    if (el.g4State) el.g4State.textContent = g4sub ? "SUBSTANTIVE" : "RITUAL";

    setDot(el.g1Dot, g1pass ? "" : "danger");
    setDot(el.g2Dot, g2warn ? "warn" : "");
    setDot(el.g3Dot, g3warn ? "warn" : "");
    setDot(el.g4Dot, g4sub ? "" : "danger");

    setBadgeKind(el.g1Badge, g1pass ? "" : "danger");
    setBadgeKind(el.g2Badge, g2warn ? "warn" : "");
    setBadgeKind(el.g3Badge, g3warn ? "warn" : "");
    setBadgeKind(el.g4Badge, g4sub ? "" : "danger");

    if (el.g1Rate) el.g1Rate.textContent = `rej ${fmtPct(sim.rej)}`;
    if (el.g2Rate) el.g2Rate.textContent = `flag ${fmtPct(sim.warn * 0.55)}`;
    if (el.g3Rate) el.g3Rate.textContent = `warn ${fmtPct(sim.warn)}`;
    if (el.g4Req) el.g4Req.textContent = sim.rationaleRequired ? "rationale on" : "rationale off";

    if (el.telMeta) {
      el.telMeta.textContent = `${sim.running ? "live" : "paused"} · γ:${Math.round(sim.gamma * 100)} λ:${Math.round(sim.work * 100)} f:${Math.round(sim.friction * 100)}`;
    }
  }

  function makeCase() {
    const id = Math.random().toString(16).slice(2, 10).toUpperCase();
    const deltaM = rand(-0.10, 0.42);
    const deltaP = rand(-0.42, 0.22);
    const ageDays = Math.round(rand(0, 75));
    const stalenessTau = 28;

    const g1Reject = deltaM < -0.02 && sim.friction > 0.45;
    const g2Flag = deltaM > 0.08 && deltaP < -0.14;
    const g3Warn = ageDays > stalenessTau;

    const collapse = sim.nc >= sim.criticalNC;
    const g4Ritual = collapse || sim.rationaleRequired;

    let decision = "ALLOW";
    if (g1Reject) decision = "REJECT";
    else if (g2Flag || g3Warn) decision = g4Ritual ? "ALLOW (RITUAL)" : "ALLOW (RATIONALE)";

    const adr = {
      id: `ADR-${id}`,
      timestamp: new Date().toISOString(),
      context: {
        preset: sim.preset,
        gamma: Number(fmtNum(sim.gamma, 2)),
        workload: Number(fmtNum(sim.work, 2)),
        friction: Number(fmtNum(sim.friction, 2)),
        nc: Number(fmtNum(sim.nc, 3)),
        error: Number(fmtNum(sim.err, 3)),
        critical_nc: Number(fmtNum(sim.criticalNC, 2)),
      },
      case: {
        deltaM: Number(fmtNum(deltaM, 3)),
        deltaP: Number(fmtNum(deltaP, 3)),
        staleness_days: ageDays,
        tau_days: stalenessTau,
      },
      gates: {
        G1: { detect: "C breach", enforce: "REJECT", triggered: !!g1Reject },
        G2: { detect: "value conflict", enforce: "FLAG", triggered: !!g2Flag },
        G3: { detect: "staleness", enforce: "WARN", triggered: !!g3Warn },
        G4: {
          detect: "FLAG/WARN or proximity",
          enforce: "Rationale + ADR",
          mode: g4Ritual ? "RITUALIZED" : "SUBSTANTIVE",
          rationale_required: !!(g2Flag || g3Warn),
        },
      },
      decision,
      auditable: !(collapse),
      rationale_template: {
        required: !!(g2Flag || g3Warn),
        fields: ["context", "tradeoff_acknowledgement", "mitigations", "owner", "expiry_or_review_date"],
      },
    };

    if (el.caseId) el.caseId.textContent = `case: ${id}`;
    if (el.cDeltaM) el.cDeltaM.textContent = fmtNum(deltaM, 3);
    if (el.cDeltaP) el.cDeltaP.textContent = fmtNum(deltaP, 3);
    if (el.cAge) el.cAge.textContent = `${ageDays}d`;
    if (el.cDecision) el.cDecision.textContent = decision;
    if (el.adrJson) el.adrJson.textContent = JSON.stringify(adr, null, 2);

    return adr;
  }

  async function copyText(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {}
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "true");
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      ta.style.top = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch (_) {
      return false;
    }
  }

  function setComboOpen(open) {
    if (!el.presetCombo || !el.presetBtn || !el.presetList) return;
    el.presetCombo.classList.toggle("open", open);
    el.presetBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) el.presetList.focus({ preventScroll: true });
  }

  function wire() {
    const onToggle = () => {
      sim.running = !sim.running;
      if (el.toggle) el.toggle.textContent = sim.running ? "Pause" : "Resume";
      updateUI();
    };

    const onReset = () => {
      sim.nc = 0.12;
      sim.err = 0.06;
      sim.eng = 0.66;
      sim.time = 0;
      seedParticles(70);
      makeCase();
      updateUI();
    };

    const onParam = () => {
      sim.gamma = clamp((Number(el.gamma?.value || 50) || 50) / 100, 0, 1);
      sim.work = clamp((Number(el.work?.value || 55) || 55) / 100, 0, 1);
      sim.friction = clamp((Number(el.friction?.value || 62) || 62) / 100, 0, 1);
      updateUI();
    };

    if (el.toggle) el.toggle.addEventListener("click", onToggle);
    if (el.reset) el.reset.addEventListener("click", onReset);

    if (el.gamma) el.gamma.addEventListener("input", onParam);
    if (el.work) el.work.addEventListener("input", onParam);
    if (el.friction) el.friction.addEventListener("input", onParam);

    if (el.presetBtn) {
      el.presetBtn.addEventListener("click", () => setComboOpen(!el.presetCombo.classList.contains("open")));
      el.presetBtn.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setComboOpen(true);
        }
      });
    }

    const optHandler = (value) => {
      applyPreset(value);
      setComboOpen(false);
      makeCase();
      updateUI();
    };

    if (el.presetOpt0) el.presetOpt0.addEventListener("click", () => optHandler("steady"));
    if (el.presetOpt1) el.presetOpt1.addEventListener("click", () => optHandler("high"));
    if (el.presetOpt2) el.presetOpt2.addEventListener("click", () => optHandler("strained"));

    document.addEventListener("click", (e) => {
      if (!el.presetCombo) return;
      if (!el.presetCombo.contains(e.target)) setComboOpen(false);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setComboOpen(false);
    });

    if (el.newCase) el.newCase.addEventListener("click", () => makeCase());
    if (el.copyAdr) {
      el.copyAdr.addEventListener("click", async () => {
        const text = el.adrJson?.textContent || "{}";
        const ok = await copyText(text);
        el.copyAdr.textContent = ok ? "Copied" : "Copy failed";
        setTimeout(() => { el.copyAdr.textContent = "Copy JSON"; }, 900);
      });
    }

    window.addEventListener("resize", () => {
      resize();
      drawScene();
    }, { passive: true });
  }

  function loop() {
    const t = now();
    const dt = clamp((t - sim.last) / 1000, 0, 0.05);
    sim.last = t;

    if (sim.running) {
      sim.time += dt;
      updateRates(dt);
      stepParticles(dt);
      updateUI();
    }

    drawScene();
    requestAnimationFrame(loop);
  }

  function init() {
    resize();
    wire();
    applyPreset("steady");
    seedParticles(70);
    makeCase();
    updateUI();
    sim.last = now();
    requestAnimationFrame(loop);
  }

  init();
})();
