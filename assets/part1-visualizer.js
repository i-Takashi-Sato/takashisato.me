(() => {
  "use strict";

  const prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const el = (id) => document.getElementById(id);

  const toggleEl   = el("toggle");
  const resetEl    = el("reset");
  const gammaEl    = el("gamma");
  const workEl     = el("work");
  const frictionEl = el("friction");

  const dotSys     = el("dotSys");
  const pillSys    = el("pillSys");
  const pillMode   = el("pillMode");
  const pillCrit   = el("pillCrit");

  const banner      = el("banner");
  const dotReg      = el("dotReg");
  const bannerState = el("bannerState");
  const bannerDesc  = el("bannerDesc");
  const bannerRead  = el("bannerReadout");
  const veil        = el("veil");
  const telMeta     = el("telMeta");

  // Gate UI
  const g1Dot = el("g1Dot"), g2Dot = el("g2Dot"), g3Dot = el("g3Dot"), g4Dot = el("g4Dot");
  const g1State = el("g1State"), g2State = el("g2State"), g3State = el("g3State"), g4State = el("g4State");
  const g1Badge = el("g1Badge"), g2Badge = el("g2Badge"), g3Badge = el("g3Badge"), g4Badge = el("g4Badge");
  const g1Rate = el("g1Rate"), g2Rate = el("g2Rate"), g3Rate = el("g3Rate"), g4Req = el("g4Req");

  // Live case + ADR
  const caseIdEl   = el("caseId");
  const cDeltaM    = el("cDeltaM");
  const cDeltaP    = el("cDeltaP");
  const cAge       = el("cAge");
  const cDecision  = el("cDecision");
  const adrJsonEl  = el("adrJson");
  const copyAdr    = el("copyAdr");
  const newCaseBtn = el("newCase");

  // Canvas
  const canvas = el("scene");
  const ctx = canvas.getContext("2d", { alpha:true, desynchronized:true });

  /* =========================================================
     Custom Combobox: preset
     - Keyboard: ↑↓ / Enter / Esc
     - Popover: 0.12s expand (CSS transition)
     ========================================================= */
  const presetCombo = el("presetCombo");
  const presetBtn   = el("presetBtn");
  const presetLabelText = el("presetLabelText");
  const presetList  = el("presetList");
  const presetOpts  = Array.from(presetCombo.querySelectorAll(".comboOpt"));

  let presetOpen = false;
  let presetActiveIndex = Math.max(0, presetOpts.findIndex(o => o.getAttribute("aria-selected") === "true"));

  function getPresetValue(){
    return presetCombo.getAttribute("data-value") || "steady";
  }

  function syncPresetActiveVisual(){
    presetOpts.forEach((o, i) => o.classList.toggle("is-active", i === presetActiveIndex));
    const act = presetOpts[presetActiveIndex];
    if (act) {
      presetList.setAttribute("aria-activedescendant", act.id || "");
      if (presetOpen) act.scrollIntoView({ block: "nearest" });
    }
  }

  function setPresetValue(v){
    presetCombo.setAttribute("data-value", v);
    presetOpts.forEach((o, i) => {
      const on = (o.dataset.value === v);
      o.setAttribute("aria-selected", on ? "true" : "false");
      if (on) {
        presetLabelText.textContent = o.textContent.trim();
        presetActiveIndex = i;
      }
    });
    syncPresetActiveVisual();
  }

  function closePreset({ focusBtn = false } = {}){
    presetOpen = false;
    presetCombo.classList.remove("open");
    presetBtn.setAttribute("aria-expanded", "false");
    if (focusBtn) presetBtn.focus({ preventScroll:true });
  }

  function openPreset(){
    presetOpen = true;
    // Align active to current selection
    const idx = presetOpts.findIndex(o => o.getAttribute("aria-selected") === "true");
    presetActiveIndex = idx >= 0 ? idx : 0;

    presetCombo.classList.add("open");
    presetBtn.setAttribute("aria-expanded", "true");
    syncPresetActiveVisual();
    presetList.focus({ preventScroll:true });
  }

  function togglePreset(){
    if (presetOpen) closePreset();
    else openPreset();
  }

  function movePreset(delta){
    const n = presetOpts.length;
    presetActiveIndex = (presetActiveIndex + delta + n) % n;
    syncPresetActiveVisual();
  }

  function commitPreset(index){
    const opt = presetOpts[index];
    if (!opt) return;
    setPresetValue(opt.dataset.value);
    closePreset({ focusBtn:true });
    applyPreset();
    makeCase();
  }

  // Click
  presetBtn.addEventListener("click", togglePreset);

  // Option click (prevent focus jumps)
  presetOpts.forEach((btn, i) => {
    btn.addEventListener("mousedown", (e) => e.preventDefault());
    btn.addEventListener("click", () => commitPreset(i));
  });

  // Keyboard: on button
  presetBtn.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!presetOpen) openPreset();
      else movePreset(+1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (!presetOpen) openPreset();
      else movePreset(-1);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (!presetOpen) openPreset();
      else commitPreset(presetActiveIndex);
    } else if (e.key === "Escape") {
      if (presetOpen) { e.preventDefault(); closePreset({ focusBtn:true }); }
    }
  });

  // Keyboard: when listbox focused
  presetList.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); movePreset(+1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); movePreset(-1); }
    else if (e.key === "Enter") { e.preventDefault(); commitPreset(presetActiveIndex); }
    else if (e.key === "Escape") { e.preventDefault(); closePreset({ focusBtn:true }); }
    else if (e.key === "Home") { e.preventDefault(); presetActiveIndex = 0; syncPresetActiveVisual(); }
    else if (e.key === "End") { e.preventDefault(); presetActiveIndex = presetOpts.length - 1; syncPresetActiveVisual(); }
  });

  // Close on outside click
  document.addEventListener("pointerdown", (e) => {
    if (!presetOpen) return;
    if (!presetCombo.contains(e.target)) closePreset();
  });

  let W=0,H=0, dpr=1;
  function resize(){
    const r = canvas.getBoundingClientRect();
    W = Math.max(320, Math.floor(r.width));
    H = Math.max(420, Math.floor(r.height));
    dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    canvas.width = Math.floor(W*dpr);
    canvas.height = Math.floor(H*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  window.addEventListener("resize", resize, { passive:true });

  // Pull CSS vars for consistent visibility against dark
  const rs = getComputedStyle(document.documentElement);
  const MONO = (rs.getPropertyValue("--font-mono") || "ui-monospace").trim();

  const C_INK   = (rs.getPropertyValue("--c-ink") || "rgba(212,212,212,.88)").trim();
  const C_SUB   = (rs.getPropertyValue("--c-sub") || "rgba(212,212,212,.52)").trim();
  const C_FAINT = (rs.getPropertyValue("--c-faint") || "rgba(212,212,212,.26)").trim();

  /* IMPORTANT: OK is INK (not blue) */
  const C_OK    = (rs.getPropertyValue("--c-ink") || "rgba(212,212,212,.88)").trim();
  const C_WARN  = (rs.getPropertyValue("--c-warn") || "rgba(255,209,139,.82)").trim();
  const C_DANG  = (rs.getPropertyValue("--c-rust-active") || "rgba(138,44,44,.72)").trim();

  // Deterministic RNG
  let seed = 202501;
  function rand(){
    seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5;
    return ((seed >>> 0) / 4294967296);
  }
  function clamp(x,a,b){ return Math.max(a, Math.min(b, x)); }
  function lerp(a,b,t){ return a + (b-a)*t; }
  function smoothstep(t){ return t*t*(3-2*t); }
  function sigmoid(x){ return 1 / (1 + Math.exp(-x)); }

  const CRIT = 0.40; // 40% critical NC (visual anchor)
  const TAU_H = 24;  // temporal threshold τ (hours)
  const THETA = 0.12;// value-conflict threshold θ
  pillCrit.textContent = `${Math.round(CRIT*100)}% NC`;

  const tokens = [];
  const MAX_TOK = 44;

  let running = true;
  let t = 0;

  // State vars (0..1)
  let nc = 0.12;
  let err = 0.06;
  let engage = 0.62;
  let collapse = false;

  // Rolling rates (EMA)
  const roll = { g1_rej: 0, g2_warn: 0, g3_warn: 0, g4_rej: 0 };
  function ema(prev, sample, a){ return prev*(1-a) + sample*a; }

  // Exemplar “case”
  let caseObj = null;

  function makeCase(){
    const w = clamp(Number(workEl.value)/100, 0, 1);
    const g = clamp(Number(gammaEl.value)/100, 0.1, 0.9);
    const f = clamp(Number(frictionEl.value)/100, 0, 1);

    const dM = clamp(0.08 + 0.62 * (0.35 + 0.65*w) * (0.65 + 0.35*(1-f)) + (rand()-0.5)*0.10, 0.02, 0.85);
    const dP = clamp(-(0.04 + 0.55 * (0.30 + 0.70*g) * (0.35 + 0.65*w)) + (rand()-0.5)*0.10, -0.95, 0.10);
    const ageH = clamp(6 + 70*(0.20 + 0.80*w) + (rand()-0.5)*10, 0, 96);

    const breachP = clamp(0.02 + 0.20*err + 0.15*smoothstep(clamp((nc-CRIT)/0.30,0,1)), 0, 0.55);
    const g1Breach = rand() < breachP;

    const valueConflict = (dM > 0) && (dP < -THETA);
    const temporalWarn = (ageH > TAU_H);

    const nearCrit = (nc >= CRIT*0.90);
    const rationaleRequired = valueConflict || temporalWarn || nearCrit;

    let decision = "ALLOW";
    if (g1Breach) decision = "REJECT";
    else if (!collapse && rationaleRequired) decision = "HOLD";
    else decision = "ALLOW";

    const id = `ALTRION-${Math.floor(100000 + rand()*900000)}`;

    caseObj = {
      id,
      deltaM: dM,
      deltaP: dP,
      ageH,
      theta: THETA,
      tauH: TAU_H,
      g1: { breach: g1Breach },
      g2: { conflict: valueConflict },
      g3: { stale: temporalWarn },
      g4: { rationaleRequired, substantive: !collapse },
      decision,
      timestamp: new Date().toISOString()
    };
    renderCaseAndADR();
  }

  function applyPreset(){
    const p = getPresetValue();
    if (p === "steady"){
      workEl.value = 55; gammaEl.value = 50; frictionEl.value = 62;
    } else if (p === "high"){
      workEl.value = 78; gammaEl.value = 58; frictionEl.value = 58;
    } else {
      workEl.value = 72; gammaEl.value = 72; frictionEl.value = 68;
    }
  }

  function computeTargets(){
    const g = clamp(Number(gammaEl.value)/100, 0.10, 0.90);
    const w = clamp(Number(workEl.value)/100, 0.00, 1.00);
    const f = clamp(Number(frictionEl.value)/100, 0.00, 1.00);

    const capacity = clamp(1 - (0.55*w + 0.55*g), 0, 1);
    const eff = clamp(0.25 + 0.75 * f * (0.45 + 0.55*capacity), 0, 1);

    const ncT = clamp(
      0.05 + 0.88 * sigmoid( 3.2*(w - 0.52) + 3.1*(g - 0.50) - 2.4*(eff - 0.55) ),
      0, 0.98
    );

    const base = 0.20;
    const benefit = 0.75 * eff * (1 - ncT);
    const lowErr = clamp(base * (1 - benefit), 0.01, 0.35);
    const spike = smoothstep( clamp((ncT - CRIT) / (0.30), 0, 1) );
    const highErr = clamp(lerp(lowErr, 0.62 + 0.25*(1-eff), spike), 0.02, 0.92);

    return { eff, ncT, errT: highErr };
  }

  function update(dt){
    const trg = computeTargets();
    const k = clamp(dt * 0.9, 0, 0.18);

    nc = clamp(lerp(nc, trg.ncT + (rand()-0.5)*0.01, k), 0, 0.98);
    err = clamp(lerp(err, trg.errT + (rand()-0.5)*0.008, k), 0, 0.98);
    engage = clamp(lerp(engage, trg.eff, k), 0, 1);

    collapse = (nc >= CRIT) && (err >= 0.22);

    const spawnRate = lerp(10, 26, engage) * (running ? 1 : 0);
    if (rand() < spawnRate * dt && tokens.length < MAX_TOK){
      tokens.push(makeToken());
    }

    const speed = lerp(0.16, 0.26, 1 - nc) + lerp(0.00, 0.10, engage);
    for (let i=tokens.length-1; i>=0; i--){
      const tok = tokens[i];
      tok.p += dt * speed;
      tok.wob += dt * (0.9 + 0.6*rand());

      const gates = [0.18, 0.36, 0.54, 0.72];
      for (let gi=0; gi<4; gi++){
        if (!tok.hit[gi] && tok.p >= gates[gi]){
          tok.hit[gi] = true;
          const out = gateOutcome(gi, tok);
          tok.state = out.state;
          tok.rej = out.rej || tok.rej;
        }
      }

      if (tok.p > 0.98 || tok.rej){
        tokens.splice(i, 1);
      }
    }
  }

  function makeToken(){
    return {
      p: -0.06 - rand()*0.12,
      lane: rand(),
      wob: rand()*6.28,
      state: "ok",
      rej: false,
      hit: [false,false,false,false],
      warnings: []
    };
  }

  function gateOutcome(gi, tok){
    const r = rand();

    const rejP = lerp(0.020, 0.060, 1 - engage) + lerp(0.00, 0.040, nc);
    const flagP = lerp(0.10, 0.24, engage) * (1 - lerp(0.0, 0.55, nc));

    if (gi === 0){
      const rejected = (r < rejP);
      roll.g1_rej = ema(roll.g1_rej, rejected ? 1 : 0, 0.06);
      return rejected ? { state:"reject", rej:true } : { state:"ok", rej:false };
    }
    if (gi === 1){
      const warned = (r < flagP);
      if (warned) tok.warnings.push("VALUE_CONFLICT");
      roll.g2_warn = ema(roll.g2_warn, warned ? 1 : 0, 0.06);
      return warned ? { state:"flagged", rej:false } : { state:"ok", rej:false };
    }
    if (gi === 2){
      const p = flagP * lerp(0.70, 1.25, Number(workEl.value)/100);
      const warned = (r < p);
      if (warned) tok.warnings.push("TEMPORAL_STALE");
      roll.g3_warn = ema(roll.g3_warn, warned ? 1 : 0, 0.06);
      return warned ? { state:"flagged", rej:false } : { state:"ok", rej:false };
    }

    const needsR = tok.warnings.length > 0 || (nc >= CRIT*0.90);
    g4Req.textContent = needsR ? "rationale on" : "rationale off";

    if (collapse){
      roll.g4_rej = ema(roll.g4_rej, 0, 0.06);
      return { state:"ok", rej:false };
    }

    const arbRej = needsR ? (0.04 + 0.12 * (1 - nc) * engage) : (0.01 + 0.03 * (1 - nc));
    const rejected = (r < arbRej);
    roll.g4_rej = ema(roll.g4_rej, rejected ? 1 : 0, 0.06);
    return rejected ? { state:"reject", rej:true } : { state:"ok", rej:false };
  }

  function riskColor(score){
    if (score < 0.52) return C_OK;
    if (score < 0.78) return C_WARN;
    return C_DANG;
  }

  function roundRect(x,y,w,h,r){
    const rr = Math.min(r, w/2, h/2);
    ctx.beginPath();
    ctx.moveTo(x+rr, y);
    ctx.arcTo(x+w, y, x+w, y+h, rr);
    ctx.arcTo(x+w, y+h, x, y+h, rr);
    ctx.arcTo(x, y+h, x, y, rr);
    ctx.arcTo(x, y, x+w, y, rr);
    ctx.closePath();
  }

  function draw(){
    ctx.clearRect(0,0,W,H);

    const bg = ctx.createLinearGradient(0,0,0,H);
    bg.addColorStop(0, "rgba(0,0,0,.08)");
    bg.addColorStop(1, "rgba(0,0,0,.66)");
    ctx.fillStyle = bg;
    ctx.fillRect(0,0,W,H);

    const pad = 18;
    const leftW = Math.floor(W * 0.56);
    const rightW = W - leftW;

    const pipeX0 = pad;
    const pipeY0 = pad;
    const pipeW  = leftW - pad*1.5;
    const pipeH  = H - pad*2;

    const plotX0 = leftW + pad*0.5;
    const plotY0 = pad;
    const plotW  = rightW - pad*1.5;
    const plotH  = H - pad*2;

    drawPipeline(pipeX0, pipeY0, pipeW, pipeH);
    drawPhasePlot(plotX0, plotY0, plotW, plotH);

    ctx.save();
    ctx.globalAlpha = 0.84;
    ctx.fillStyle = "rgba(212,212,212,.82)";
    ctx.font = `12px ${MONO}`;
    const txt = `NC:${Math.round(nc*100)}%  ERR:${Math.round(err*100)}%  ENG:${Math.round(engage*100)}%  | γ:${gammaEl.value}  λ:${workEl.value}`;
    ctx.fillText(txt, 22, 28);
    ctx.restore();
  }

  function drawPipeline(x,y,w,h){
    ctx.save();
    ctx.globalAlpha = 0.30;
    ctx.strokeStyle = "rgba(255,255,255,.16)";
    ctx.lineWidth = 1;
    roundRect(x,y,w,h,14);
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.10;
    ctx.strokeStyle = "rgba(255,255,255,.12)";
    ctx.lineWidth = 1;
    const step = 44;
    for (let yy=y+step; yy<y+h; yy+=step){
      ctx.beginPath(); ctx.moveTo(x,yy); ctx.lineTo(x+w,yy); ctx.stroke();
    }
    ctx.restore();

    const gateXs = [0.18,0.36,0.54,0.72].map(t => x + w*t);
    const laneMid = y + h*0.58;

    const ribbon = lerp(h*0.18, h*0.10, smoothstep(nc));
    ctx.save();
    ctx.globalAlpha = 0.22;
    ctx.fillStyle = collapse ? "rgba(138,44,44,.10)" : "rgba(212,212,212,.06)";
    roundRect(x+10, laneMid - ribbon/2, w-20, ribbon, 999);
    ctx.fill();
    ctx.restore();

    const labels = ["G1  BASELINE", "G2  VALUE", "G3  TEMPORAL", "G4  ARBITRATE"];
    for (let i=0;i<4;i++){
      const gx = gateXs[i];

      ctx.save();
      ctx.globalAlpha = 0.34;
      ctx.strokeStyle = "rgba(255,255,255,.16)";
      ctx.setLineDash([6,10]);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(gx, y+16);
      ctx.lineTo(gx, y+h-16);
      ctx.stroke();
      ctx.restore();

      ctx.save();
      const capW = 122;
      const capH = 26;
      const cx = clamp(gx - capW/2, x+12, x+w-capW-12);
      const cy = y + 18;
      ctx.globalAlpha = 0.92;
      ctx.fillStyle = "rgba(10,10,10,.56)";
      ctx.strokeStyle = "rgba(255,255,255,.10)";
      ctx.lineWidth = 1;
      roundRect(cx,cy,capW,capH,999);
      ctx.fill(); ctx.stroke();

      ctx.fillStyle = "rgba(212,212,212,.82)";
      ctx.font = `11px ${MONO}`;
      ctx.fillText(labels[i], cx+12, cy+17);
      ctx.restore();
    }

    for (const tok of tokens){
      const px = x + w * tok.p;
      const wob = Math.sin(tok.wob) * lerp(8, 4, smoothstep(nc));
      const py = laneMid + (tok.lane - 0.5) * ribbon * 0.75 + wob;

      let c = C_OK;
      if (tok.warnings.length) c = C_WARN;
      if (tok.state === "reject") c = C_DANG;

      ctx.save();
      ctx.globalAlpha = 0.84;
      ctx.fillStyle = c;
      ctx.strokeStyle = "rgba(0,0,0,.38)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(px, py, 3.2, 0, Math.PI*2);
      ctx.fill(); ctx.stroke();

      ctx.globalAlpha = 0.22;
      ctx.strokeStyle = c;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(px-10, py);
      ctx.lineTo(px-2, py);
      ctx.stroke();
      ctx.restore();
    }

    ctx.save();
    ctx.globalAlpha = 0.78;
    ctx.fillStyle = "rgba(212,212,212,.70)";
    ctx.font = `12px ${MONO}`;
    const msg = collapse ? "RITUALIZATION COLLAPSE: Gate 4 loses epistemic correction." : "PRODUCTIVE FRICTION: staged gates preserve engagement.";
    ctx.fillText(msg, x+18, y+h-18);
    ctx.restore();
  }

  function drawPhasePlot(x,y,w,h){
    ctx.save();
    ctx.globalAlpha = 0.30;
    ctx.strokeStyle = "rgba(255,255,255,.16)";
    ctx.lineWidth = 1;
    roundRect(x,y,w,h,14);
    ctx.stroke();
    ctx.restore();

    const pad = 16;
    const axX = x + pad;
    const axY = y + pad;
    const axW = w - pad*2;
    const axH = h - pad*2;

    ctx.save();
    ctx.globalAlpha = 0.10;
    ctx.strokeStyle = "rgba(255,255,255,.12)";
    ctx.lineWidth = 1;
    for (let i=1;i<=4;i++){
      const yy = axY + axH * (i/5);
      ctx.beginPath(); ctx.moveTo(axX,yy); ctx.lineTo(axX+axW,yy); ctx.stroke();
    }
    for (let i=1;i<=4;i++){
      const xx = axX + axW * (i/5);
      ctx.beginPath(); ctx.moveTo(xx,axY); ctx.lineTo(xx,axY+axH); ctx.stroke();
    }
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.10;
    ctx.fillStyle = "rgba(220,230,255,.18)";
    const critX = axX + axW * CRIT;
    roundRect(axX, axY, critX-axX, axH, 12);
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.40;
    ctx.strokeStyle = "rgba(255,209,139,.40)";
    ctx.setLineDash([6,10]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(critX, axY);
    ctx.lineTo(critX, axY+axH);
    ctx.stroke();
    ctx.restore();

    const score = (nc+err)/2;
    ctx.save();
    ctx.globalAlpha = 0.90;
    ctx.strokeStyle = riskColor(score);
    ctx.lineWidth = 2.25;
    ctx.beginPath();
    for (let i=0;i<=120;i++){
      const xx = i/120;
      const errAt = errorGivenNc(xx);
      const px = axX + axW * xx;
      const py = axY + axH * (1 - errAt);
      if (i===0) ctx.moveTo(px,py);
      else ctx.lineTo(px,py);
    }
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.95;
    const px = axX + axW * nc;
    const py = axY + axH * (1 - err);
    ctx.fillStyle = "rgba(212,212,212,.86)";
    ctx.strokeStyle = "rgba(0,0,0,.42)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(px, py, 4.2, 0, Math.PI*2);
    ctx.fill(); ctx.stroke();

    ctx.globalAlpha = 0.18;
    ctx.strokeStyle = riskColor(score);
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(px, py, 6.5, 0, Math.PI*2);
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.globalAlpha = 0.78;
    ctx.fillStyle = "rgba(212,212,212,.66)";
    ctx.font = `11px ${MONO}`;
    ctx.fillText("x: Non-Compliance (NC)", axX+6, axY+14);
    ctx.fillText("y: Critical Error", axX+6, axY+28);
    ctx.fillText("critical @ 40%", critX+6, axY+14);
    ctx.restore();
  }

  function errorGivenNc(ncX){
    const f = clamp(Number(frictionEl.value)/100, 0.00, 1.00);
    const g = clamp(Number(gammaEl.value)/100, 0.10, 0.90);
    const w = clamp(Number(workEl.value)/100, 0.00, 1.00);

    const capacity = clamp(1 - (0.55*w + 0.55*g), 0, 1);
    const eff = clamp(0.25 + 0.75 * f * (0.45 + 0.55*capacity), 0, 1);

    const base = 0.20;
    const benefit = 0.75 * eff * (1 - ncX);
    const lowErr = clamp(base * (1 - benefit), 0.01, 0.35);

    const spike = smoothstep( clamp((ncX - CRIT) / 0.30, 0, 1) );
    const highErr = clamp(lerp(lowErr, 0.62 + 0.25*(1-eff), spike), 0.02, 0.92);
    return highErr;
  }

  function pct(x){ return (x*100).toFixed(1) + "%"; }

  function setBadge(badgeEl, dotEl, stateEl, level){
    badgeEl.className = "badgeMini " + (level || "");
    dotEl.className = "dot" + (level === "warn" ? " warn" : level === "danger" ? " danger" : "");
    stateEl.style.color = (level === "danger") ? "rgba(212,212,212,.86)" : "rgba(212,212,212,.78)";
  }

  function renderCaseAndADR(){
    if (!caseObj) return;

    caseIdEl.textContent = `case: ${caseObj.id}`;
    cDeltaM.textContent = `+${caseObj.deltaM.toFixed(2)}`;
    cDeltaP.textContent = `${caseObj.deltaP.toFixed(2)}`;
    cAge.textContent = `${caseObj.ageH.toFixed(0)}h (τ=${caseObj.tauH}h)`;

    const vc = caseObj.g2.conflict;
    const tw = caseObj.g3.stale;
    const nearCrit = (nc >= CRIT*0.90);
    const needsR = caseObj.g4.rationaleRequired;

    if (caseObj.g1.breach){
      g1State.textContent = "REJECT";
      setBadge(g1Badge, g1Dot, g1State, "danger");
    } else {
      g1State.textContent = "PASS";
      setBadge(g1Badge, g1Dot, g1State, "ok");
    }

    if (vc){
      g2State.textContent = "FLAG";
      setBadge(g2Badge, g2Dot, g2State, "warn");
    } else {
      g2State.textContent = "CLEAR";
      setBadge(g2Badge, g2Dot, g2State, "ok");
    }

    if (tw){
      g3State.textContent = "WARN";
      setBadge(g3Badge, g3Dot, g3State, "warn");
    } else {
      g3State.textContent = "FRESH";
      setBadge(g3Badge, g3Dot, g3State, "ok");
    }

    if (collapse){
      g4State.textContent = "PROCEDURAL";
      setBadge(g4Badge, g4Dot, g4State, "danger");
    } else if (needsR){
      g4State.textContent = "RATIONALE";
      setBadge(g4Badge, g4Dot, g4State, "warn");
    } else {
      g4State.textContent = "SUBSTANTIVE";
      setBadge(g4Badge, g4Dot, g4State, "ok");
    }
    g4Req.textContent = needsR ? "rationale on" : "rationale off";

    let decisionText = caseObj.decision;
    if (caseObj.decision === "HOLD") decisionText = "HOLD (written rationale required)";
    if (caseObj.decision === "REJECT") decisionText = "REJECT (baseline constraint breach)";
    cDecision.textContent = decisionText;

    const adr = {
      adr_id: caseObj.id,
      timestamp: caseObj.timestamp,
      regime: {
        nc: Number((nc).toFixed(4)),
        err: Number((err).toFixed(4)),
        engagement: Number((engage).toFixed(4)),
        critical_nc: CRIT,
        collapse: !!collapse
      },
      parameters: {
        fatigue_gamma: Number(gammaEl.value),
        workload_lambda: Number(workEl.value),
        gate_friction: Number(frictionEl.value),
        theta: caseObj.theta,
        tau_hours: caseObj.tauH
      },
      gates: {
        G1_baseline_constraints: { pass: !caseObj.g1.breach, enforce: caseObj.g1.breach ? "REJECT" : "PASS" },
        G2_value_conflict: { conflict: vc, enforce: vc ? "FLAG" : "CLEAR" },
        G3_temporal_reliability: { stale: tw, enforce: tw ? "WARN" : "FRESH" },
        G4_human_arbitration: {
          rationale_required: needsR || nearCrit,
          mode: collapse ? "PROCEDURAL" : "SUBSTANTIVE"
        }
      },
      warnings: [
        ...(vc ? ["VALUE_CONFLICT"] : []),
        ...(tw ? ["TEMPORAL_STALE"] : []),
        ...(nearCrit ? ["NEAR_CRITICAL_REGIME"] : [])
      ],
      decision: caseObj.decision,
      auditable: !collapse,
      rationale_template: (needsR || nearCrit) ? {
        required: true,
        fields: ["context", "tradeoff_acknowledgement", "mitigations", "owner", "expiry_or_review_date"]
      } : { required: false }
    };

    adrJsonEl.textContent = JSON.stringify(adr, null, 2);
  }

  function renderUI(){
    const ncPct = Math.round(nc*100);
    const erPct = Math.round(err*100);
    bannerRead.textContent = `NC: ${ncPct}% · Error: ${erPct}%`;

    if (collapse){
      banner.className = "banner collapse";
      bannerState.textContent = "COLLAPSE";
      bannerDesc.textContent = "Ritualization collapse: Gate 4 is no longer epistemic correction.";
      dotReg.className = "dot danger";
      dotSys.className = "dot danger";
      pillSys.textContent = "COLLAPSED";
      veil.classList.add("on");
    } else if (nc >= CRIT*0.9){
      banner.className = "banner warn";
      bannerState.textContent = "AT-RISK";
      bannerDesc.textContent = "Approaching critical non-compliance: arbitration becoming procedural.";
      dotReg.className = "dot warn";
      dotSys.className = "dot warn";
      pillSys.textContent = "AT-RISK";
      veil.classList.remove("on");
    } else {
      banner.className = "banner ok";
      bannerState.textContent = "PRODUCTIVE";
      bannerDesc.textContent = "Region of productive friction: staged gates preserve engagement.";
      dotReg.className = "dot";
      dotSys.className = "dot";
      pillSys.textContent = "STABLE";
      veil.classList.remove("on");
    }

    telMeta.textContent = running ? "live" : "hold";

    g1Rate.textContent = `rej ${pct(roll.g1_rej)}`;
    g2Rate.textContent = `warn ${pct(roll.g2_warn)}`;
    g3Rate.textContent = `warn ${pct(roll.g3_warn)}`;

    if (!caseObj) makeCase();
    renderCaseAndADR();
  }

  function copyText(str){
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(str);
    const ta = document.createElement("textarea");
    ta.value = str;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try{ document.execCommand("copy"); } catch(_){}
    document.body.removeChild(ta);
    return Promise.resolve();
  }

  let last = 0;
  function tick(now){
    if (!last) last = now;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    if (running && !prefersReduced){
      t += dt;
      update(dt);
    }

    draw();
    renderUI();
    requestAnimationFrame(tick);
  }

  // Controls
  toggleEl.addEventListener("click", () => {
    running = !running;
    toggleEl.textContent = running ? "Pause" : "Play";
    pillMode.textContent = running ? "SIM" : "HOLD";
  });

  resetEl.addEventListener("click", () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    tokens.length = 0;
    roll.g1_rej = roll.g2_warn = roll.g3_warn = roll.g4_rej = 0;
    nc = 0.12; err = 0.06;
    engage = clamp(Number(frictionEl.value)/100, 0, 1);
    collapse = false;
    makeCase();
  });

  gammaEl.addEventListener("input", () => makeCase());
  workEl.addEventListener("input", () => makeCase());
  frictionEl.addEventListener("input", () => makeCase());

  newCaseBtn.addEventListener("click", () => makeCase());
  copyAdr.addEventListener("click", () => {
    copyText(adrJsonEl.textContent).then(() => {
      copyAdr.textContent = "Copied";
      setTimeout(() => (copyAdr.textContent = "Copy JSON"), 900);
    });
  });

  // init
  resize();
  setPresetValue(getPresetValue());
  applyPreset();
  makeCase();

  if (prefersReduced){
    running = false;
    toggleEl.textContent = "Play";
    pillMode.textContent = "STATIC";
  }

  requestAnimationFrame(tick);
})();
