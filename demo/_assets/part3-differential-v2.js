(() => {
  const canvas = document.getElementById('differentialCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d', { alpha: true });
  const phaseSequence = document.getElementById('phaseSequence');
  const phaseTimeline = document.getElementById('phaseTimeline');
  const mobileGdi = document.getElementById('mobileGdi');
  const lead = document.getElementById('leadText');
  const status = document.getElementById('statusLine');
  const srStatus = document.getElementById('srStatus');
  const advance = document.getElementById('advancePhase');
  const intervene = document.getElementById('intervenePhase');
  const reset = document.getElementById('resetPhase');

  const phases = [
    { id:'00', label:'Surface', note:'Plural judgment exists. Diversity intact.', lead:'The governance field remains plural. Judgment still has contour, hesitation, and reversible doubt.', sed:.22, tc:.18, ed:.16, cb:.04, speed:1.05, spread:1.00, lever:0, memory:0 },
    { id:'01', label:'Order', note:'Procedure begins. Variance reduces.', lead:'Artificial order becomes visible. The system is beautiful, legible, and already beginning to close.', sed:.34, tc:.38, ed:.26, cb:.12, speed:1.36, spread:.72, lever:0, memory:0 },
    { id:'02', label:'Loop', note:'Synchronization increases.', lead:'The field folds into one decision-cycle. Review begins to imitate thought.', sed:.50, tc:.70, ed:.50, cb:.30, speed:1.82, spread:.42, lever:.05, memory:0 },
    { id:'03', label:'Silence', note:'All channels converge. Judgment collapses.', lead:'Motion continues. Judgment no longer oscillates. Resolution collapses into procedural stillness.', sed:.18, tc:.88, ed:.82, cb:.55, speed:.82, spread:.10, lever:.18, memory:0 },
    { id:'04', label:'Circuit Breaker', note:'Intervention lever engages. System arrested.', lead:'The mechanism is arrested, not destroyed. A human stop-line enters the differential core.', sed:.24, tc:.74, ed:.86, cb:.95, speed:.44, spread:.06, lever:1, memory:.24 },
    { id:'05', label:'Proper Ending', note:'Motion ceases. Memory preserved.', lead:'The system stopped without erasing memory. Authority returns; the record remains legible.', sed:.12, tc:.52, ed:.92, cb:1, speed:0, spread:0, lever:1, memory:1 }
  ];

  const keys = [
    ['SED','Semantic Entropy Decay','sed'],
    ['TC','Temporal Compression','tc'],
    ['ED','Exhaustion of Dissent','ed'],
    ['CB','Circuit Breaker Readiness','cb']
  ];

  let phase = 0;
  let previousPhase = 0;
  let state = { ...phases[0], angle: 0, angle2: 0, angle3: 0, stop: 0 };
  let last = performance.now();
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  function makePhaseControls(){
    if (phaseSequence) {
      phaseSequence.innerHTML = phases.map((p,i)=>`<button class="phase-button" data-i="${i}" type="button"><span class="num">${p.id}</span><span class="label">${p.label}</span><span class="dot"></span></button>`).join('');
      phaseSequence.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => setPhase(Number(btn.dataset.i))));
    }
    if (phaseTimeline) {
      phaseTimeline.innerHTML = phases.map((p,i)=>`<div class="tile" data-i="${i}"><strong>${p.id} ${p.label}</strong><span>${p.note}</span></div>`).join('');
    }
    if (mobileGdi) {
      mobileGdi.innerHTML = keys.map(([k]) => `<span data-mobile="${k}">${k}<br><b>0.00</b></span>`).join('');
    }
  }

  function setPhase(i){
    phase = Math.max(0, Math.min(phases.length - 1, i));
    if (lead) lead.textContent = phases[phase].lead;
    if (status) status.textContent = `${phases[phase].id} ${phases[phase].label}`;
    if (srStatus) srStatus.textContent = `Phase ${phases[phase].id}: ${phases[phase].label}. ${phases[phase].note}`;
    updateActive();
  }

  function updateActive(){
    document.querySelectorAll('[data-i]').forEach(el => el.classList.toggle('active', Number(el.dataset.i) === phase));
  }

  function resize(){
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * dpr));
    canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }

  function lerp(a,b,t){ return a + (b-a)*t; }
  function polar(cx, cy, r, a){ return [cx + Math.cos(a)*r, cy + Math.sin(a)*r]; }
  function clamp(v){ return Math.max(0, Math.min(1, v)); }

  function strokeCircle(cx,cy,r, color, lw=1, start=0, end=Math.PI*2){
    ctx.beginPath(); ctx.arc(cx,cy,r,start,end); ctx.strokeStyle=color; ctx.lineWidth=lw; ctx.stroke();
  }

  function drawRegulator(cx,cy,r,ang,label,value,offset){
    ctx.save();
    ctx.translate(cx,cy);
    ctx.rotate(ang * .12);
    strokeCircle(0,0,r,`rgba(239,232,216,${.13 + value*.10})`,1);
    strokeCircle(0,0,r*.68,`rgba(220,193,121,${.12 + value*.12})`,1);
    strokeCircle(0,0,r*.28,'rgba(239,232,216,.20)',1);
    for(let i=0;i<8;i++){
      const a = offset + i*Math.PI/4;
      const p1 = polar(0,0,r*.20,a);
      const p2 = polar(0,0,r*.64,a);
      ctx.beginPath(); ctx.moveTo(p1[0],p1[1]); ctx.lineTo(p2[0],p2[1]); ctx.strokeStyle='rgba(239,232,216,.13)'; ctx.lineWidth=.8; ctx.stroke();
    }
    const p = polar(0,0,r*.58,offset*1.65);
    ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(p[0],p[1]); ctx.strokeStyle='rgba(220,193,121,.55)'; ctx.lineWidth=1.2; ctx.stroke();
    ctx.fillStyle='rgba(239,232,216,.80)'; ctx.beginPath(); ctx.arc(0,0,3,0,Math.PI*2); ctx.fill();
    ctx.restore();
    ctx.fillStyle='rgba(214,207,191,.78)'; ctx.font='600 9px Inter, sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(label,cx,cy);
  }

  function drawMemoryTrace(cx,cy,r,memory){
    if(memory <= .02) return;
    ctx.save();
    ctx.globalAlpha = memory*.9;
    ctx.beginPath();
    for(let i=0;i<160;i++){
      const t = i/159;
      const a = t*Math.PI*8 + state.angle*.002;
      const rr = r*(.10 + t*.74);
      const x = cx + Math.cos(a)*rr;
      const y = cy + Math.sin(a)*rr;
      if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle='rgba(220,193,121,.32)'; ctx.lineWidth=1; ctx.stroke();
    ctx.restore();
  }

  function draw(){
    const rect = canvas.getBoundingClientRect();
    const w = rect.width, h = rect.height;
    ctx.clearRect(0,0,w,h);
    const cx = w/2, cy = h/2;
    const R = Math.min(w,h)*.43;

    ctx.save();
    ctx.translate(cx,cy);
    const grad = ctx.createRadialGradient(0,0,R*.08,0,0,R*.78);
    grad.addColorStop(0,'rgba(239,232,216,.10)'); grad.addColorStop(.46,'rgba(185,157,87,.035)'); grad.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=grad; ctx.beginPath(); ctx.arc(0,0,R*.86,0,Math.PI*2); ctx.fill();
    ctx.restore();

    for(let i=0;i<5;i++) strokeCircle(cx,cy,R*(.38+i*.105),`rgba(239,232,216,${.06-i*.006})`,1);
    strokeCircle(cx,cy,R*.76,'rgba(220,193,121,.22)',1.1);
    strokeCircle(cx,cy,R*.22,'rgba(239,232,216,.18)',1);

    const locations = [
      [-.46,-.43,'SED',state.sed,state.angle], [.46,-.43,'TC',state.tc,-state.angle2],
      [-.46,.43,'ED',state.ed,state.angle3], [.46,.43,'CB',state.cb,-state.angle3]
    ];
    locations.forEach(([dx,dy,label,value,offset])=>{
      const x = cx + dx*R, y = cy + dy*R;
      ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(x,y); ctx.strokeStyle='rgba(239,232,216,.11)'; ctx.lineWidth=1; ctx.stroke();
      drawRegulator(x,y,R*.18,offset,label,value,offset*.03);
    });

    ctx.save(); ctx.translate(cx,cy); ctx.rotate(state.angle*.006);
    for(let i=0;i<16;i++){
      const a = i*Math.PI/8;
      const p1 = polar(0,0,R*.12,a), p2 = polar(0,0,R*.33,a);
      ctx.beginPath(); ctx.moveTo(p1[0],p1[1]); ctx.lineTo(p2[0],p2[1]); ctx.strokeStyle='rgba(239,232,216,.16)'; ctx.lineWidth=i%4===0?1.5:.8; ctx.stroke();
    }
    strokeCircle(0,0,R*.30,'rgba(239,232,216,.25)',1.2);
    strokeCircle(0,0,R*.18,'rgba(220,193,121,.28)',1);
    strokeCircle(0,0,R*.075,'rgba(239,232,216,.34)',1.5);
    ctx.restore();

    const lever = lerp(-Math.PI/2.8, -Math.PI/1.55, state.lever);
    const p0 = polar(cx,cy,R*.07,lever);
    const p1 = polar(cx,cy,R*.56,lever);
    ctx.beginPath(); ctx.moveTo(p0[0],p0[1]); ctx.lineTo(p1[0],p1[1]);
    ctx.strokeStyle=`rgba(220,193,121,${.32 + state.cb*.35})`; ctx.lineWidth=3; ctx.stroke();
    ctx.beginPath(); ctx.arc(p1[0],p1[1],R*.022,0,Math.PI*2); ctx.fillStyle='rgba(239,232,216,.75)'; ctx.fill();

    const gap = state.cb * .55;
    ctx.beginPath();
    ctx.arc(cx,cy,R*.64,-Math.PI*.18+gap,Math.PI*1.82-gap);
    ctx.strokeStyle=`rgba(239,232,216,${.20 + state.cb*.20})`; ctx.lineWidth=3; ctx.stroke();
    if(state.cb > .3){
      const g1 = polar(cx,cy,R*.64,-Math.PI*.18+gap), g2 = polar(cx,cy,R*.64,Math.PI*1.82-gap);
      [g1,g2].forEach(p=>{ctx.beginPath();ctx.arc(p[0],p[1],5,0,Math.PI*2);ctx.fillStyle='rgba(239,232,216,.86)';ctx.fill();ctx.shadowColor='rgba(220,193,121,.6)';ctx.shadowBlur=20;ctx.fill();ctx.shadowBlur=0;});
    }

    drawMemoryTrace(cx,cy,R*.52,state.memory);
    if(state.memory>.22){
      ctx.fillStyle=`rgba(239,232,216,${state.memory*.86})`;
      ctx.font='400 24px Cormorant Garamond, Georgia, serif'; ctx.textAlign='center';
      ctx.fillText('Memory',cx,cy-6); ctx.fillText('Preserved',cx,cy+18);
      ctx.fillStyle=`rgba(185,157,87,${state.memory*.82})`; ctx.font='600 8px Inter, sans-serif';
      ctx.fillText('AUTHORITY RETURNED / SYSTEM ENDED',cx,cy+38);
    }
  }

  function updateUI(){
    keys.forEach(([k,label,prop])=>{
      const v = clamp(state[prop]);
      document.querySelectorAll(`[data-gdi="${k}"]`).forEach(row=>{
        row.style.setProperty('--v', v.toFixed(4));
        const val = row.querySelector('.gdi-value'); if(val) val.textContent = v.toFixed(2);
      });
      document.querySelectorAll(`[data-mobile="${k}"] b`).forEach(el => el.textContent = v.toFixed(2));
    });
  }

  function tick(now){
    const dt = Math.min(2, (now-last)/16.6667); last = now;
    const target = phases[phase];
    const rate = reduceMotion.matches ? 1 : .055;
    ['sed','tc','ed','cb','speed','spread','lever','memory'].forEach(k=> state[k] = lerp(state[k], target[k], rate));
    if (phase !== previousPhase && phase === 5) state.stop = 0;
    previousPhase = phase;
    if (!reduceMotion.matches) {
      state.angle += state.speed * (1.45 + state.spread) * dt;
      state.angle2 += state.speed * (.92 + state.spread*.62) * dt;
      state.angle3 -= state.speed * (1.12 + state.spread*.44) * dt;
    }
    draw(); updateUI();
    requestAnimationFrame(tick);
  }

  makePhaseControls();
  keys.forEach(([k,label])=>{
    document.querySelectorAll(`[data-gdi="${k}"] .gdi-label`).forEach(el=>{el.innerHTML = `${k} <small>${label}</small>`;});
  });
  setPhase(0);
  resize();
  addEventListener('resize', resize, { passive:true });
  advance?.addEventListener('click', () => setPhase((phase + 1) % phases.length));
  intervene?.addEventListener('click', () => setPhase(4));
  reset?.addEventListener('click', () => setPhase(0));
  document.addEventListener('keydown', e => {
    if (e.code === 'Space') { e.preventDefault(); setPhase((phase + 1) % phases.length); }
    if (e.code === 'Enter') { e.preventDefault(); setPhase(4); }
    if (e.key.toLowerCase() === 'r') setPhase(0);
  });
  requestAnimationFrame(t => { last = t; tick(t); });
})();
