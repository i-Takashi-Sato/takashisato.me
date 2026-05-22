(() => {
  "use strict";

  const stage = document.getElementById("stage");
  const cDust = document.getElementById("dust");
  const cStr = document.getElementById("strands");
  if (!stage || !cDust || !cStr) return;

  const ctxD = cDust.getContext("2d", { alpha: false });
  const ctxS = cStr.getContext("2d", { alpha: true });
  const cursor = document.getElementById("cursor");
  const uiP = document.getElementById("uiP");
  const uiMeta = document.getElementById("uiMeta");
  const uiStatus = document.getElementById("uiStatus");
  const uiLog = document.getElementById("uiLog");
  const btnExport = document.getElementById("btnExport");
  const btnCopy = document.getElementById("btnCopy");
  const adrNote = document.getElementById("adrNote");
  const gateEls = ["g1", "g2", "g3", "g4"].map(id => document.getElementById(id)).filter(Boolean);

  const isTouch = matchMedia("(pointer: coarse)").matches;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  let W = 1;
  let H = 1;
  let DPR = 1;
  let frame = 0;
  let lastFrameAt = 0;
  let lastCaseAt = 0;
  let paused = document.hidden;

  const MAX_PARTICLES = reduced ? 900 : (isTouch ? 1400 : 2600);
  const LINE_COUNT = reduced ? 10 : (isTouch ? 14 : 22);
  const SEGMENTS = reduced ? 48 : (isTouch ? 58 : 76);
  const minFrameMs = reduced ? 90 : (isTouch ? 50 : 34);

  const P = {
    x: new Float32Array(MAX_PARTICLES),
    y: new Float32Array(MAX_PARTICLES),
    vx: new Float32Array(MAX_PARTICLES),
    vy: new Float32Array(MAX_PARTICLES),
    z: new Float32Array(MAX_PARTICLES),
    tone: new Uint8Array(MAX_PARTICLES)
  };

  const state = {
    mx: 0,
    my: 0,
    A: 0.62,
    W: 0.34,
    tA: 0.62,
    tW: 0.34,
    Wp: 0.34,
    Pint: 0.38,
    collapsed: false,
    dragging: false,
    pressBoost: 0,
    noncompRate: 0,
    caseId: 0,
    pendingFlagged: false,
    pendingAIwrong: false,
    overrideRequested: false,
    t: 0
  };

  const adr = [];

  function clamp01(v){ return Math.max(0, Math.min(1, v)); }
  function pad(n){ return String(n).padStart(2, "0"); }
  function nowHHMMSS(){ const d = new Date(); return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`; }
  function escapeHTML(s){ return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
  function flashNote(text){ if (!adrNote) return; adrNote.textContent = text; setTimeout(() => { adrNote.textContent = ""; }, 1400); }
  function isInteractiveTarget(target){ return !!target.closest?.("a,button,input,textarea,select,label"); }

  function resetParticle(i, x = Math.random() * W, y = Math.random() * H){
    P.x[i] = x;
    P.y[i] = y;
    P.vx[i] = 0.35 + Math.random() * 1.2;
    P.vy[i] = (Math.random() - 0.5) * 0.45;
    P.z[i] = Math.random();
    P.tone[i] = Math.random() > 0.84 ? 1 : 0;
  }

  function resize(){
    W = Math.max(1, innerWidth);
    H = Math.max(1, innerHeight);
    DPR = Math.min(devicePixelRatio || 1, isTouch ? 1 : 1.12);
    for (const c of [cDust, cStr]){
      c.width = Math.floor(W * DPR);
      c.height = Math.floor(H * DPR);
      c.style.width = `${W}px`;
      c.style.height = `${H}px`;
    }
    ctxD.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctxS.setTransform(DPR, 0, 0, DPR, 0, 0);
    for (let i = 0; i < MAX_PARTICLES; i++) resetParticle(i);
    state.mx = W * 0.52;
    state.my = H * 0.48;
  }

  function logADR(entry){
    adr.unshift(entry);
    if (adr.length > (isTouch ? 5 : 7)) adr.length = isTouch ? 5 : 7;
    if (!uiLog) return;
    uiLog.innerHTML = adr.map(r => `<span class="${r.auditable ? "ok" : "bad"}">${escapeHTML(r.line)}</span>`).join("\n");
  }

  function exportPayload(){
    return {
      schema: "ALTRION_ADR_V1_LITE",
      exported_at: new Date().toISOString(),
      meta: { window: { width: W, height: H, dpr: DPR }, pointer: isTouch ? "coarse" : "fine", runtime: "performance-capped" },
      records: adr.slice().reverse()
    };
  }

  function downloadJSON(filename, obj){
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function stepCase(){
    state.caseId++;
    const flagged = Math.random() < (0.16 + state.Wp * 0.22);
    const aiWrong = Math.random() < (0.14 + state.Wp * 0.14);
    state.pendingFlagged = flagged || state.dragging;
    state.pendingAIwrong = aiWrong;

    const missed = flagged && aiWrong && Math.random() > state.Pint;
    state.noncompRate = clamp01(state.noncompRate * 0.88 + (missed ? 0.16 : -0.035));
    state.collapsed = state.noncompRate > 0.42 || (state.dragging && state.Wp > 0.72 && Math.random() > 0.72);
    document.body.classList.toggle("collapse", state.collapsed);

    let decision = "ACCEPT";
    let auditable = true;
    if (flagged && aiWrong && state.overrideRequested){ decision = "OVERRIDE"; auditable = true; }
    else if (missed){ decision = "ACCEPT (UNSEEN ERROR)"; auditable = false; }
    else if (flagged){ decision = "ACCEPT"; auditable = !aiWrong; }
    state.overrideRequested = false;

    const warnings = flagged ? (aiWrong ? "G2:ValueConflict,G3:StaleContext" : "G2:Review") : "";
    logADR({
      timestamp: new Date().toISOString(),
      caseId: state.caseId,
      auditable,
      final_decision: decision,
      warnings,
      line: `[${nowHHMMSS()}] case#${state.caseId} W=${state.Wp.toFixed(2)} A=${state.A.toFixed(2)} P=${state.Pint.toFixed(2)} AI=${aiWrong ? "WRONG" : "OK"} Warnings=[${warnings}] → ${decision}`
    });
  }

  function drawDust(){
    ctxD.globalCompositeOperation = "source-over";
    ctxD.fillStyle = "rgba(6,6,6,0.90)";
    ctxD.fillRect(0, 0, W, H);
    ctxD.globalCompositeOperation = "lighter";

    const t = state.t;
    const press = state.pressBoost;
    const stress = (state.collapsed ? 1.2 : 1) + press * 1.15;
    for (let i = 0; i < MAX_PARTICLES; i++){
      const z = P.z[i];
      const speed = (0.45 + (1 - z) * 1.8) * (0.78 + state.Wp * 0.75) * stress;
      const wave = Math.sin(P.x[i] * 0.006 + P.y[i] * 0.004 + t * (1.8 + press * 1.3));
      const toward = (state.mx - P.x[i]) * 0.000018 * ((state.pendingFlagged ? 1.8 : 0.6) + press * 2.2);
      P.vx[i] += ((speed + toward) - P.vx[i]) * (0.045 + press * 0.018);
      P.vy[i] += (wave * (0.78 + press * 1.65) - P.vy[i]) * (0.035 + press * 0.020);
      if (state.collapsed || state.dragging) P.vy[i] += 0.018 + press * 0.030;
      P.x[i] += P.vx[i];
      P.y[i] += P.vy[i];

      if (P.x[i] > W + 12) resetParticle(i, -8, Math.random() * H);
      if (P.x[i] < -16) resetParticle(i, W + 8, Math.random() * H);
      if (P.y[i] > H + 10) P.y[i] = -8;
      if (P.y[i] < -10) P.y[i] = H + 8;

      const alpha = (0.18 + (1 - z) * 0.62) * ((state.collapsed || state.dragging) ? 0.98 : 0.72);
      if (state.collapsed || state.Wp > 0.78 || state.dragging) ctxD.fillStyle = `hsla(350,82%,64%,${alpha})`;
      else if (P.tone[i]) ctxD.fillStyle = `hsla(200,10%,82%,${alpha})`;
      else ctxD.fillStyle = `hsla(42,58%,70%,${alpha})`;
      const size = 0.55 + (1 - z) * 1.6 + press * 0.35;
      ctxD.fillRect(P.x[i], P.y[i], size * (2.1 + press * 0.8), size);
    }
  }

  function curveY(x, lane, amp, t){
    const base = H * 0.50 + lane;
    return base + Math.sin(x * 0.0045 + t * 1.3) * amp + Math.sin(x * 0.009 + lane * 0.03 - t * 0.8) * amp * 0.38;
  }

  function drawStrands(){
    ctxS.clearRect(0, 0, W, H);
    ctxS.globalCompositeOperation = "screen";
    const press = state.pressBoost;
    const amp = (state.collapsed ? H * 0.045 : H * 0.028) + state.Wp * H * 0.055 + press * H * 0.075;
    const span = W / SEGMENTS;
    const hue = (state.collapsed || state.dragging) ? 350 : 150;

    for (let l = 0; l < LINE_COUNT; l++){
      const k = LINE_COUNT <= 1 ? 0 : (l / (LINE_COUNT - 1)) * 2 - 1;
      const lane = k * H * (isTouch ? 0.045 : 0.06);
      ctxS.beginPath();
      for (let i = 0; i <= SEGMENTS; i++){
        const x = -40 + i * span + 80 * (i / SEGMENTS);
        const pinch = Math.exp(-Math.pow((x - W * (0.42 + press * 0.10)) / (W * 0.085), 2));
        const yy = curveY(x, lane * (1 - pinch * (0.78 + press * 0.35)), amp, state.t + l * 0.04);
        if (i === 0) ctxS.moveTo(x, yy);
        else ctxS.lineTo(x, yy);
      }
      const center = 1 - Math.abs(k);
      ctxS.strokeStyle = `hsla(${hue}, ${(state.collapsed || state.dragging) ? 74 : 18}%, ${(state.collapsed || state.dragging) ? 66 : 76}%, ${0.035 + center * (0.11 + press * 0.10)})`;
      ctxS.lineWidth = state.dragging ? 1.45 : (state.collapsed ? 1.0 : 1.15);
      ctxS.stroke();
    }

    ctxS.beginPath();
    ctxS.moveTo(0, H * 0.5);
    ctxS.lineTo(W, H * 0.5);
    ctxS.strokeStyle = `rgba(230,235,225,${state.collapsed ? 0.05 : 0.13 + press * 0.10})`;
    ctxS.lineWidth = 1;
    ctxS.stroke();
  }

  function updateUI(){
    state.pressBoost += ((state.dragging ? 1 : 0) - state.pressBoost) * 0.16;
    state.A += (state.tA - state.A) * 0.045;
    state.W += (state.tW - state.W) * 0.045;
    state.Wp = clamp01(state.W + (state.pendingFlagged ? 0.08 : 0) + (state.collapsed ? 0.18 : 0) + state.pressBoost * 0.34);
    state.Pint = clamp01(state.A * (1 - 0.55 * state.Wp));

    if (uiP) uiP.textContent = state.Pint.toFixed(2);
    if (uiMeta) uiMeta.innerHTML = `ALIGNMENT <b>${state.A.toFixed(3)}</b><br/>WORKLOAD W <b>${state.W.toFixed(3)}</b><br/>FRICTION W' <b>${state.Wp.toFixed(3)}</b><br/>NON-COMPLIANCE <b>${(state.noncompRate * 100).toFixed(1)}%</b><br/>MODE <b>${state.collapsed ? "RITUALIZATION COLLAPSE" : (state.dragging ? "WORKLOAD SPIKE" : "PRODUCTIVE FRICTION")}</b>`;
    if (uiStatus) uiStatus.textContent = state.collapsed ? "COLLAPSE" : (state.dragging ? "WORKLOAD SPIKE" : "STABLE FLOW");

    const active = Math.max(0, Math.min(3, Math.floor((state.mx / Math.max(1, W)) * 4)));
    gateEls.forEach((el, i) => {
      el.classList.toggle("active", i === active && (state.Wp > 0.52 || state.dragging));
      el.classList.toggle("warn", (state.pendingFlagged && i >= 1) || (state.dragging && i >= active));
    });
  }

  function loop(now = 0){
    requestAnimationFrame(loop);
    if (paused) return;
    if (now - lastFrameAt < minFrameMs) return;
    lastFrameAt = now;
    frame++;
    state.t = frame * 0.018;

    if (isTouch && !state.dragging){
      state.tA = 0.52 + Math.sin(state.t * 0.42) * 0.20;
      state.tW = 0.46 + Math.cos(state.t * 0.35) * 0.16;
      state.mx = W * (0.50 + Math.sin(state.t * 0.36) * 0.17);
      state.my = H * (0.50 + Math.cos(state.t * 0.31) * 0.12);
    }

    updateUI();
    drawDust();
    drawStrands();

    if (frame - lastCaseAt > (isTouch ? 44 : 58)){
      lastCaseAt = frame;
      stepCase();
    }
  }

  function beginPress(e){
    if (isInteractiveTarget(e.target)) return;
    state.dragging = true;
    state.mx = e.clientX;
    state.my = e.clientY;
    state.tA = clamp01(e.clientX / Math.max(1, W));
    state.tW = clamp01(e.clientY / Math.max(1, H));
    document.body.classList.add("dragging");
    try { stage.setPointerCapture?.(e.pointerId); } catch {}
    e.preventDefault();
  }

  function movePress(e){
    if (!state.dragging && isTouch) return;
    state.mx = e.clientX;
    state.my = e.clientY;
    state.tA = clamp01(e.clientX / Math.max(1, W));
    state.tW = clamp01(e.clientY / Math.max(1, H));
    if (cursor){ cursor.style.left = `${e.clientX}px`; cursor.style.top = `${e.clientY}px`; }
    if (state.dragging) e.preventDefault();
  }

  function endPress(){
    state.dragging = false;
    document.body.classList.remove("dragging");
  }

  addEventListener("resize", resize, { passive: true });
  document.addEventListener("visibilitychange", () => { paused = document.hidden; }, { passive: true });
  stage.addEventListener("pointerdown", beginPress, { passive: false });
  stage.addEventListener("pointermove", movePress, { passive: false });
  stage.addEventListener("pointerup", endPress, { passive: true });
  stage.addEventListener("pointercancel", endPress, { passive: true });
  stage.addEventListener("lostpointercapture", endPress, { passive: true });

  if (!isTouch){
    addEventListener("mousemove", e => {
      if (state.dragging) return;
      state.mx = e.clientX;
      state.my = e.clientY;
      state.tA = clamp01(e.clientX / Math.max(1, W));
      state.tW = clamp01(e.clientY / Math.max(1, H));
      if (cursor){ cursor.style.left = `${e.clientX}px`; cursor.style.top = `${e.clientY}px`; }
    }, { passive: true });
    addEventListener("keydown", e => { if (e.key.toLowerCase() === "o") state.overrideRequested = true; });
  } else if (cursor) cursor.style.display = "none";

  btnExport?.addEventListener("click", () => { downloadJSON(`altrion-adr-${Date.now()}.json`, exportPayload()); flashNote("exported"); });
  btnCopy?.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(JSON.stringify(exportPayload(), null, 2)); flashNote("copied"); }
    catch { flashNote("copy failed"); }
  });

  resize();
  logADR({ auditable: true, line: `[${nowHHMMSS()}] boot · click/hold or touch/hold to spike workload · mobile: auto-run.` });
  requestAnimationFrame(loop);
})();
