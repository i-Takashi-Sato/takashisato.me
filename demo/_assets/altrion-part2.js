const clamp01 = v => Math.max(0, Math.min(1, v));
const lerp = (a,b,t) => a + (b-a)*t;
let entropy = 0;
let target = 0;

const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d', { alpha:false });
canvas.style.position = 'fixed';
canvas.style.inset = '0';
canvas.style.width = '100vw';
canvas.style.height = '100vh';
canvas.style.zIndex = '0';
canvas.style.pointerEvents = 'none';
document.body.appendChild(canvas);

const ui = {
  slider: document.getElementById('entropy-slider'),
  hit: document.getElementById('slider-hit'),
  wrap: document.getElementById('slider-wrap'),
  progress: document.getElementById('progress-bar'),
  num: document.getElementById('ph-num'),
  title: document.getElementById('ph-title'),
  desc: document.getElementById('ph-desc'),
  badge: document.getElementById('ph-badge'),
  items: Array.from(document.querySelectorAll('.traj-item')),
  mForms: document.getElementById('m-forms'),
  mExc: document.getElementById('m-exc'),
  mLat: document.getElementById('m-lat'),
  mLiab: document.getElementById('m-liab')
};

const phases = [
  ['Formal Coherence','The system looks perfect: rules close into a self-consistent loop. Compliance is legible; responsibility is covered. The hidden cost is only deferred.','STATUS: NOMINAL'],
  ['Cognitive Offload','Operational pressure rises. People stop thinking in first principles and begin thinking in checklists. Judgment migrates from humans into protocol.','STATUS: LOADING'],
  ['Liability Hardening','Responsibility inverts. The system optimizes for defensibility, not truth. More gates, more forms, less nuance.','STATUS: DEFENSIVE'],
  ['Operational Entropy','Daily work heats the machine. Exceptions accumulate; attention fragments; coordination liquefies.','STATUS: DEGRADING'],
  ['Legibility Capture','Reality is forced into a grid for reporting. Complexity is quantized into static categories.','STATUS: ARCHIVED']
];

let W=0,H=0,DPR=1,points=[];
function resize(){
  DPR = Math.min(window.devicePixelRatio || 1, window.innerWidth <= 820 ? 1.5 : 2);
  W = Math.max(1, window.innerWidth);
  H = Math.max(1, window.innerHeight);
  canvas.width = Math.floor(W*DPR);
  canvas.height = Math.floor(H*DPR);
  ctx.setTransform(DPR,0,0,DPR,0,0);
  build();
}

function build(){
  const n = W <= 430 ? 15000 : W <= 820 ? 22000 : 42000;
  points = new Array(n);
  for(let i=0;i<n;i++){
    const a = Math.random()*Math.PI*2;
    const b = Math.random()*Math.PI*2;
    const r = (0.22 + Math.random()*0.58) * Math.min(W,H) * 0.82;
    const twist = Math.sin(a*3.0+b*2.0)*0.42;
    const x = W*0.52 + Math.cos(a+twist)*Math.sin(b)*r;
    const y = H*0.36 + Math.sin(a+twist)*Math.sin(b)*r*0.72;
    points[i] = {x,y,z:Math.cos(b),s:Math.random(),d:Math.random()-0.5};
  }
}

function setEntropy(v){
  target = clamp01(v);
  if(ui.slider) ui.slider.value = target;
  if(ui.progress) ui.progress.style.width = `${target*100}%`;
}
function setFromX(x){
  if(!ui.wrap) return;
  const r = ui.wrap.getBoundingClientRect();
  setEntropy((x-r.left)/Math.max(1,r.width));
}
let drag=false;
ui.hit?.addEventListener('pointerdown',e=>{drag=true;setFromX(e.clientX);e.preventDefault();},{passive:false});
ui.hit?.addEventListener('pointermove',e=>{if(drag){setFromX(e.clientX);e.preventDefault();}},{passive:false});
ui.hit?.addEventListener('pointerup',()=>{drag=false},{passive:true});
ui.slider?.addEventListener('input',e=>setEntropy(parseFloat(e.target.value)),{passive:true});
ui.items.forEach((el,i)=>el.addEventListener('click',()=>setEntropy(i/4),{passive:true}));

let last=-1;
function updateUI(t){
  const i = Math.min(4, Math.floor(entropy*4.999));
  if(i!==last){
    last=i;
    if(ui.num) ui.num.innerText=`PHASE 0${i}`;
    if(ui.title) ui.title.innerText=phases[i][0];
    if(ui.desc) ui.desc.innerText=phases[i][1];
    if(ui.badge) ui.badge.innerText=phases[i][2];
    ui.items.forEach((el,n)=>el.classList.toggle('active',n===i));
  }
  const root = document.documentElement.style;
  root.setProperty('--uiE', entropy.toFixed(6));
  root.setProperty('--uiDim', (entropy*.72).toFixed(6));
  root.setProperty('--uiNoise', (.08+entropy*.72).toFixed(6));
  root.setProperty('--uiBlur', Math.max(0,entropy-.60).toFixed(6));
  root.setProperty('--uiSkew', (entropy*.72).toFixed(6));
  root.setProperty('--uiRuleBoost', entropy.toFixed(6));
  root.setProperty('--uiGoldMute', Math.max(0,entropy-.55).toFixed(6));
  root.setProperty('--uiLetter', (entropy*.72).toFixed(6));
  root.setProperty('--uiScan', Math.max(0,entropy-.55).toFixed(6));
  root.setProperty('--uiFlicker', (t*(1+entropy*5)).toFixed(6));
  root.setProperty('--hudGlow', (entropy*.7).toFixed(6));
  root.setProperty('--stamp', Math.max(0,entropy-.42).toFixed(6));
  root.setProperty('--stampRot', `${(t*(6+entropy*12)).toFixed(3)}deg`);
  root.setProperty('--gate0','1');
  root.setProperty('--gate1',Math.max(0,(entropy-.18)*5).toFixed(6));
  root.setProperty('--gate2',Math.max(0,(entropy-.42)*4.5).toFixed(6));
  root.setProperty('--gate3',Math.max(0,(entropy-.70)*4.5).toFixed(6));
  if(ui.mForms) ui.mForms.innerText = String(Math.floor(18+entropy*988)).padStart(3,'0').slice(-3);
  if(ui.mExc) ui.mExc.innerText = String(Math.floor(entropy*entropy*540)).padStart(3,'0').slice(-3);
  if(ui.mLat) ui.mLat.innerText = `${(0.45+entropy*14.2).toFixed(1)}d`;
  if(ui.mLiab) ui.mLiab.innerText = clamp01(.08+entropy*.86).toFixed(2);
}

function draw(t){
  entropy += (target-entropy)*0.04;
  ctx.fillStyle = '#050507';
  ctx.fillRect(0,0,W,H);
  const cx = W*.52 + Math.sin(t*.00008)*W*.03;
  const cy = H*.35;
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const alphaBase = W <= 430 ? .33 : .44;
  ctx.fillStyle = `rgba(232,230,223,${alphaBase*(1-entropy*.34)})`;
  for(const p of points){
    const drift = entropy*entropy;
    const x = cx + (p.x-W*.52) + Math.sin(t*.00022+p.s*9+p.y*.01)*drift*38 + p.d*drift*42;
    const y = cy + (p.y-H*.36) - drift*(26+Math.abs(p.d)*82);
    if(y > H*.55 && W <= 820 && p.s < .55) continue;
    const size = (p.s<.92?0.62:1.05) * (1-entropy*.25);
    ctx.fillRect(x,y,size,size);
  }
  ctx.restore();
  const g = ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'rgba(0,0,0,.16)');
  g.addColorStop(.55,'rgba(0,0,0,.10)');
  g.addColorStop(1,'rgba(0,0,0,.30)');
  ctx.fillStyle = g;
  ctx.fillRect(0,0,W,H);
  updateUI(t*.001);
  requestAnimationFrame(draw);
}

window.addEventListener('resize',resize,{passive:true});
if(window.visualViewport) window.visualViewport.addEventListener('resize',resize,{passive:true});
window.addEventListener('load',()=>{
  const l = document.getElementById('loader');
  if(l){ l.style.opacity='0'; setTimeout(()=>l.remove(),700); }
  setEntropy(0);
  resize();
  requestAnimationFrame(draw);
},{passive:true});
