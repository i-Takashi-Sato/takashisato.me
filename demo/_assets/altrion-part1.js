(() => {
  "use strict";

  // ====== DOM ======
  const stage = document.getElementById("stage");
  const cDust = document.getElementById("dust");
  const cStr  = document.getElementById("strands");
  if (!stage || !cDust || !cStr) return;

  const ctxD  = cDust.getContext("2d", { alpha: false });
  const ctxS  = cStr.getContext("2d");
  const cursor = document.getElementById("cursor");

  const uiP = document.getElementById("uiP");
  const uiMeta = document.getElementById("uiMeta");
  const uiStatus = document.getElementById("uiStatus");
  const uiLog = document.getElementById("uiLog");

  const btnExport = document.getElementById("btnExport");
  const btnCopy = document.getElementById("btnCopy");
  const adrNote = document.getElementById("adrNote");

  const gateEls = [
    document.getElementById("g1"),
    document.getElementById("g2"),
    document.getElementById("g3"),
    document.getElementById("g4"),
  ].filter(Boolean);

  const isTouch = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;

  // ====== CANVAS / DPR ======
  let W = 0, H = 0, DPR = 1;

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;

    for(const c of [cDust, cStr]){
      c.width  = Math.floor(W * DPR);
      c.height = Math.floor(H * DPR);
      c.style.width = W + "px";
      c.style.height = H + "px";
    }
    ctxD.setTransform(DPR,0,0,DPR,0,0);
    ctxS.setTransform(DPR,0,0,DPR,0,0);

    initField();
    initStrands();
  }
  window.addEventListener("resize", resize);

  // ====== ALTRION STATE (A/W/P + noncompliance + collapse) ======
  const state = {
    mx: -9999, my: -9999,
    dragging:false,

    // target inputs (0..1)
    tA: 0.65,
    tW: 0.35,

    // smoothed
    A: 0.65,
    W: 0.35,

    // derived
    Wp: 0.35,
    Pint: 0.0,
    collapsed:false,

    // flags from gates
    fG1:false, fG2:false, fG3:false,

    // compliance dynamics
    gamma: 0.55,
    noncomplianceWin: 120,
    recentIgnored: [],
    recentFlagged: [],
    noncompRate: 0.0,

    // case stream
    caseId: 0,
    pendingFlagged: false,
    pendingAIwrong: false,
    overrideRequested: false,

    // time
    t: 0,
  };

  // ====== INPUT ======
  function clamp01(x){ return Math.max(0, Math.min(1, x)); }
  function nowHHMMSS(){
    const d = new Date();
    const pad = (n)=>String(n).padStart(2,"0");
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
  function escapeHTML(s){
    return String(s)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;");
  }

  if(!isTouch){
    window.addEventListener("mousemove", (e) => {
      state.mx = e.clientX; state.my = e.clientY;
      if (cursor){
        cursor.style.left = e.clientX + "px";
        cursor.style.top  = e.clientY + "px";
      }

      state.tA = clamp01(e.clientX / Math.max(1, W));
      state.tW = clamp01(e.clientY / Math.max(1, H));
    });

    window.addEventListener("mousedown", () => {
      state.dragging = true;
      document.body.classList.add("dragging");
    });
    window.addEventListener("mouseup", () => {
      state.dragging = false;
      document.body.classList.remove("dragging");
    });

    window.addEventListener("keydown", (e) => {
      if (e.key.toLowerCase() === "o") state.overrideRequested = true;
    });
  } else {
    if (cursor) cursor.style.display = "none";
    state.mx = W*0.5; state.my = H*0.5;
  }

  // ====== Gates geometry ======
  function gateXs(){
    const margin = W * 0.18;
    const avail = W - margin*2;
    return [ margin, margin + avail*0.33, margin + avail*0.66, W - margin ];
  }

  // ====== ADR LOGGING ======
  const adr = [];
  function logADR(entry){
    adr.unshift(entry);
    if(adr.length > 10) adr.length = 10;
    renderLog();
  }
  function renderLog(){
    if (!uiLog) return;
    uiLog.innerHTML = adr.map(r => {
      const cls = r.auditable ? "ok" : "bad";
      return `<span class="${cls}">${escapeHTML(r.line)}</span>`;
    }).join("\n");
  }

  // ====== ADR EXPORT ======
  function buildADRExportPayload(){
    const records = adr.slice().reverse();
    return {
      schema: "ALTRION_ADR_V1",
      exported_at: new Date().toISOString(),
      meta: {
        version: "phase-modulated-spectral-truthline",
        window: { width: W, height: H, dpr: DPR },
        pointer: isTouch ? "coarse" : "fine"
      },
      records: records.map(r => ({
        D: r.final_decision ?? null,
        W: {
          warnings: [
            ...(r.warnings_G2?.length ? ["G2:" + r.warnings_G2.join("|")] : []),
            ...(r.warnings_G3?.length ? ["G3:" + r.warnings_G3.join("|")] : []),
          ],
          gates_passed: r.gates_passed ?? []
        },
        R: r.human_rationale ?? null,
        caseId: r.caseId ?? null,
        auditable: !!r.auditable,
        timestamp: r.timestamp ?? null
      }))
    };
  }

  function downloadJSON(filename, obj){
    const json = JSON.stringify(obj, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return json;
  }

  function flashNote(text){
    if(!adrNote) return;
    adrNote.textContent = text;
    window.setTimeout(() => { adrNote.textContent = ""; }, 1600);
  }

  btnExport?.addEventListener("click", () => {
    const payload = buildADRExportPayload();
    const stamp = new Date().toISOString().replaceAll(":","-").replaceAll(".","-");
    downloadJSON(`altrion-adr-${stamp}.json`, payload);
    flashNote("exported");
  });

  btnCopy?.addEventListener("click", async () => {
    try{
      const payload = buildADRExportPayload();
      const json = JSON.stringify(payload, null, 2);
      await navigator.clipboard.writeText(json);
      flashNote("copied");
    } catch {
      flashNote("copy failed");
    }
  });

  // ====== Decision stream (cases) ======
  function stepCase(){
    state.caseId++;

    const g1 = (Math.random() < (0.03 + (1-state.A)*0.05)) && (state.Wp > 0.75);
    const g2 = !g1 && (Math.random() < (0.18 + state.Wp*0.22));
    const g3 = !g1 && (Math.random() < (0.14 + state.W*0.26));

    state.fG1 = g1; state.fG2 = g2; state.fG3 = g3;

    const aiWrong = Math.random() < 0.20;
    state.pendingAIwrong = aiWrong;
    state.pendingFlagged = g1 || g2 || g3;

    const humanWouldIntervene = (Math.random() < state.Pint);

    let finalDecision = "ACCEPT";
    let rationale = null;
    let auditable = true;
    let ignored = 0;

    if (g1) {
      finalDecision = "REJECT (G1)";
      rationale = "Baseline constraint triggered.";
      auditable = true;
      ignored = 0;
    } else if (state.pendingFlagged) {
      const needsIntervention = aiWrong;

      if (state.overrideRequested) {
        state.overrideRequested = false;
        rationale = prompt("Gate-4 Rationale (required):", "Flagged: provide a substantive rationale.");
        if (!rationale || !rationale.trim()) {
          finalDecision = "ACCEPT (RITUALIZED)";
          auditable = false;
          ignored = needsIntervention ? 1 : 0;
        } else {
          finalDecision = needsIntervention ? "OVERRIDE (JUSTIFIED)" : "ACCEPT (JUSTIFIED)";
          auditable = true;
          ignored = 0;
        }
      } else {
        if (needsIntervention && humanWouldIntervene) {
          finalDecision = "OVERRIDE (AUTO)";
          rationale = "Auto-intervention (simulated).";
          auditable = true;
          ignored = 0;
        } else {
          finalDecision = needsIntervention ? "ACCEPT (CRITICAL ERROR)" : "ACCEPT";
          auditable = false;
          ignored = needsIntervention ? 1 : 0;
        }
      }
    } else {
      finalDecision = aiWrong ? "ACCEPT (UNSEEN ERROR)" : "ACCEPT";
      auditable = true;
      ignored = aiWrong ? 1 : 0;
    }

    state.recentIgnored.push(ignored);
    state.recentFlagged.push(state.pendingFlagged ? 1 : 0);
    if (state.recentIgnored.length > state.noncomplianceWin) state.recentIgnored.shift();
    if (state.recentFlagged.length > state.noncomplianceWin) state.recentFlagged.shift();

    const ignoredSum = state.recentIgnored.reduce((a,b)=>a+b,0);
    const flaggedSum = Math.max(1, state.recentFlagged.reduce((a,b)=>a+b,0));
    state.noncompRate = clamp01(ignoredSum / flaggedSum);

    const was = state.collapsed;
    state.collapsed = state.noncompRate > 0.40;
    if (state.collapsed !== was) document.body.classList.toggle("collapse", state.collapsed);

    const warnings = [];
    if (g2) warnings.push("G2:ValueConflict");
    if (g3) warnings.push("G3:StaleContext");

    const line =
      `[${nowHHMMSS()}] case#${state.caseId} ` +
      `W=${state.Wp.toFixed(2)} A=${state.A.toFixed(2)} P=${state.Pint.toFixed(2)} ` +
      `AI=${aiWrong?"WRONG":"OK"} ` +
      `${g1?"G1:REJECT":"Warnings=["+warnings.join(",")+"]"} ` +
      `→ ${finalDecision}` +
      (rationale ? ` | R="${rationale.slice(0,40)}${rationale.length>40?"…":""}"` : "");

    logADR({
      timestamp: Date.now(),
      caseId: state.caseId,
      gates_passed: g1 ? ["G1"] : ["G1","G2","G3","G4"],
      warnings_G2: g2 ? ["Metric_Imbalance_High"] : [],
      warnings_G3: g3 ? ["Freshness_Threshold_Breach"] : [],
      human_rationale: rationale,
      final_decision: finalDecision,
      auditable,
      line
    });
  }

  // ====== Visual system B: dust + flow field ======
  const FIELD_RES = 42;
  let cols = 0, rows = 0, field = null;

  const PARTICLES = 9000;
  const P = {
    x: new Float32Array(PARTICLES),
    y: new Float32Array(PARTICLES),
    vx:new Float32Array(PARTICLES),
    vy:new Float32Array(PARTICLES),
    z: new Float32Array(PARTICLES),
    s: new Float32Array(PARTICLES),
    t: new Uint8Array(PARTICLES),
  };

  function initField(){
    cols = Math.ceil(W / FIELD_RES) + 3;
    rows = Math.ceil(H / FIELD_RES) + 3;
    field = new Float32Array(cols * rows * 2);
    for(let i=0;i<PARTICLES;i++) resetParticle(i, Math.random()*W, Math.random()*H);
  }

  function resetParticle(i,x,y){
    P.x[i]=x; P.y[i]=y;
    P.vx[i]=0; P.vy[i]=0;
    const z = Math.random();
    P.z[i]=z;
    P.s[i]=(1-z)*1.6 + 0.45;
    P.t[i]=(Math.random()>0.82) ? 1 : 0;
  }

  function noise2(x,y,t){
    return Math.sin(x*0.008 + t*0.2) * Math.cos(y*0.010 + t*0.11) * 2.0;
  }

  function updateField(t){
    const gx = gateXs();
    const stress = clamp01(state.dragging ? (state.Wp) : 0);

    for(let x=0;x<cols;x++){
      for(let y=0;y<rows;y++){
        const idx = (x + y*cols)*2;
        const px = x*FIELD_RES;
        const py = y*FIELD_RES;

        let ang = 0.10 * Math.cos(x*0.10 + t*0.8);

        const dx2 = Math.abs(px - gx[1]);
        if (dx2 < 140){
          const f = (1 - dx2/140) * (state.fG2 ? 2.2 : 0.9);
          ang += (py < H*0.5 ? -1 : 1) * f;
        }

        const dx3 = Math.abs(px - gx[2]);
        if (dx3 < 140){
          const f = (1 - dx3/140) * (state.fG3 ? 1.8 : 0.6);
          ang += noise2(px,py,t) * f * 0.65;
        }

        if (state.dragging){
          ang += noise2(px,py,t) * (0.8 + stress*2.0);
        }

        const dx = px - state.mx, dy = py - state.my;
        const dsq = dx*dx + dy*dy;
        const rsq = 280*280;
        if(dsq < rsq){
          const f = (1 - dsq/rsq) * 1.8 * (1 + state.Wp);
          const push = Math.atan2(dy,dx);
          ang += push * f * 0.12;
        }

        field[idx]   = Math.cos(ang);
        field[idx+1] = Math.sin(ang);
      }
    }
  }

  // ====== Visual system A: strands (Verlet) ======
  const STRANDS = 52;
  const POINTS  = 58;
  const ITER    = 3;

  class VPoint{
    constructor(x,y,pin){
      this.x=x; this.y=y;
      this.ox=x; this.oy=y;
      this.pin=pin;
    }
    step(drag, gravity){
      if(this.pin) return;
      const vx = (this.x - this.ox) * drag;
      const vy = (this.y - this.oy) * drag;
      this.ox = this.x; this.oy = this.y;
      this.x += vx;
      this.y += vy + gravity;
    }
  }
  class Link{
    constructor(a,b){
      this.a=a; this.b=b;
      this.rest = Math.hypot(a.x-b.x, a.y-b.y);
    }
    solve(k){
      const dx = this.a.x - this.b.x;
      const dy = this.a.y - this.b.y;
      const d = Math.sqrt(dx*dx + dy*dy) || 0.0001;
      const diff = (this.rest - d) / d * k;
      const ox = dx * diff * 0.5;
      const oy = dy * diff * 0.5;
      if(!this.a.pin){ this.a.x += ox; this.a.y += oy; }
      if(!this.b.pin){ this.b.x -= ox; this.b.y -= oy; }
    }
  }

  let strands = [];
  function initStrands(){
    strands = [];
    const startX = -60;
    const endX = W + 60;
    const stepX = (endX - startX) / POINTS;

    for(let s=0;s<STRANDS;s++){
      const ns = (s/(STRANDS-1))*2 - 1;
      const spread = H * 0.06 * ns;

      const pts = [];
      const links = [];
      for(let i=0;i<=POINTS;i++){
        const x = startX + i*stepX;
        const y = H*0.5 + spread;
        const pin = (i===0 || i===POINTS);
        pts.push(new VPoint(x,y,pin));
        if(i>0) links.push(new Link(pts[i], pts[i-1]));
      }
      strands.push({ ns, pts, links });
    }
  }

  // ====== THE LINE: Phase-Modulated Spectral Stack (204° fixed) ======
  function drawTruthLineSpectral(){
    if(state.A <= 0.25) return;

    const baseAlpha = Math.max(0, (state.A * 0.40) * (1 - state.Wp * 0.72));
    if(baseAlpha <= 0.0005) return;

    if(state.collapsed){
      ctxS.save();
      ctxS.beginPath();
      ctxS.moveTo(0, H*0.5);
      ctxS.lineTo(W, H*0.5);
      ctxS.strokeStyle = `hsla(210, 3%, 22%, ${Math.min(0.18, baseAlpha*0.65)})`;
      ctxS.lineWidth = 1;
      ctxS.shadowBlur = 0;
      ctxS.stroke();
      ctxS.restore();
      return;
    }

    const integrity = clamp01((state.Pint * 0.75) + (1 - state.noncompRate) * 0.25);
    const t = state.t;
    const phase = Math.sin(t * 2.2 + integrity * 3.1);
    const micro = Math.sin(t * 12.0 + integrity * 7.0);
    const jitterX = (phase * 0.25) + (micro * 0.10);
    const blur = 10 + (1 - integrity) * 10 + (Math.abs(phase) * 3);
    const a = baseAlpha;

    const hue = 204;
    const passes = [
      { ox: jitterX * 1.00, lw: 0.75, sat: 1.5, lig: 95, mulA: 1.00, sh: blur * 0.35 },
      { ox: jitterX * 0.55, lw: 1.25, sat: 6.0, lig: 90, mulA: 0.60, sh: blur * 0.65 },
      { ox: jitterX * 0.20, lw: 2.20, sat: 14.0, lig: 86, mulA: 0.25, sh: blur * 1.00 },
    ];

    for(const p of passes){
      ctxS.save();
      ctxS.beginPath();
      ctxS.translate(p.ox, 0);
      ctxS.moveTo(0, H*0.5);
      ctxS.lineTo(W, H*0.5);

      const alpha = a * p.mulA * (0.92 + 0.08 * (1 + micro));
      ctxS.strokeStyle = `hsla(${hue}, ${p.sat}%, ${p.lig}%, ${alpha})`;
      ctxS.lineWidth = p.lw;

      ctxS.shadowBlur = p.sh;
      ctxS.shadowColor = `hsla(${hue}, 40%, 80%, ${alpha * 0.55})`;

      ctxS.stroke();
      ctxS.restore();
    }
  }

  // ====== Main loop ======
  let frame = 0;
  let lastCaseAt = 0;

  function loop(){
    frame++;
    state.t = frame * 0.004;

    if(isTouch){
      const tt = frame * 0.006;
      state.tA = 0.52 + Math.sin(tt * 0.9) * 0.22;
      state.tW = 0.48 + Math.cos(tt * 0.7) * 0.20;
      state.mx = W*0.5 + Math.sin(tt*1.1) * (W*0.18);
      state.my = H*0.5 + Math.cos(tt*0.8) * (H*0.14);
    }

    state.A += (state.tA - state.A) * 0.040;
    state.W += (state.tW - state.W) * 0.040;

    const deltaV = state.fG2 ? 0.18 : 0.0;
    const deltaS = state.fG3 ? 0.08 : 0.0;
    const dragSpike = (!isTouch && state.dragging) ? 0.28 : 0.0;

    state.Wp = clamp01(state.W + deltaV + deltaS + dragSpike);

    const rawP = state.A * (1 - state.gamma * state.Wp);
    state.Pint = clamp01(rawP);

    if (uiP) uiP.textContent = state.Pint.toFixed(2);
    if (uiMeta) uiMeta.innerHTML =
      `ALIGNMENT <b>${state.A.toFixed(3)}</b><br/>` +
      `WORKLOAD W <b>${state.W.toFixed(3)}</b><br/>` +
      `FRICTION W' <b>${state.Wp.toFixed(3)}</b><br/>` +
      `NON-COMPLIANCE <b>${(state.noncompRate*100).toFixed(1)}%</b><br/>` +
      `MODE <b>${state.collapsed ? "RITUALIZATION COLLAPSE" : "PRODUCTIVE FRICTION"}</b>`;

    if (uiStatus) uiStatus.textContent = state.collapsed ? "COLLAPSE" : "STABLE FLOW";

    const gx = gateXs();
    const mGate = Math.max(0, Math.min(3, Math.floor((state.mx / Math.max(1,W)) * 4)));
    const activeAny = (!isTouch && state.dragging) || state.Wp > 0.55;

    gateEls.forEach((el,i)=>{
      el.classList.toggle("active", activeAny && i===mGate);
      el.classList.toggle("warn",
        (i===0 && state.fG1) ||
        (i===1 && state.fG2) ||
        (i===2 && state.fG3) ||
        (i===3 && state.pendingFlagged && (state.pendingAIwrong || state.overrideRequested))
      );
    });

    // ====== Dust render ======
    updateField(state.t);

    ctxD.globalCompositeOperation = "source-over";
    ctxD.fillStyle = "rgba(7,7,7,0.86)";
    ctxD.fillRect(0,0,W,H);

    ctxD.globalCompositeOperation = "lighter";

    const g1x = gx[0], g4x = gx[3];
    const cluster = state.pendingFlagged ? (0.6 + state.A*0.6) : 0.0;

    for(let i=0;i<PARTICLES;i++){
      const cx = Math.floor(P.x[i]/FIELD_RES);
      const cy = Math.floor(P.y[i]/FIELD_RES);
      let fx=1, fy=0;
      if(cx>=0 && cx<cols && cy>=0 && cy<rows){
        const idx = (cx + cy*cols)*2;
        fx = field[idx]; fy = field[idx+1];
      }

      const mass = P.s[i];
      const speed = (1.2 + (1-P.z[i])*2.6) * (1 + state.Wp*0.9);

      P.vx[i] += (fx*speed - P.vx[i]) * (0.10 + (1-mass)*0.02);
      P.vy[i] += (fy*speed - P.vy[i]) * (0.10 + (1-mass)*0.02);

      if (cluster > 0){
        const dx = g4x - P.x[i];
        P.vx[i] += dx * 0.00018 * cluster;
      }

      if (state.collapsed) P.vy[i] += 0.010 + state.Wp*0.006;

      P.x[i] += P.vx[i];
      P.y[i] += P.vy[i];

      if(P.x[i] > W){ P.x[i]=0; P.y[i]=Math.random()*H; }
      if(P.x[i] < 0){ P.x[i]=W; }
      if(P.y[i] > H){ P.y[i]=0; }
      if(P.y[i] < 0){ P.y[i]=H; }

      if(state.fG1 && P.x[i] < g1x + 18){
        resetParticle(i, Math.random()*W, Math.random()*H);
        continue;
      }

      const vel = Math.hypot(P.vx[i], P.vy[i]);
      const bright = 0.25 + Math.min(1, vel/6.5) * 0.75;
      const alpha = (1-P.z[i]) * bright;

      let h,s,l;
      if(state.collapsed || state.Wp > 0.78){
        h = 350; s = 82; l = 58 + bright*18;
      } else if (P.t[i]===0){
        h = 42; s = 62; l = 68 + bright*10;
      } else {
        h = 200; s = 10; l = 80 + bright*8;
      }

      ctxD.fillStyle = `hsla(${h},${s}%,${l}%,${alpha})`;
      const wRect = P.s[i] + vel*0.55;
      ctxD.fillRect(P.x[i], P.y[i], wRect, P.s[i]);
    }

    // ====== Strands update + render ======
    const stiffness = state.collapsed ? 0.03 : (0.20 + state.A*0.85);
    const gravity = state.collapsed ? (0.12 + state.Wp*0.18) : 0.0;
    const drag = state.collapsed ? 0.945 : 0.962;

    const g2x = gx[1], g3x = gx[2];

    for(const st of strands){
      const pts = st.pts;

      for(let i=0;i<pts.length;i++){
        const p = pts[i];
        if(p.pin) continue;

        const amp = state.Wp * (state.collapsed ? 2.0 : 0.55);
        p.x += Math.sin(state.t*2.2 + i*0.22 + st.ns) * amp;
        p.y += Math.cos(state.t*2.8 + i*0.28) * amp;

        const dx2 = g2x - p.x;
        const d2 = Math.abs(dx2);
        if(d2 < 140){
          const pull = Math.cos((d2/140)*(Math.PI/2));
          const twist = (p.y - H*0.5) * 0.0022 * pull * (state.fG2 ? 2.1 : 0.9);
          p.x += twist * (H*0.5 - p.y) * 0.08;
          p.y += twist * (p.x - g2x) * 0.08;
        }

        const dx3 = g3x - p.x;
        const d3 = Math.abs(dx3);
        if(d3 < 140){
          const pull = Math.cos((d3/140)*(Math.PI/2));
          const lag = (state.fG3 ? 0.18 : 0.08) * pull;
          p.x += (p.ox - p.x) * lag;
          p.y += (p.oy - p.y) * lag;
        }

        if(!state.collapsed && state.pendingFlagged){
          const dx4 = gx[3] - p.x;
          const d4 = Math.abs(dx4);
          if(d4 < 170){
            const pull = Math.cos((d4/170)*(Math.PI/2));
            const ydist = (H*0.5 - p.y);
            p.y += ydist * pull * (0.07 + state.A*0.12);
          }
        }

        p.step(drag, gravity);
      }

      for(let k=0;k<ITER;k++){
        for(const ln of st.links) ln.solve(stiffness);
      }
    }

    ctxS.clearRect(0,0,W,H);
    ctxS.globalCompositeOperation = "screen";

    const ab = state.Wp * (state.collapsed ? 3.2 : 1.6);
    const rgbPasses = [
      { r:255,g:80, b:60,  ox:+ab, oy:0 },
      { r:60, g:255,b:90,  ox:0,   oy:0 },
      { r:120,g:200,b:255, ox:-ab, oy:0 },
    ];

    for(const pass of rgbPasses){
      ctxS.save();
      ctxS.translate(pass.ox, pass.oy);

      for(const st of strands){
        const pts = st.pts;
        ctxS.beginPath();
        ctxS.moveTo(pts[0].x, pts[0].y);
        for(let i=1;i<pts.length-1;i++){
          const xc = (pts[i].x + pts[i+1].x)/2;
          const yc = (pts[i].y + pts[i+1].y)/2;
          ctxS.quadraticCurveTo(pts[i].x, pts[i].y, xc, yc);
        }
        ctxS.lineTo(pts[pts.length-1].x, pts[pts.length-1].y);

        let a = state.collapsed ? 0.035 : 0.075;
        a *= (1 - Math.abs(st.ns));
        if(!state.collapsed) a += state.A * 0.09;

        ctxS.strokeStyle = `rgba(${pass.r},${pass.g},${pass.b},${a})`;
        ctxS.lineWidth = state.collapsed ? 1.0 : 1.4;
        ctxS.stroke();
      }

      ctxS.restore();
    }

    drawTruthLineSpectral();

    if(frame - lastCaseAt > 96){
      lastCaseAt = frame;
      stepCase();
    }

    requestAnimationFrame(loop);
  }

  // boot
  resize();
  logADR({ auditable: true, line: `[${nowHHMMSS()}] boot · desktop: move mouse (A/W), drag to spike workload, press O to Override · mobile: auto-run.` });
  requestAnimationFrame(loop);
})();
