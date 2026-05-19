import * as THREE from "./vendor/three/three.module.js";
import { OrbitControls } from "./vendor/three/OrbitControls.js";

(() => {
  const canvas = document.getElementById("differentialCanvas");
  if (!canvas) return;

  const phaseSequence = document.getElementById("phaseSequence");
  const phaseTimeline = document.getElementById("phaseTimeline");
  const mobileGdi = document.getElementById("mobileGdi");
  const lead = document.getElementById("leadText");
  const status = document.getElementById("statusLine");
  const srStatus = document.getElementById("srStatus");
  const advance = document.getElementById("advancePhase");
  const intervene = document.getElementById("intervenePhase");
  const reset = document.getElementById("resetPhase");

  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)") || { matches: false };

  const phases = [
    { id:"00", label:"Surface", note:"Plural judgment exists. Diversity intact.", lead:"The governance field remains plural. Judgment still has contour, hesitation, and reversible doubt.", sed:.22, tc:.18, ed:.16, cb:.04, speed:1.05, spread:1.00, lever:0, memory:0, authority:0, collapse:0 },
    { id:"01", label:"Order", note:"Procedure begins. Variance reduces.", lead:"Artificial order becomes visible. The system is beautiful, legible, and already beginning to close.", sed:.34, tc:.38, ed:.26, cb:.12, speed:1.36, spread:.72, lever:.02, memory:0, authority:0, collapse:.08 },
    { id:"02", label:"Loop", note:"Synchronization increases.", lead:"The field folds into one decision-cycle. Review begins to imitate thought.", sed:.50, tc:.70, ed:.50, cb:.30, speed:1.82, spread:.42, lever:.08, memory:.03, authority:0, collapse:.28 },
    { id:"03", label:"Silence", note:"All channels converge. Judgment collapses.", lead:"Motion continues. Judgment no longer oscillates. Resolution collapses into procedural stillness.", sed:.18, tc:.88, ed:.82, cb:.55, speed:.82, spread:.10, lever:.22, memory:.10, authority:.04, collapse:.66 },
    { id:"04", label:"Circuit Breaker", note:"Intervention lever engages. System arrested.", lead:"The mechanism is arrested, not destroyed. A human stop-line enters the differential core.", sed:.24, tc:.74, ed:.86, cb:.95, speed:.36, spread:.06, lever:1, memory:.38, authority:.58, collapse:.88 },
    { id:"05", label:"Proper Ending", note:"Motion ceases. Memory preserved.", lead:"The system stopped without erasing memory. Authority returns; the record remains legible.", sed:.12, tc:.52, ed:.92, cb:1, speed:0, spread:0, lever:1, memory:1, authority:1, collapse:1 }
  ];

  const keys = [
    ["SED", "Semantic Entropy Decay", "sed"],
    ["TC", "Temporal Compression", "tc"],
    ["ED", "Exhaustion of Dissent", "ed"],
    ["CB", "Circuit Breaker Readiness", "cb"]
  ];

  let phase = 0;
  const state = { ...phases[0], theta: 0, micro: 0 };
  const target = () => phases[phase];

  function clamp01(v){ return Math.max(0, Math.min(1, v)); }
  function lerp(a, b, t){ return a + (b - a) * t; }
  function smooth(a, b, x){
    const t = clamp01((x - a) / Math.max(0.0001, b - a));
    return t * t * (3 - 2 * t);
  }

  function makePhaseControls(){
    if (phaseSequence) {
      phaseSequence.innerHTML = phases.map((p, i) => `<button class="phase-button" data-i="${i}" type="button"><span class="num">${p.id}</span><span class="label">${p.label}</span><span class="dot"></span></button>`).join("");
      phaseSequence.querySelectorAll("button").forEach(btn => btn.addEventListener("click", () => setPhase(Number(btn.dataset.i))));
    }
    if (phaseTimeline) {
      phaseTimeline.innerHTML = phases.map((p, i) => `<div class="tile" data-i="${i}"><strong>${p.id} ${p.label}</strong><span>${p.note}</span></div>`).join("");
      phaseTimeline.querySelectorAll(".tile").forEach(tile => tile.addEventListener("click", () => setPhase(Number(tile.dataset.i))));
    }
    if (mobileGdi) mobileGdi.innerHTML = keys.map(([k]) => `<span data-mobile="${k}">${k}<br><b>0.00</b></span>`).join("");
  }

  function setPhase(i){
    phase = Math.max(0, Math.min(phases.length - 1, i));
    if (lead) lead.textContent = target().lead;
    if (status) status.textContent = `${target().id} ${target().label}`;
    if (srStatus) srStatus.textContent = `Phase ${target().id}: ${target().label}. ${target().note}`;
    updateActive();
  }

  function updateActive(){
    document.querySelectorAll("[data-i]").forEach(el => el.classList.toggle("active", Number(el.dataset.i) === phase));
  }

  makePhaseControls();
  setPhase(0);

  const scene = new THREE.Scene();
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
    stencil: false,
    depth: true
  });
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.18;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.style.touchAction = "none";

  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 120);
  camera.position.set(0, 0.18, 8.4);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.075;
  controls.enablePan = false;
  controls.enableZoom = true;
  controls.zoomSpeed = 0.58;
  controls.rotateSpeed = 0.28;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.08;
  controls.minDistance = 5.6;
  controls.maxDistance = 12.5;
  controls.minPolarAngle = 0.82;
  controls.maxPolarAngle = 2.12;

  scene.add(new THREE.AmbientLight(0xd8cfbd, 0.48));
  const key = new THREE.PointLight(0xdcc179, 1.45, 18);
  key.position.set(2.5, 3.2, 5.8);
  scene.add(key);
  const cold = new THREE.PointLight(0xb7c8ff, 0.28, 16);
  cold.position.set(-3.5, -1.8, 4.2);
  scene.add(cold);

  const root = new THREE.Group();
  root.rotation.x = -0.08;
  scene.add(root);

  const colors = {
    bone: 0xefe8d8,
    dim: 0x8f8472,
    gold: 0xb99d57,
    gold2: 0xdcc179,
    black: 0x050504,
    stop: 0xf2e8c7
  };

  const materialBank = {
    bone: new THREE.MeshStandardMaterial({ color: colors.bone, metalness: .72, roughness: .34, transparent: true, opacity: .36 }),
    gold: new THREE.MeshStandardMaterial({ color: colors.gold2, metalness: .84, roughness: .28, transparent: true, opacity: .58, emissive: colors.gold, emissiveIntensity: .05 }),
    dim: new THREE.MeshStandardMaterial({ color: colors.dim, metalness: .68, roughness: .46, transparent: true, opacity: .20 }),
    stop: new THREE.MeshStandardMaterial({ color: colors.stop, metalness: .88, roughness: .22, transparent: true, opacity: .76, emissive: colors.gold2, emissiveIntensity: .08 }),
    dark: new THREE.MeshStandardMaterial({ color: colors.black, metalness: .9, roughness: .52, transparent: true, opacity: .80 })
  };

  const lineMaterials = {
    conduit: new THREE.LineBasicMaterial({ color: colors.bone, transparent: true, opacity: .16 }),
    gold: new THREE.LineBasicMaterial({ color: colors.gold2, transparent: true, opacity: .36 }),
    memory: new THREE.LineBasicMaterial({ color: colors.gold2, transparent: true, opacity: .22 }),
    authority: new THREE.LineBasicMaterial({ color: colors.stop, transparent: true, opacity: 0 })
  };

  function addTorus(parent, radius, tube, mat, z = 0){
    const mesh = new THREE.Mesh(new THREE.TorusGeometry(radius, tube, 12, 192), mat.clone());
    mesh.position.z = z;
    parent.add(mesh);
    return mesh;
  }

  function makeLine(points, material){
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    return line;
  }

  function makeArc(radius, start, end, segments, material, z = 0){
    const pts = [];
    for (let i = 0; i <= segments; i++){
      const t = i / segments;
      const a = start + (end - start) * t;
      pts.push(new THREE.Vector3(Math.cos(a) * radius, Math.sin(a) * radius, z));
    }
    return makeLine(pts, material);
  }

  const outerRing = addTorus(root, 3.05, .010, materialBank.bone, 0);
  const evidenceRing = addTorus(root, 2.64, .007, materialBank.dim, -.012);
  const breakerRing = new THREE.Group();
  breakerRing.add(makeArc(2.25, -Math.PI * .88, Math.PI * .12, 144, lineMaterials.gold, .028));
  breakerRing.add(makeArc(2.25, Math.PI * .22, Math.PI * 1.02, 128, lineMaterials.gold, .028));
  root.add(breakerRing);

  const core = new THREE.Group();
  root.add(core);
  const coreOuter = addTorus(core, .86, .018, materialBank.gold, .03);
  const coreInner = addTorus(core, .52, .010, materialBank.bone, .055);
  const coreHub = new THREE.Mesh(new THREE.SphereGeometry(.085, 28, 16), materialBank.stop.clone());
  coreHub.position.z = .08;
  core.add(coreHub);

  const spokes = new THREE.Group();
  for (let i = 0; i < 18; i++){
    const a = (i / 18) * Math.PI * 2;
    const line = makeLine([
      new THREE.Vector3(Math.cos(a) * .17, Math.sin(a) * .17, .075),
      new THREE.Vector3(Math.cos(a) * .78, Math.sin(a) * .78, .075)
    ], i % 3 === 0 ? lineMaterials.gold : lineMaterials.conduit);
    spokes.add(line);
  }
  core.add(spokes);

  const teeth = new THREE.Group();
  const toothGeo = new THREE.BoxGeometry(.035, .18, .034);
  for (let i = 0; i < 24; i++){
    const a = (i / 24) * Math.PI * 2;
    const m = new THREE.Mesh(toothGeo, materialBank.bone);
    m.position.set(Math.cos(a) * .99, Math.sin(a) * .99, .045);
    m.rotation.z = a;
    teeth.add(m);
  }
  core.add(teeth);

  const conduitGroup = new THREE.Group();
  root.add(conduitGroup);
  const regulators = [];
  const locations = [
    [-1.72, 1.40, "SED", "sed"],
    [1.72, 1.40, "TC", "tc"],
    [-1.72, -1.40, "ED", "ed"],
    [1.72, -1.40, "CB", "cb"]
  ];

  function makeLabelTexture(text){
    const labelCanvas = document.createElement("canvas");
    labelCanvas.width = 512;
    labelCanvas.height = 192;
    const labelCtx = labelCanvas.getContext("2d");
    labelCtx.clearRect(0, 0, labelCanvas.width, labelCanvas.height);
    labelCtx.fillStyle = "rgba(239,232,216,.88)";
    labelCtx.font = "600 72px Inter, sans-serif";
    labelCtx.textAlign = "center";
    labelCtx.textBaseline = "middle";
    labelCtx.fillText(text, 256, 96);
    const texture = new THREE.CanvasTexture(labelCanvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
    return texture;
  }

  locations.forEach(([x, y, label, prop], i) => {
    conduitGroup.add(makeLine([new THREE.Vector3(0, 0, -.02), new THREE.Vector3(x, y, -.02)], lineMaterials.conduit));
    const g = new THREE.Group();
    g.position.set(x, y, .03);
    const ringA = addTorus(g, .42, .010, materialBank.bone, 0);
    const ringB = addTorus(g, .28, .006, materialBank.gold, .025);
    const needle = makeLine([new THREE.Vector3(0, 0, .06), new THREE.Vector3(0, .31, .06)], lineMaterials.gold);
    g.add(needle);
    const jewel = new THREE.Mesh(new THREE.SphereGeometry(.036, 20, 12), materialBank.gold.clone());
    jewel.position.z = .08;
    g.add(jewel);
    const spriteMaterial = new THREE.SpriteMaterial({ map: makeLabelTexture(label), transparent: true, opacity: .72, depthWrite: false });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(.42, .16, 1);
    sprite.position.z = .12;
    g.add(sprite);
    root.add(g);
    regulators.push({ group: g, ringA, ringB, needle, jewel, prop, index: i, spriteMaterial });
  });

  const leverGroup = new THREE.Group();
  leverGroup.position.z = .14;
  const leverGeo = new THREE.BoxGeometry(.052, 2.38, .052);
  leverGeo.translate(0, 1.19, 0);
  const leverArm = new THREE.Mesh(leverGeo, materialBank.stop.clone());
  leverGroup.add(leverArm);
  const leverCap = new THREE.Mesh(new THREE.SphereGeometry(.082, 24, 14), materialBank.stop.clone());
  leverCap.position.y = 2.38;
  leverGroup.add(leverCap);
  root.add(leverGroup);

  const stops = new THREE.Group();
  [-0.78, 0.78].forEach(sign => {
    const stop = new THREE.Mesh(new THREE.SphereGeometry(.058, 24, 14), materialBank.stop.clone());
    stop.position.set(Math.cos(sign) * 2.25, Math.sin(sign) * 2.25, .12);
    stops.add(stop);
  });
  root.add(stops);

  const memoryGroup = new THREE.Group();
  const memoryPoints = [];
  for (let i = 0; i < 220; i++){
    const t = i / 219;
    const a = t * Math.PI * 7.5;
    const r = .34 + t * 2.05;
    memoryPoints.push(new THREE.Vector3(Math.cos(a) * r, Math.sin(a) * r, .10 + t * .06));
  }
  const memoryTrace = makeLine(memoryPoints, lineMaterials.memory);
  memoryGroup.add(memoryTrace);
  root.add(memoryGroup);

  const beamMaterial = new THREE.LineBasicMaterial({ color: colors.stop, transparent: true, opacity: 0 });
  const authorityBeam = makeLine([
    new THREE.Vector3(.02, .02, .16),
    new THREE.Vector3(1.14, -.42, .18),
    new THREE.Vector3(2.52, -1.10, .16),
    new THREE.Vector3(3.18, -1.62, .12)
  ], beamMaterial);
  root.add(authorityBeam);

  const particleCount = 1100;
  const particleGeometry = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);
  const particleSeeds = new Float32Array(particleCount);
  for (let i = 0; i < particleCount; i++){
    const a = Math.random() * Math.PI * 2;
    const band = Math.random();
    const radius = 1.0 + Math.random() * 2.28;
    const yWarp = (Math.random() - .5) * .36 * (1 - band) + Math.sin(a * 3) * .04;
    particlePositions[i * 3 + 0] = Math.cos(a) * radius;
    particlePositions[i * 3 + 1] = Math.sin(a) * radius + yWarp;
    particlePositions[i * 3 + 2] = (Math.random() - .5) * .34;
    particleSeeds[i] = Math.random();
  }
  particleGeometry.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
  particleGeometry.setAttribute("aSeed", new THREE.BufferAttribute(particleSeeds, 1));
  const particleMaterial = new THREE.PointsMaterial({ color: colors.bone, size: .017, transparent: true, opacity: .18, depthWrite: false, blending: THREE.AdditiveBlending });
  const particles = new THREE.Points(particleGeometry, particleMaterial);
  root.add(particles);

  const inscriptionTexture = makeLabelTexture("MEMORY PRESERVED / AUTHORITY RETURNED");
  const inscriptionMaterial = new THREE.SpriteMaterial({ map: inscriptionTexture, transparent: true, opacity: 0, depthWrite: false });
  const inscription = new THREE.Sprite(inscriptionMaterial);
  inscription.scale.set(2.0, .42, 1);
  inscription.position.set(0, -.12, .46);
  root.add(inscription);

  function updateUI(){
    keys.forEach(([k, label, prop]) => {
      const v = clamp01(state[prop]);
      document.querySelectorAll(`[data-gdi="${k}"]`).forEach(row => {
        row.style.setProperty("--v", v.toFixed(4));
        const val = row.querySelector(".gdi-value");
        if (val) val.textContent = v.toFixed(2);
      });
      document.querySelectorAll(`[data-mobile="${k}"] b`).forEach(el => { el.textContent = v.toFixed(2); });
    });
  }

  function updateScene(dt, time){
    const rate = reduceMotion.matches ? 1 : .055;
    const t = target();
    ["sed", "tc", "ed", "cb", "speed", "spread", "lever", "memory", "authority", "collapse"].forEach(k => {
      state[k] = lerp(state[k], t[k], rate);
    });

    if (!reduceMotion.matches) {
      state.theta += dt * state.speed * (0.55 + state.spread * .75);
      state.micro += dt * (0.2 + state.speed * .35);
    }

    const arrest = smooth(.72, 1, state.lever);
    const live = 1 - arrest * .92;
    const pulse = Math.sin(time * 1.2) * .5 + .5;

    root.rotation.z = Math.sin(time * .08) * .025 * (1 - state.memory);
    core.rotation.z = state.theta * live;
    coreOuter.material.opacity = .28 + state.cb * .26;
    coreInner.material.opacity = .22 + (1 - state.spread) * .24;
    coreHub.material.emissiveIntensity = .06 + state.cb * .14 + state.memory * .22;
    teeth.rotation.z = -state.theta * .62 * live;
    spokes.rotation.z = state.theta * .34 * live;

    outerRing.material.opacity = .24 + state.memory * .18;
    evidenceRing.material.opacity = .16 + state.memory * .42;
    breakerRing.children.forEach((arc, idx) => {
      arc.material.opacity = .14 + state.cb * .34 + (idx === 0 ? pulse * .025 : 0);
    });

    regulators.forEach(r => {
      const v = clamp01(state[r.prop]);
      r.group.rotation.z = (r.index % 2 ? -1 : 1) * state.theta * (.12 + v * .30) * live;
      r.ringA.material.opacity = .18 + v * .30;
      r.ringB.material.opacity = .18 + v * .36;
      r.needle.rotation.z = -Math.PI * .72 + v * Math.PI * 1.42;
      r.jewel.material.emissiveIntensity = .02 + v * .18;
      r.spriteMaterial.opacity = .50 + v * .34;
      const collapsePull = state.collapse * .035;
      r.group.position.z = .03 + Math.sin(time * .5 + r.index) * .012 * (1 - state.memory) + collapsePull;
    });

    const leverStart = -Math.PI * .42;
    const leverEnd = -Math.PI * .92;
    leverGroup.rotation.z = lerp(leverStart, leverEnd, state.lever);
    leverArm.material.opacity = .34 + state.cb * .44;
    leverArm.material.emissiveIntensity = .02 + state.cb * .12;
    leverCap.material.emissiveIntensity = .04 + state.cb * .16;

    stops.children.forEach(stop => {
      stop.material.opacity = .30 + state.cb * .54;
      stop.material.emissiveIntensity = .03 + state.cb * .18;
      stop.scale.setScalar(1 + state.cb * .42 + pulse * state.cb * .05);
    });

    memoryGroup.rotation.z = -state.theta * .08;
    memoryTrace.material.opacity = state.memory * (.18 + pulse * .08);
    memoryGroup.scale.setScalar(.82 + state.memory * .18);

    beamMaterial.opacity = state.authority * (.18 + pulse * .14);
    inscriptionMaterial.opacity = smooth(.42, .95, state.memory) * .78;
    inscription.scale.x = 1.75 + state.memory * .52;

    particleMaterial.opacity = .12 + state.collapse * .10 - state.memory * .045;
    particleMaterial.size = .012 + state.collapse * .016;
    particles.rotation.z = state.theta * .055 * live;
    particles.rotation.y = Math.sin(time * .16) * .06 * (1 - state.memory);
    particles.scale.setScalar(1 - state.collapse * .06 + state.memory * .02);

    key.intensity = 1.02 + state.cb * .46 + state.memory * .26;
    renderer.toneMappingExposure = 1.08 + state.cb * .12 + state.memory * .10;
  }

  function resize(){
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor(rect.width));
    const height = Math.max(1, Math.floor(rect.height));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    renderer.setPixelRatio(dpr);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    const narrow = window.innerWidth <= 900;
    camera.fov = narrow ? 42 : 38;
    camera.position.z = narrow ? 8.9 : 8.2;
    root.scale.setScalar(narrow ? .92 : 1);
    camera.updateProjectionMatrix();
  }

  const clock = new THREE.Clock();
  function animate(){
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, clock.getDelta());
    const time = clock.elapsedTime;
    updateScene(dt, time);
    updateUI();
    controls.autoRotateSpeed = reduceMotion.matches ? 0 : (.06 + state.speed * .018) * (1 - state.memory * .8);
    controls.update();
    renderer.render(scene, camera);
  }

  resize();
  window.addEventListener("resize", resize, { passive: true });
  if (window.visualViewport) window.visualViewport.addEventListener("resize", resize, { passive: true });

  advance?.addEventListener("click", () => setPhase((phase + 1) % phases.length));
  intervene?.addEventListener("click", () => setPhase(4));
  reset?.addEventListener("click", () => setPhase(0));
  document.addEventListener("keydown", e => {
    const tag = document.activeElement?.tagName?.toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "button" || tag === "a") return;
    if (e.code === "Space") { e.preventDefault(); setPhase((phase + 1) % phases.length); }
    if (e.code === "Enter") { e.preventDefault(); setPhase(4); }
    if (e.key.toLowerCase() === "r") setPhase(0);
  });

  animate();
})();
