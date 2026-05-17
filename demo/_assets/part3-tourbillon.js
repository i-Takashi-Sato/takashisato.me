(() => {
  const frame = document.querySelector('.demo-page--part3 .frame');
  if (!frame || document.querySelector('.governance-tourbillon')) return;

  const tourbillon = document.createElement('div');
  tourbillon.className = 'governance-tourbillon';
  tourbillon.setAttribute('aria-hidden', 'true');
  tourbillon.innerHTML = `
    <div class="tourbillon-cage"></div>
    <div class="tourbillon-gap"></div>
    <div class="tourbillon-breath"></div>
    <div class="tourbillon-nodes"></div>
    <div class="tourbillon-epitaph"><b>Memory<br>Preserved</b><small>Authority returned / System ended</small></div>
  `;
  frame.appendChild(tourbillon);

  const nodes = tourbillon.querySelector('.tourbillon-nodes');
  const nodeCount = window.matchMedia('(pointer: coarse)').matches ? 30 : 54;
  const frag = document.createDocumentFragment();
  for (let i = 0; i < nodeCount; i++) {
    const n = document.createElement('i');
    const angle = (360 / nodeCount) * i + ((i % 5) * 2.7);
    const radius = 23 + ((i * 37) % 36);
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
  ledger.innerHTML = `<strong>ADR Ledger / Proper Ending</strong><code>[14:00:32] SED below threshold
[14:00:33] Temporal variance collapsed
[14:00:34] Dissent exhausted
[14:00:35] Irreversible threshold crossed
[14:00:36] Circuit Breaker activated
[14:00:36] Authority returned to institution
[14:00:36] Memory preserved. System ended.</code>`;
  frame.appendChild(ledger);

  const phaseButtons = () => Array.from(document.querySelectorAll('.phase-item, #mobilePhase button'));
  const targets = [
    { sed:.86, tc:.12, ed:.08, cb:.00, node:.62, ring:.66, breath:.00, memory:.00 },
    { sed:.66, tc:.34, ed:.16, cb:.00, node:.52, ring:.62, breath:.00, memory:.00 },
    { sed:.36, tc:.76, ed:.46, cb:.00, node:.36, ring:.56, breath:.00, memory:.00 },
    { sed:.07, tc:.92, ed:.88, cb:.04, node:.14, ring:.28, breath:.00, memory:.00 },
    { sed:.20, tc:.78, ed:.82, cb:.68, node:.22, ring:.36, breath:.92, memory:.00 },
    { sed:.05, tc:.45, ed:.95, cb:1.00, node:.10, ring:.18, breath:.44, memory:1.00 }
  ];
  let phase = 0;
  let state = { ...targets[0], p:0 };

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
    tourbillon.style.setProperty('--p', state.p.toFixed(4));
    tourbillon.style.setProperty('--sed', state.sed.toFixed(4));
    tourbillon.style.setProperty('--tc', state.tc.toFixed(4));
    tourbillon.style.setProperty('--ed', state.ed.toFixed(4));
    tourbillon.style.setProperty('--cb', state.cb.toFixed(4));
    tourbillon.style.setProperty('--node-alpha', state.node.toFixed(4));
    tourbillon.style.setProperty('--ring-alpha', state.ring.toFixed(4));
    tourbillon.style.setProperty('--breath', state.breath.toFixed(4));
    tourbillon.style.setProperty('--memory', state.memory.toFixed(4));
    const vals = [state.sed, state.tc, state.ed, state.cb];
    ['SED','TC','ED','CB'].forEach((k, i) => {
      if (readoutVals[k]) readoutVals[k].textContent = vals[i].toFixed(2);
      if (bars[i]) bars[i].style.setProperty('--v', vals[i].toFixed(4));
    });
  }

  phaseButtons().forEach(el => el.addEventListener('click', () => requestAnimationFrame(detectPhase), { passive:true }));
  document.addEventListener('keydown', () => requestAnimationFrame(detectPhase), { passive:true });

  function tick() {
    detectPhase();
    const target = targets[phase] || targets[0];
    const rate = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 1 : .045;
    for (const k of ['sed','tc','ed','cb','node','ring','breath','memory']) state[k] += (target[k] - state[k]) * rate;
    state.p += (0.002 + state.tc * .004) * (1 - state.memory * .82);
    setVars();
    requestAnimationFrame(tick);
  }
  setVars();
  requestAnimationFrame(() => { detectPhase(); tick(); });
})();
