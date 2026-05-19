import * as THREE from "./vendor/three/three.module.js";
import { OrbitControls } from "./vendor/three/OrbitControls.js";

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const mix = (a, b, t) => a * (1 - t) + b * t;

function smoothstep(a, b, x){
  const t = clamp01((x - a) / Math.max(0.00001, b - a));
  return t * t * (3 - 2 * t);
}

const isMobile = window.innerWidth <= 820;
const isNarrow = window.innerWidth <= 430;
const dpr = Math.min(window.devicePixelRatio || 1, isMobile ? 1.65 : 2);

function particleBudget(){
  if (isNarrow) return 68000;
  if (isMobile) return 88000;
  return 170000;
}

const BUDGET = particleBudget();
const COUNTS = {
  primary: Math.floor(BUDGET * 0.62),
  veil: Math.floor(BUDGET * 0.28),
  dust: Math.max(8000, BUDGET - Math.floor(BUDGET * 0.90))
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
renderer.setPixelRatio(dpr);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = isMobile ? 1.02 : 1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.domElement.style.touchAction = "none";
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(isMobile ? 42 : 38, window.innerWidth / window.innerHeight, 0.1, 180);
camera.position.set(isMobile ? 0.4 : 2.0, isMobile ? 1.25 : 1.0, isMobile ? 34 : 31);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.075;
controls.enablePan = false;
controls.enableZoom = true;
controls.zoomSpeed = 0.65;
controls.enableRotate = true;
controls.rotateSpeed = 0.22;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.055;
controls.minPolarAngle = 1.02;
controls.maxPolarAngle = 1.54;
controls.minDistance = 24;
controls.maxDistance = 52;
controls.target.set(isMobile ? 0.8 : 2.2, isMobile ? 0.15 : 0.0, 0.0);

const commonUniforms = {
  uTime: { value: 0 },
  uEntropy: { value: 0 },
  uPixelRatio: { value: dpr },
  uViewport: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
};

const vertexShader = `
precision highp float;

uniform float uTime;
uniform float uEntropy;
uniform float uPixelRatio;
uniform float uSizeMul;
uniform float uAlphaMul;
uniform vec2 uViewport;

attribute vec3 aSeed;
attribute float aLayer;
attribute float aQuiet;

varying vec3 vColor;
varying float vAlpha;
varying float vSoft;

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
  vec4 p = permute(permute(permute(i.z + vec4(0.0, i1.z, i2.z, 1.0)) + i.y + vec4(0.0, i1.y, i2.y, 1.0)) + i.x + vec4(0.0, i1.x, i2.x, 1.0));
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

float sat(float x){ return clamp(x, 0.0, 1.0); }

void main(){
  float e = sat(uEntropy);
  float e1 = smoothstep(0.08, 0.34, e);
  float e2 = smoothstep(0.36, 0.70, e);
  float e3 = smoothstep(0.72, 1.00, e);

  vec3 pos = position;
  float s = aSeed.x;
  float lane = aSeed.y;
  float grain = aSeed.z;

  float horizontalDrift = (uTime * (0.020 + 0.030 * e) + s * 9.0);
  float n1 = snoise(vec3(pos.x * 0.055 + horizontalDrift, pos.y * 0.075, pos.z * 0.035));
  float n2 = snoise(vec3(pos.x * 0.032, pos.y * 0.044 + uTime * 0.045, s * 6.1));

  pos.x += (n1 * 0.42 + e1 * (lane - 0.5) * 1.4) * (1.0 + e * 0.8);
  pos.y += n2 * 0.30 - e2 * (0.7 + grain * 1.8);
  pos.z += n1 * 0.35 + e2 * sin(pos.x * 0.08 + uTime * 0.12) * 0.40;

  float bureaucraticCompression = smoothstep(0.42, 0.88, e);
  pos.y = mix(pos.y, floor(pos.y / 1.05 + 0.5) * 1.05, bureaucraticCompression * 0.36);
  pos.x = mix(pos.x, floor(pos.x / 1.85 + 0.5) * 1.85, e3 * 0.26);

  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mv;

  vec4 clip = projectionMatrix * mv;
  vec2 ndc = clip.xy / max(0.0001, clip.w);
  vec2 screen = ndc * 0.5 + 0.5;

  float panelMask = smoothstep(0.48, 0.64, screen.y);
  float lowerTextMask = 1.0 - panelMask;
  float quietZone = mix(1.0, 0.54, lowerTextMask) * mix(1.0, 0.72, aQuiet);

  float distanceFade = 1.0 - smoothstep(24.0, 58.0, abs(mv.z));
  float depthSize = 1.0 / max(0.0001, -mv.z);
  float baseSize = mix(22.0, 13.0, e) * mix(0.72, 1.10, aLayer);
  gl_PointSize = baseSize * uSizeMul * depthSize * uPixelRatio;

  vec3 bone = vec3(0.86, 0.84, 0.79);
  vec3 paper = vec3(0.72, 0.70, 0.66);
  vec3 ash = vec3(0.42, 0.42, 0.40);
  vec3 gold = vec3(0.70, 0.58, 0.26);
  vec3 iron = vec3(0.12, 0.12, 0.13);

  vec3 col = mix(bone, paper, aLayer * 0.45);
  col = mix(col, gold, e1 * 0.16);
  col = mix(col, ash, e2 * 0.34);
  col = mix(col, iron, e3 * 0.42);

  float localPulse = 0.82 + 0.18 * snoise(vec3(pos.x * 0.08, pos.y * 0.08, uTime * 0.10 + s * 4.0));
  float heroPreserve = mix(0.72, 1.00, smoothstep(0.60, 0.94, screen.y));

  vColor = col * localPulse;
  vSoft = mix(0.28, 0.58, aLayer);
  vAlpha = uAlphaMul * quietZone * heroPreserve * (0.64 + distanceFade * 0.32) * (1.0 - e3 * 0.22);
}
`;

const fragmentShader = `
precision highp float;

varying vec3 vColor;
varying float vAlpha;
varying float vSoft;

void main(){
  vec2 uv = gl_PointCoord - vec2(0.5);
  float r = length(uv);
  if (r > 0.5) discard;
  float core = 1.0 - smoothstep(0.0, 0.18, r);
  float edge = 1.0 - smoothstep(vSoft, 0.5, r);
  float alpha = edge * vAlpha;
  vec3 col = vColor + core * 0.08;
  gl_FragColor = vec4(col, alpha);
}
`;

function makeSedimentationGeometry(count, layer, seedOffset){
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const seeds = new Float32Array(count * 3);
  const layers = new Float32Array(count);
  const quiet = new Float32Array(count);

  for (let i = 0; i < count; i++){
    const u = Math.random();
    const v = Math.random();
    const band = Math.random();
    const side = Math.random() < 0.5 ? -1 : 1;

    const width = isMobile ? 22.0 : 25.0;
    const x = (u - 0.5) * width + side * Math.pow(Math.random(), 3.4) * 2.6;
    const sediment = Math.pow(v, 1.35);
    const baseY = mix(isMobile ? -8.2 : -7.4, isMobile ? 6.8 : 7.2, sediment);
    const slope = -0.16 * x + Math.sin(x * 0.34 + seedOffset * 4.0) * 0.65;
    const ridge = Math.sin((u * 9.0 + seedOffset) * Math.PI) * (0.35 + band * 0.55);
    const voidCut = 1.0 - Math.exp(-(x*x + (baseY + 1.0)*(baseY + 1.0)) / 38.0);

    const y = baseY + slope + ridge * voidCut + (Math.random() - 0.5) * (1.8 + layer * 2.2);
    const z = (Math.random() - 0.5) * (8.5 + layer * 8.0) + Math.sin(x * 0.18) * 1.1;

    positions[i * 3 + 0] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;

    seeds[i * 3 + 0] = (Math.random() + seedOffset) % 1;
    seeds[i * 3 + 1] = Math.random();
    seeds[i * 3 + 2] = Math.random();
    layers[i] = layer;

    const screenQuiet = y < (isMobile ? -1.5 : -2.0) ? 1.0 : 0.0;
    quiet[i] = screenQuiet;
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aSeed", new THREE.BufferAttribute(seeds, 3));
  geometry.setAttribute("aLayer", new THREE.BufferAttribute(layers, 1));
  geometry.setAttribute("aQuiet", new THREE.BufferAttribute(quiet, 1));
  geometry.computeBoundingSphere();
  return geometry;
}

function makeMaterial(sizeMul, alphaMul){
  return new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: commonUniforms.uTime,
      uEntropy: commonUniforms.uEntropy,
      uPixelRatio: commonUniforms.uPixelRatio,
      uViewport: commonUniforms.uViewport,
      uSizeMul: { value: sizeMul },
      uAlphaMul: { value: alphaMul }
    },
    transparent: true,
    depthWrite: false,
    blending: THREE.NormalBlending
  });
}

const group = new THREE.Group();
scene.add(group);

const primary = new THREE.Points(makeSedimentationGeometry(COUNTS.primary, 0.20, 0.13), makeMaterial(isMobile ? 0.88 : 1.00, isMobile ? 0.44 : 0.56));
const veil = new THREE.Points(makeSedimentationGeometry(COUNTS.veil, 0.78, 0.47), makeMaterial(isMobile ? 1.06 : 1.18, isMobile ? 0.22 : 0.30));
const dust = new THREE.Points(makeSedimentationGeometry(COUNTS.dust, 0.55, 0.79), makeMaterial(isMobile ? 0.60 : 0.70, isMobile ? 0.16 : 0.20));

primary.frustumCulled = false;
veil.frustumCulled = false;
dust.frustumCulled = false;

group.add(dust);
group.add(veil);
group.add(primary);

group.rotation.z = isMobile ? -0.05 : -0.04;
group.rotation.x = isMobile ? -0.04 : -0.02;
group.position.set(isMobile ? 1.4 : 2.8, isMobile ? 0.50 : 0.35, 0.0);

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
  { t:"Formal Coherence",    d:"Rules close into a self-consistent loop. The system is sound on paper. Costs are deferred into procedure, waiting to be paid by operators.", s:"STATUS: NOMINAL" },
  { t:"Cognitive Offload",   d:"Operational pressure rises. People stop thinking in first principles and begin thinking in checklists. Judgment migrates from humans into protocol.", s:"STATUS: LOADING" },
  { t:"Liability Hardening", d:"Responsibility inverts. The system optimizes for defensibility, not truth. Interfaces sharpen into spikes: more gates, more forms, less nuance.", s:"STATUS: DEFENSIVE" },
  { t:"Operational Entropy", d:"Daily work heats the machine. Exceptions accumulate; attention fragments; coordination liquefies. The structure drips into lower-energy routines.", s:"STATUS: DEGRADING" },
  { t:"Legibility Capture",  d:"Reality is forced into a grid for reporting. Complexity is quantized into static categories. The system survives as dead data — and loses the world.", s:"STATUS: ARCHIVED" }
];

function setEntropyUI(v){
  targetEntropy = clamp01(v);
  if (ui.slider) ui.slider.value = String(targetEntropy);
  if (ui.progress) ui.progress.style.width = (targetEntropy * 100) + "%";
}

function setFromClientX(clientX){
  if (!ui.wrap) return;
  const r = ui.wrap.getBoundingClientRect();
  const t = clamp01((clientX - r.left) / Math.max(1, r.width));
  setEntropyUI(t);
}

let dragging = false;
const onPointerDown = (e) => {
  dragging = true;
  ui.wrap?.setPointerCapture?.(e.pointerId);
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
  ui.wrap?.releasePointerCapture?.(e.pointerId);
  e.preventDefault();
};
ui.hit?.addEventListener("pointerdown", onPointerDown, { passive: false });
ui.hit?.addEventListener("pointermove", onPointerMove, { passive: false });
ui.hit?.addEventListener("pointerup", onPointerUp, { passive: false });
ui.hit?.addEventListener("pointercancel", onPointerUp, { passive: false });
ui.slider?.addEventListener("input", (e) => setEntropyUI(parseFloat(e.target.value)), { passive: true });
ui.items.forEach((el, i) => {
  const toPhase = () => setEntropyUI(i === 0 ? 0 : (i / 4));
  el.addEventListener("click", toPhase, { passive: true });
  el.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " "){
      e.preventDefault();
      toPhase();
    }
  }, { passive: false });
});

const panel = document.querySelector(".panel-glass");
panel?.addEventListener("wheel", (e) => {
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
}, { passive: true });

const rootStyle = document.documentElement.style;
const clock = new THREE.Clock();

function pad3(n){
  const s = String(Math.max(0, Math.floor(n)));
  if (s.length >= 3) return s.slice(-3);
  return ("000" + s).slice(-3);
}

function updateUI(time){
  const idx = Math.min(Math.floor(entropy * 4.999), 4);
  if (ui.title && ui.title.innerText !== phases[idx].t){
    if (ui.num) ui.num.innerText = `PHASE 0${idx}`;
    if (ui.title) ui.title.innerText = phases[idx].t;
    if (ui.desc) ui.desc.innerText = phases[idx].d;
    if (ui.badge) ui.badge.innerText = phases[idx].s;
    ui.items.forEach((el, i) => el.classList.toggle("active", i === idx));
  }

  const dim = smoothstep(0.32, 0.985, entropy) * 0.72;
  const noise = mix(0.05, 0.72, smoothstep(0.16, 0.96, entropy));
  const blur = mix(0.00, 0.68, smoothstep(0.65, 0.985, entropy));
  const skew = mix(0.00, 0.72, smoothstep(0.48, 0.93, entropy));
  const ruleBoost = mix(0.00, 0.74, smoothstep(0.22, 0.76, entropy));
  const goldMute = mix(0.00, 0.76, smoothstep(0.62, 1.00, entropy));
  const letter = mix(0.00, 0.70, smoothstep(0.30, 0.90, entropy));
  const scan = mix(0.00, 0.58, smoothstep(0.66, 0.985, entropy));
  const hudGlow = mix(0.00, 0.72, smoothstep(0.12, 0.55, entropy)) * (0.65 + 0.35 * Math.sin(time * 0.85));

  rootStyle.setProperty("--uiE", entropy.toFixed(6));
  rootStyle.setProperty("--uiDim", dim.toFixed(6));
  rootStyle.setProperty("--uiNoise", noise.toFixed(6));
  rootStyle.setProperty("--uiBlur", blur.toFixed(6));
  rootStyle.setProperty("--uiSkew", skew.toFixed(6));
  rootStyle.setProperty("--uiRuleBoost", ruleBoost.toFixed(6));
  rootStyle.setProperty("--uiGoldMute", goldMute.toFixed(6));
  rootStyle.setProperty("--uiLetter", letter.toFixed(6));
  rootStyle.setProperty("--uiScan", scan.toFixed(6));
  rootStyle.setProperty("--uiFlicker", (time * (1.0 + entropy * 4.0)).toFixed(6));
  rootStyle.setProperty("--hudGlow", hudGlow.toFixed(6));
  rootStyle.setProperty("--stamp", smoothstep(0.44, 0.82, entropy).toFixed(6));
  rootStyle.setProperty("--stampRot", `${(time * (4.0 + entropy * 9.0)).toFixed(3)}deg`);
  rootStyle.setProperty("--gate0", "1.000000");
  rootStyle.setProperty("--gate1", smoothstep(0.18, 0.38, entropy).toFixed(6));
  rootStyle.setProperty("--gate2", smoothstep(0.42, 0.64, entropy).toFixed(6));
  rootStyle.setProperty("--gate3", smoothstep(0.70, 0.92, entropy).toFixed(6));

  const forms = 18 + entropy * 988 + Math.sin(time * (0.55 + entropy * 0.85)) * 8.0;
  const exc = entropy * entropy * 540 + Math.sin(time * 0.75 + 1.2) * 6.0;
  const lat = 0.45 + entropy * 14.2 + Math.sin(time * 0.33 + entropy * 1.2) * 0.25;
  const liab = 0.08 + entropy * 0.86 + Math.sin(time * 0.48) * 0.02;
  if (ui.mForms) ui.mForms.innerText = pad3(forms);
  if (ui.mExc) ui.mExc.innerText = pad3(exc);
  if (ui.mLat) ui.mLat.innerText = `${Math.max(0, lat).toFixed(1)}d`;
  if (ui.mLiab) ui.mLiab.innerText = clamp01(liab).toFixed(2);
}

function animate(){
  requestAnimationFrame(animate);
  const time = clock.getElapsedTime();
  entropy += (targetEntropy - entropy) * 0.034;
  entropy = clamp01(entropy);

  commonUniforms.uTime.value = time;
  commonUniforms.uEntropy.value = entropy;

  const slow = mix(0.055, 0.025, smoothstep(0.35, 0.95, entropy));
  controls.autoRotateSpeed = slow;
  renderer.toneMappingExposure = mix(isMobile ? 1.00 : 1.10, isMobile ? 1.06 : 1.18, smoothstep(0.20, 0.72, entropy));

  group.rotation.y = Math.sin(time * 0.035) * 0.045;
  group.rotation.z = (isMobile ? -0.05 : -0.04) + Math.sin(time * 0.027) * 0.018;
  group.position.x = (isMobile ? 1.4 : 2.8) + Math.sin(time * 0.045) * 0.32;
  group.position.y = (isMobile ? 0.50 : 0.35) - entropy * 0.28;

  updateUI(time);
  controls.update();
  renderer.render(scene, camera);
}

function resize(){
  const w = Math.max(1, window.innerWidth);
  const h = Math.max(1, window.innerHeight);
  commonUniforms.uViewport.value.set(w, h);
  camera.aspect = w / h;
  camera.fov = w <= 820 ? 42 : 38;
  camera.position.set(w <= 820 ? 0.4 : 2.0, w <= 820 ? 1.25 : 1.0, w <= 820 ? 34 : 31);
  controls.target.set(w <= 820 ? 0.8 : 2.2, w <= 820 ? 0.15 : 0.0, 0.0);
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  const nextDpr = Math.min(window.devicePixelRatio || 1, w <= 820 ? 1.65 : 2);
  renderer.setPixelRatio(nextDpr);
  commonUniforms.uPixelRatio.value = nextDpr;
}

window.addEventListener("resize", resize, { passive: true });
if (window.visualViewport) window.visualViewport.addEventListener("resize", resize, { passive: true });

window.addEventListener("load", () => {
  setTimeout(() => {
    const l = document.getElementById("loader");
    if (!l) return;
    l.style.opacity = "0";
    setTimeout(() => l.remove(), 1400);
  }, 700);
  setEntropyUI(0);
  resize();
  animate();
}, { passive: true });
