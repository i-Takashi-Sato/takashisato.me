(() => {
  const frame = document.querySelector('.demo-page--part3 .frame');
  if (!frame || document.querySelector('.governance-tourbillon')) return;

  const tourbillon = document.createElement('div');
  tourbillon.className = 'governance-tourbillon';
  tourbillon.setAttribute('aria-hidden', 'true');
  tourbillon.innerHTML = `
    <div class="differential-lines"></div>
    <div class="differential-inputs">
      <i class="diff-channel sed" data-k="SED"></i>
      <i class="diff-channel tc" data-k="TC"></i>
      <i class="diff-channel ed" data-k="ED"></i>
      <i class="diff-channel cb" data-k="CB"></i>
    </div>
    <div class="tourbillon-cage"></div>
    <div class="escapement-bar"></div>
    <div class="tourbillon-gap"></div>
    <div class="tourbillon-breath"></div>
    <div class="tourbillon-nodes"></div>
    <div class="tourbillon-epitaph"><b>Memory<br>Preserved</b><small>Authority returned / System ended</small></div>
  `;
  frame.appendChild(tourbillon);

  const nodes = tourbillon.querySelector('.tourbillon-nodes');
  const nodeCount = window.matchMedia('(pointer: coarse)').matches ? 34 : 64;
  const frag = document.createDocumentFragment();
  for (let i = 0; i < nodeCount; i++) {
    const n = document.createElement('i');
    const angle = (360 / nodeCount) * i + ((i % 7) * 2.4);
    const radius = 25 + ((i * 37) % 34);
    n.style.setProperty('--a', `${angle}deg`);
    n.style.setProperty('--r', String(radius));
    frag.appendChild(n);
  }
  nodes.appendChild(frag);

  const readout = document.createElement('div');
  readout.className = 'tourbillon-readout';
  readout.innerHTML = ['SED','TC','ED','CB'].map(k => `<span><b>${k}</b><i style="--v:.5"></i><b data-k="${k}">0.00</b></span>`).join('');
  frame.appendChild(readout);

  const ledger = document.createElement('div');
  ledger.className = 'tourbillon-ledger';
  ledger.innerHTML = `<strong>Caseback Record / Proper Ending</strong><code>SED below threshold
Temporal variance collapsed
Dissent exhausted
Circuit breaker activated
Authority returned
Memory preserved</code>`;
  frame.appendChild(ledger);

  const phaseButtons = () => Array.from(document.querySelectorAll('.phase-item, #mobilePhase button'));
  const targets = [
    { sed:.86, tc:.12, ed:.08, cb:.00, node:.62, ring:.66, breath:.00, memory:.00, spin:1.08, precess:.38, tertiary:.72, wobble:.70, breathPulse:.00 },
    { sed:.66, tc:.34, ed:.16, cb:.00, node:.52, ring:.62, breath:.00, memory:.00, spin:1.46, precess:.54, tertiary:.90, wobble:.46, breathPulse:.00 },
    { sed:.36, tc:.76, ed:.46, cb:.00, node:.36, ring:.56, breath:.00, memory:.00, spin:1.88, precess:.82, tertiary:1.08, wobble:.24, breathPulse:.00 },
    { sed:.07, tc:.92, ed:.88, cb:.04, node:.14, ring:.28, breath:.00, memory:.00, spin:.72, precess:.32, tertiary:.44, wobble:.06, breathPulse:.00 },
    { sed:.20, tc:.78, ed:.82, cb:.72, node:.22, ring:.36, breath:.82, memory:.00, spin:.58, precess:.20, tertiary:.32, wobble:.18, breathPulse:.86 },
    { sed:.05, tc:.45, ed:.95, cb:1.00, node:.10, ring:.18, breath:.34, memory:1.00, spin:0.00, precess:0.00, tertiary:0.00, wobble:.00, breathPulse:.10 }
  ];

  let phase = 0;
  let lastPhase = 0;
  let state = { ...targets[0], p:0, rot:0, rot2:0, rot3:0, wobblePhase:0, breathPhase:0 };
  let lastTime = performance.now();

  function detectPhase() {
    const active = document.querySelector('.phase-item.active') || document.querySelector('#mobilePhase button.active');
    const idx = active ? Number(active.dataset.i) : 0;
    if (Number.isFinite(idx)) phase = Math.max(0, Math.min(5, idx));
  }

  const readoutVals = {
    SED: readout.querySelector('[data-k="SED"]'),
    TC: readout.querySelector('[data-k="TC"]'),
    ED: readout.querySelector('[data-k="ED"]'),
    CB: readout.querySelector('[data-k="CB"]')
  };
  const bars = Array.from(readout.querySelectorAll('i'));

  function setVars() {
    const wobbleX = Math.sin(state.wobblePhase) * state.wobble * 7;
    const wobbleY = Math.cos(state.wobblePhase * .82) * state.wobble * 5;
    const breathY = Math.sin(state.breathPhase) * state.breathPulse * 4;
    const vars = {
      '--p': state.p.toFixed(4),
      '--sed': state.sed.toFixed(4),
      '--tc': state.tc.toFixed(4),
      '--ed': state.ed.toFixed(4),
      '--cb': state.cb.toFixed(4),
      '--node-alpha': state.node.toFixed(4),
      '--ring-alpha': state.ring.toFixed(4),
      '--breath': state.breath.toFixed(4),
      '--memory': state.memory.toFixed(4),
      '--rot': state.rot.toFixed(3),
      '--rot2': state.rot2.toFixed(3),
      '--rot3': state.rot3.toFixed(3),
      '--wobble-x': `${wobbleX.toFixed(2)}px`,
      '--wobble-y': `${wobbleY.toFixed(2)}px`,
      '--breath-y': `${breathY.toFixed(2)}px`
    };
    for (const [k, v] of Object.entries(vars)) {
      tourbillon.style.setProperty(k, v);
      frame.style.setProperty(k, v);
    }
    frame.dataset.phase = String(phase);
    const vals = [state.sed, state.tc, state.ed, state.cb];
    ['SED','TC','ED','CB'].forEach((k, i) => {
      if (readoutVals[k]) readoutVals[k].textContent = vals[i].toFixed(2);
      if (bars[i]) bars[i].style.setProperty('--v', vals[i].toFixed(4));
    });
  }

  phaseButtons().forEach(el => el.addEventListener('click', () => requestAnimationFrame(detectPhase), { passive:true }));
  document.addEventListener('keydown', () => requestAnimationFrame(detectPhase), { passive:true });

  function tick(now) {
    detectPhase();
    const dt = Math.min(2.2, (now - lastTime) / 16.6667);
    lastTime = now;
    const target = targets[phase] || targets[0];
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const rate = reduced ? 1 : .055;

    for (const k of ['sed','tc','ed','cb','node','ring','breath','memory','spin','precess','tertiary','wobble','breathPulse']) state[k] += (target[k] - state[k]) * rate;

    if (phase !== lastPhase && phase === 5) state.breathPhase = 0;
    lastPhase = phase;

    state.p += (0.002 + state.tc * .004) * dt * (1 - state.memory * .86);
    state.rot += state.spin * 1.68 * dt;
    state.rot2 += state.precess * 2.18 * dt;
    state.rot3 += state.tertiary * -1.74 * dt;
    state.wobblePhase += (0.015 + state.spin * .01) * dt;
    state.breathPhase += (0.045 + state.breathPulse * .035) * dt;

    if (reduced && phase === 5) {
      state.rot = 0;
      state.rot2 = 0;
      state.rot3 = 0;
      state.wobblePhase = 0;
      state.breathPhase = 0;
    }

    setVars();
    requestAnimationFrame(tick);
  }

  setVars();
  requestAnimationFrame((t) => { detectPhase(); lastTime = t; tick(t); });
})();
