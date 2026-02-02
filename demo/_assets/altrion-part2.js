import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";
import { OrbitControls } from "https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js";

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const mix = (a, b, t) => a * (1 - t) + b * t;

function smoothstep(a, b, x){
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
}

function chooseParticleBudget(){
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.max(1, window.innerWidth);
  const h = Math.max(1, window.innerHeight);
  const megapixels = (w * h * dpr * dpr) / 1_000_000;
  const base = 320_000;
  const k = 1 / Math.max(1.0, megapixels * 0.52);
  const budget = Math.floor(base * k);
  const coarse = w < 820 ? 1 : 0;
  const cap = coarse ? 190_000 : 340_000;
  return Math.max(150_000, Math.min(cap, budget));
}

const BUDGET = chooseParticleBudget();
const COUNTS = {
  core: Math.floor(BUDGET * 0.58),
  halo: Math.floor(BUDGET * 0.28),
  dust: Math.max(14_000, BUDGET - Math.floor(BUDGET * 0.86))
};

const CONFIG = {
  radius: 16,
  symmetry: 5,
  grid: 1.85,
  gridResidueCount: Math.min(16_000, Math.floor(BUDGET * 0.075))
};

let entropy = 0;
let targetEntropy = 0;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050507);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
  alpha: false,
  stencil: false,
  depth: true
});

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.55;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.domElement.style.touchAction = "none";
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.1, 240);

const commonUniforms = {
  uTime: { value: 0 },
  uEntropy: { value: 0 },
  uPixelRatio: { value: Math.min(window.devicePixelRatio || 1, 2) },
  uFocus: { value: 58.0 }
};

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.075;
controls.enablePan = false;
controls.enableZoom = true;
controls.zoomSpeed = 0.90;
controls.enableRotate = true;
controls.rotateSpeed = 0.38;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.14;
controls.minPolarAngle = 0.92;
controls.maxPolarAngle = 1.50;
controls.target.set(0.0, 0.0, 0.0);

const vertexShader = `
precision highp float;

uniform float uTime;
uniform float uEntropy;
uniform float uPixelRatio;
uniform float uSizeMul;
uniform float uAlphaMul;
uniform float uFocus;

attribute vec3 aRandom;
varying vec3 vColor;
varying float vAlpha;
varying float vBlur;
varying float vHeat;

vec3 mod289(vec3 x){ return x - floor(x*(1.0/289.0))*289.0; }
vec4 mod289(vec4 x){ return x - floor(x*(1.0/289.0))*289.0; }
vec4 permute(vec4 x){ return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314*r; }

float snoise(vec3 v){
  const vec2 C = vec2(1.0/6.0, 1.0/3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  i = mod289(i);
  vec4 p = permute( permute( permute(
    i.z + vec4(0.0, i1.z, i2.z, 1.0)) +
    i.y + vec4(0.0, i1.y, i2.y, 1.0)) +
    i.x + vec4(0.0, i1.x, i2.x, 1.0));
  float n_ = 0.142857142857;
  vec3 ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);
  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
  p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m*m;
  return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
}

vec3 curl(vec3 p){
  float e = 0.12;
  vec3 dx = vec3(e,0.0,0.0);
  vec3 dy = vec3(0.0,e,0.0);
  vec3 dz = vec3(0.0,0.0,e);
  float x = snoise(p + dy) - snoise(p - dy);
  float y = snoise(p + dz) - snoise(p - dz);
  float z = snoise(p + dx) - snoise(p - dx);
  return vec3(x,y,z);
}

float sat(float x){ return clamp(x,0.0,1.0); }

void main(){
  vec3 pos = position;
  float t = uTime;

  float e0 = sat(uEntropy);
  float e1 = smoothstep(0.02, 0.22, e0);
  float e2 = smoothstep(0.25, 0.60, e0);
  float e3 = smoothstep(0.55, 0.88, e0);
  float e4 = smoothstep(0.85, 1.00, e0);

  float seed = aRandom.x;
  float drift = aRandom.z;

  vec3 pN = pos * 0.16 + vec3(seed*7.1, seed*3.7, seed*5.9);

  if (e1 > 0.0){
    vec3 c = curl(pN * 2.2 + t * 0.82);
    pos += c * (0.95 + seed*0.6) * e1 * 0.46;
  }

  if (e2 > 0.0){
    float spike = max(0.0, sin(t * (1.6 + seed) + (pos.x*0.8 + pos.z*0.6) * 2.2));
    spike *= e2 * (2.0 + seed*2.4);
    vec3 dir = normalize(pos + 0.0001);
    pos += dir * spike;
  }

  if (e3 > 0.0){
    vec3 flow = curl(pN * 0.52 + t * 0.18);
    pos += flow * e3 * (4.1 + seed*2.0);
    pos.y -= e3 * (abs(drift) * 7.0 + 1.2);
  }

  if (e4 > 0.0){
    float grid = 1.85;
    vec3 snapped = floor(pos / grid + 0.5) * grid;
    pos = mix(pos, snapped, e4);
    vec3 scatter = (aRandom - 0.5) * 2.0;
    pos += scatter * e4 * 40.0;
  }

  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mv;

  float dist = length(mv.xyz);
  float dof = abs(dist - uFocus);
  float blur = smoothstep(0.0, 12.0, dof);
  vBlur = blur;

  float base = (66.0 + 30.0 * (1.0 - smoothstep(0.0, 1.0, e0))) * aRandom.y;
  float bokeh = (1.0 + blur * 2.25);
  gl_PointSize = base * uSizeMul * bokeh * (1.0 / max(0.0001, -mv.z)) * uPixelRatio;

  vec3 cMarble = vec3(0.99, 0.99, 0.995);
  vec3 cIris   = vec3(0.48, 0.50, 1.00);
  vec3 cVio    = vec3(0.28, 0.14, 0.78);
  vec3 cCrim   = vec3(0.66, 0.06, 0.08);
  vec3 cVoid   = vec3(0.03, 0.03, 0.035);

  vec3 col = cMarble;
  if (e0 <= 0.35) col = mix(cMarble, cIris, e0 * 2.857142857);
  else if (e0 <= 0.70) col = mix(cIris, cVio, (e0 - 0.35) * 2.857142857);
  else if (e0 <= 0.88) col = mix(cVio, cCrim, (e0 - 0.70) * 5.555555556);
  else col = mix(cCrim, cVoid, (e0 - 0.88) * 8.333333333);

  float heat = smoothstep(0.14, 0.58, e0) * (1.0 - smoothstep(0.62, 0.98, e0));
  vHeat = heat;

  float micro = snoise(pN * 2.4 + t * 0.25) * 0.09;
  col += vec3(0.44, 0.58, 1.0) * heat * 0.22;
  col += micro;

  vColor = col;

  float focusFade = 1.0 - blur * 0.50;
  float entropyFade = 1.0 - e4 * 0.30;
  vAlpha = uAlphaMul * focusFade * entropyFade;
}
`;

const fragmentShader = `
precision highp float;

varying vec3 vColor;
varying float vAlpha;
varying float vBlur;
varying float vHeat;

void main(){
  vec2 uv = gl_PointCoord - vec2(0.5);
  float r = length(uv);
  if (r > 0.5) discard;

  float hardness = 0.50 - (vBlur * 0.38);
  float alpha = 1.0 - smoothstep(hardness, 0.5, r);

  float core = 1.0 - smoothstep(0.0, 0.13, r);
  vec3 col = vColor + core * (0.22 + vHeat * 0.22);

  float edgeGlow = 1.0 - smoothstep(0.22, 0.5, r);
  col += edgeGlow * (0.10 + vHeat * 0.10);

  gl_FragColor = vec4(col, alpha * vAlpha);
}
`;

function buildGeometry(count, radius, seedShift){
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const randoms = new Float32Array(count * 3);
  const scale = radius * 0.52;

  for (let i = 0; i < count; i++){
    const u = Math.random() * Math.PI * 2;
    const v = Math.random() * Math.PI * 2;
    const r = (3.05 + Math.cos(5.0 * u) * 0.62 + Math.sin(5.0 * v) * 0.58) * 0.86;

    let x = r * Math.cos(u) * Math.sin(v);
    let y = r * Math.sin(u) * Math.sin(v);
    let z = r * Math.cos(v);

    const twist = Math.sin(x * 0.52 + y * 0.50) * 2.10;
    const x2 = x * Math.cos(twist) - y * Math.sin(twist);
    const y2 = x * Math.sin(twist) + y * Math.cos(twist);
    x = x2; y = y2;

    positions[i * 3 + 0] = x * scale;
    positions[i * 3 + 1] = y * scale;
    positions[i * 3 + 2] = z * scale;

    const s = Math.random();
    randoms[i * 3 + 0] = (s + seedShift) % 1.0;
    randoms[i * 3 + 1] = 0.58 + Math.random() * 0.42;
    randoms[i * 3 + 2] = (Math.random() - 0.5);
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aRandom", new THREE.BufferAttribute(randoms, 3));
  geometry.computeBoundingSphere();
  return geometry;
}

function makeLayerMaterial(sizeMul, alphaMul){
  return new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: commonUniforms.uTime,
      uEntropy: commonUniforms.uEntropy,
      uPixelRatio: commonUniforms.uPixelRatio,
      uFocus: commonUniforms.uFocus,
      uSizeMul: { value: sizeMul },
      uAlphaMul: { value: alphaMul }
    },
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending
  });
}

const geoCore = buildGeometry(COUNTS.core, CONFIG.radius, 0.13);
const geoHalo = buildGeometry(COUNTS.halo, CONFIG.radius, 0.47);
const geoDust = buildGeometry(COUNTS.dust, CONFIG.radius, 0.79);

const matCore = makeLayerMaterial(1.00, 1.05);
const matHalo = makeLayerMaterial(1.28, 0.70);
const matDust = makeLayerMaterial(0.78, 0.42);

const ptsCore = new THREE.Points(geoCore, matCore);
const ptsHalo = new THREE.Points(geoHalo, matHalo);
const ptsDust = new THREE.Points(geoDust, matDust);

ptsCore.frustumCulled = false;
ptsHalo.frustumCulled = false;
ptsDust.frustumCulled = false;

scene.add(ptsDust);
scene.add(ptsHalo);
scene.add(ptsCore);

const residueGeom = new THREE.BufferGeometry();
const residuePos = new Float32Array(CONFIG.gridResidueCount * 3);

{
  const src = geoCore.attributes.position.array;
  const n = Math.min(CONFIG.gridResidueCount, Math.floor(src.length / 3));
  const grid = CONFIG.grid;

  for (let i = 0; i < n; i++){
    const j = (Math.floor(Math.random() * (src.length / 3))) * 3;

    let x = src[j + 0];
    let y = src[j + 1];
    let z = src[j + 2];

    x = Math.round(x / grid) * grid;
    y = Math.round(y / grid) * grid;
    z = Math.round(z / grid) * grid;

    residuePos[i * 3 + 0] = x;
    residuePos[i * 3 + 1] = y;
    residuePos[i * 3 + 2] = z;
  }

  residueGeom.setAttribute("position", new THREE.BufferAttribute(residuePos, 3));
  residueGeom.computeBoundingSphere();
}

const residueMat = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
  uniforms: {
    uTime: commonUniforms.uTime,
    uEntropy: commonUniforms.uEntropy,
    uPixelRatio: commonUniforms.uPixelRatio
  },
  vertexShader: `
precision highp float;
uniform float uTime;
uniform float uEntropy;
uniform float uPixelRatio;
varying float vA;

void main(){
  vec3 pos = position;
  float e4 = smoothstep(0.85, 1.0, uEntropy);

  float trem = (sin(uTime * 0.9 + pos.x*0.08) + sin(uTime*1.3 + pos.y*0.06)) * 0.03;
  pos += vec3(trem, -trem*0.35, trem*0.25) * (1.0 - e4) * 0.45;

  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mv;

  float s = 22.0;
  gl_PointSize = s * (1.0 / max(0.0001, -mv.z)) * uPixelRatio;

  vA = e4;
}
`,
  fragmentShader: `
precision highp float;
varying float vA;

void main(){
  vec2 uv = gl_PointCoord - vec2(0.5);
  float r = length(uv);
  if (r > 0.5) discard;

  float a = 1.0 - smoothstep(0.18, 0.5, r);
  vec3 c = vec3(0.99, 0.99, 1.0);
  c += (1.0 - smoothstep(0.0, 0.12, r)) * 0.22;

  gl_FragColor = vec4(c, a * vA * 0.92);
}
`
});

const residuePts = new THREE.Points(residueGeom, residueMat);
residuePts.frustumCulled = false;
scene.add(residuePts);

{
  const r = (geoCore.boundingSphere?.radius || 26.0) * 1.14;
  const fov = (camera.fov * Math.PI) / 180.0;
  const fit = r / Math.sin(fov * 0.50);

  camera.position.set(0.0, r * 0.18, fit * 1.05);

  controls.minDistance = fit * 0.72;
  controls.maxDistance = fit * 2.35;

  controls.update();
  commonUniforms.uFocus.value = fit * 0.92;
}

const ui = {
  slider: document.getElementById("entropy-slider"),
  hit: document.getElementById("slider-hit"),
  wrap: document.getElementById("slider-wrap"),
  progress: document.getElementById("progress-bar"),
  num: document.getElementById("ph-num"),
  title: document.getElementById("ph-title"),
  desc: document.getElementById("ph-desc"),
  badge: document.getElementById("ph-badge"),
  items: Array.from(document.querySelectorAll(".traj-item")),
  mForms: document.getElementById("m-forms"),
  mExc: document.getElementById("m-exc"),
  mLat: document.getElementById("m-lat"),
  mLiab: document.getElementById("m-liab")
};

const phases = [
  { t:"Formal Coherence",    d:"Rules close into a self-consistent loop. The system is “sound” on paper. Costs are deferred into procedure, waiting to be paid by operators.", s:"STATUS: NOMINAL" },
  { t:"Cognitive Offload",   d:"Operational pressure rises. People stop thinking in first principles and begin thinking in checklists. Judgment migrates from humans into protocol.", s:"STATUS: LOADING" },
  { t:"Liability Hardening", d:"Responsibility inverts. The system optimizes for defensibility, not truth. Interfaces sharpen into spikes: more gates, more forms, less nuance.", s:"STATUS: DEFENSIVE" },
  { t:"Operational Entropy", d:"Daily work heats the machine. Exceptions accumulate; attention fragments; coordination liquefies. The structure drips into lower-energy routines.", s:"STATUS: DEGRADING" },
  { t:"Legibility Capture",  d:"Reality is forced into a grid for reporting. Complexity is quantized into static categories. The system survives as dead data — and loses the world.", s:"STATUS: ARCHIVED" }
];

function setEntropyUI(v){
  targetEntropy = clamp01(v);
  ui.slider.value = String(targetEntropy);
  ui.progress.style.width = (targetEntropy * 100) + "%";
}

function setFromClientX(clientX){
  const r = ui.wrap.getBoundingClientRect();
  const t = clamp01((clientX - r.left) / Math.max(1, r.width));
  setEntropyUI(t);
}

let dragging = false;

const onPointerDown = (e) => {
  dragging = true;
  ui.wrap.setPointerCapture?.(e.pointerId);
  setFromClientX(e.clientX);
  e.preventDefault();
};

const onPointerMove = (e) => {
  if (!dragging) return;
  setFromClientX(e.clientX);
  e.preventDefault();
};

const onPointerUp = (e) => {
  dragging = false;
  ui.wrap.releasePointerCapture?.(e.pointerId);
  e.preventDefault();
};

ui.hit.addEventListener("pointerdown", onPointerDown, { passive: false });
ui.hit.addEventListener("pointermove", onPointerMove, { passive: false });
ui.hit.addEventListener("pointerup", onPointerUp, { passive: false });
ui.hit.addEventListener("pointercancel", onPointerUp, { passive: false });

ui.items.forEach((el, i) => {
  el.setAttribute("role", "button");
  el.setAttribute("tabindex", "0");
  const toPhase = () => setEntropyUI(i === 0 ? 0 : (i / 4));
  el.addEventListener("click", toPhase, { passive: true });
  el.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " "){
      e.preventDefault();
      toPhase();
    }
  }, { passive: false });
});

{
  const panel = document.querySelector(".panel-glass");
  const forwardWheel = (e) => {
    renderer.domElement.dispatchEvent(new WheelEvent("wheel", {
      bubbles: true,
      cancelable: true,
      composed: true,
      deltaMode: e.deltaMode,
      deltaX: e.deltaX,
      deltaY: e.deltaY,
      deltaZ: e.deltaZ,
      clientX: e.clientX,
      clientY: e.clientY,
      ctrlKey: e.ctrlKey,
      shiftKey: e.shiftKey,
      altKey: e.altKey,
      metaKey: e.metaKey
    }));
  };
  panel.addEventListener("wheel", forwardWheel, { passive: true });
}

const rootStyle = document.documentElement.style;
const clock = new THREE.Clock();

function phaseImpulse(time, entropyNow){
  const thresholds = [0.25, 0.55, 0.85];
  let imp = 0.0;
  for (let i = 0; i < thresholds.length; i++){
    const x = entropyNow - thresholds[i];
    imp += Math.exp(-Math.abs(x) * 55.0) * 0.022;
  }
  imp *= (0.35 + 0.65 * Math.min(1.0, entropyNow * 1.6));
  imp *= (0.5 + 0.5 * Math.sin(time * 6.5));
  return imp;
}

function pad3(n){
  const s = String(Math.max(0, Math.floor(n)));
  if (s.length >= 3) return s.slice(-3);
  return ("000" + s).slice(-3);
}

function animate(){
  requestAnimationFrame(animate);

  const time = clock.getElapsedTime();

  entropy += (targetEntropy - entropy) * 0.032;
  entropy = clamp01(entropy);

  commonUniforms.uTime.value = time;
  commonUniforms.uEntropy.value = entropy;

  {
    const d = camera.position.distanceTo(controls.target);
    commonUniforms.uFocus.value = mix(54.0, d, 0.72);
  }

  {
    const base = 0.16;
    const slow = mix(base, 0.07, smoothstep(0.35, 0.95, entropy));
    const micro = (Math.sin(time * 0.55) + Math.sin(time * 1.11 + 1.7)) * 0.032;
    controls.autoRotateSpeed = slow * (1.0 + micro);
  }

  renderer.toneMappingExposure = 1.55 + phaseImpulse(time, entropy);

  const rotSpeed = 0.10 + entropy * 0.22;
  ptsCore.rotation.y = time * rotSpeed * 0.28;
  ptsCore.rotation.z = time * rotSpeed * 0.10;

  ptsHalo.rotation.y = time * rotSpeed * 0.26 + 0.22;
  ptsHalo.rotation.z = time * rotSpeed * 0.08 + 0.10;

  ptsDust.rotation.y = time * rotSpeed * 0.20 + 0.44;
  ptsDust.rotation.z = time * rotSpeed * 0.06 + 0.18;

  residuePts.rotation.y = time * 0.035;
  residuePts.rotation.z = time * 0.018;

  const idx = Math.min(Math.floor(entropy * 4.999), 4);
  if (ui.title.innerText !== phases[idx].t){
    ui.num.innerText = `PHASE 0${idx}`;
    ui.title.innerText = phases[idx].t;
    ui.desc.innerText = phases[idx].d;
    ui.badge.innerText = phases[idx].s;

    ui.items.forEach((el, i) => {
      if (i === idx) el.classList.add("active");
      else el.classList.remove("active");
    });
  }

  const dim = smoothstep(0.30, 0.985, entropy);
  const noise = mix(0.08, 1.00, smoothstep(0.12, 0.96, entropy));
  const blur = mix(0.00, 1.00, smoothstep(0.60, 0.985, entropy));
  const skew = mix(0.00, 1.00, smoothstep(0.45, 0.93, entropy));
  const ruleBoost = mix(0.00, 1.00, smoothstep(0.18, 0.76, entropy));
  const letter = mix(0.00, 1.00, smoothstep(0.28, 0.90, entropy));
  const scan = mix(0.00, 1.00, smoothstep(0.66, 0.985, entropy));
  const hudGlow = mix(0.00, 1.00, smoothstep(0.10, 0.55, entropy)) * (0.65 + 0.35 * Math.sin(time * 0.85));

  const stamp = smoothstep(0.44, 0.82, entropy);
  const stampRot = (time * (6.0 + entropy * 12.0)) * (0.35 + 0.65 * stamp);

  const g0 = 1.0;
  const g1 = smoothstep(0.18, 0.38, entropy);
  const g2 = smoothstep(0.42, 0.64, entropy);
  const g3 = smoothstep(0.70, 0.92, entropy);

  rootStyle.setProperty("--uiE", entropy.toFixed(6));
  rootStyle.setProperty("--uiDim", dim.toFixed(6));
  rootStyle.setProperty("--uiNoise", noise.toFixed(6));
  rootStyle.setProperty("--uiBlur", blur.toFixed(6));
  rootStyle.setProperty("--uiSkew", skew.toFixed(6));
  rootStyle.setProperty("--uiRuleBoost", ruleBoost.toFixed(6));
  rootStyle.setProperty("--uiLetter", letter.toFixed(6));
  rootStyle.setProperty("--uiScan", scan.toFixed(6));
  rootStyle.setProperty("--uiFlicker", (time * (1.0 + entropy * 6.0)).toFixed(6));
  rootStyle.setProperty("--hudGlow", hudGlow.toFixed(6));

  rootStyle.setProperty("--stamp", stamp.toFixed(6));
  rootStyle.setProperty("--stampRot", `${stampRot.toFixed(3)}deg`);

  rootStyle.setProperty("--gate0", g0.toFixed(6));
  rootStyle.setProperty("--gate1", g1.toFixed(6));
  rootStyle.setProperty("--gate2", g2.toFixed(6));
  rootStyle.setProperty("--gate3", g3.toFixed(6));

  const forms = 18 + entropy * 988 + (Math.sin(time * (0.55 + entropy * 0.85)) * 8.0);
  const exc = entropy * entropy * 540 + (Math.sin(time * 0.75 + 1.2) * 6.0);
  const lat = 0.45 + entropy * 14.2 + (Math.sin(time * 0.33 + entropy * 1.2) * 0.25);
  const liab = 0.08 + entropy * 0.86 + (Math.sin(time * 0.48) * 0.02);

  ui.mForms.innerText = pad3(forms);
  ui.mExc.innerText = pad3(exc);
  ui.mLat.innerText = `${Math.max(0, lat).toFixed(1)}d`;
  ui.mLiab.innerText = clamp01(liab).toFixed(2);

  controls.update();
  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  const w = Math.max(1, window.innerWidth);
  const h = Math.max(1, window.innerHeight);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  commonUniforms.uPixelRatio.value = Math.min(window.devicePixelRatio || 1, 2);
}, { passive: true });

window.onload = () => {
  setTimeout(() => {
    const l = document.getElementById("loader");
    if (!l) return;
    l.style.opacity = "0";
    setTimeout(() => l.remove(), 1800);
  }, 900);
  setEntropyUI(0);
  animate();
};
