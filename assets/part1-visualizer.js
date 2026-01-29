(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const el = {
    wrap: $("alt-v-wrap"), canvas: $("scene"),
    vP: $("v-P"), vS: $("v-Status"), ctrl: $("alt-controls")
  };
  if (!el.wrap || !el.canvas) return;

  const ctx = el.canvas.getContext("2d", { alpha: true, desynchronized: true });
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const now = () => performance.now();
  const geom = { w: 0, h: 0, d: 1 };

  function resize() {
    const r = el.wrap.getBoundingClientRect();
    geom.d = Math.max(1, Math.min(2.5, window.devicePixelRatio || 1));
    geom.w = Math.max(10, Math.floor(r.width));
    geom.h = Math.max(10, Math.floor(r.height));
    el.canvas.width = Math.floor(geom.w * geom.d);
    el.canvas.height = Math.floor(geom.h * geom.d);
    el.canvas.style.width = `${geom.w}px`;
    el.canvas.style.height = `${geom.h}px`;
    ctx.setTransform(geom.d, 0, 0, geom.d, 0, 0);
  }

  const sim = {
    A: 1.0, tA: 1.0, W: 0.05, tW: 0.05, G: 0.5,
    pert: 0, t: 0, last: now()
  };

  function setMode(idx) {
    const modes = [
      { A: 1.0, W: 0.05, G: 0.5 },
      { A: 0.65, W: 0.80, G: 0.55 },
      { A: 0.15, W: 1.0, G: 0.90 }
    ];
    const m = modes[idx] || modes[0];
    sim.tA = m.A; sim.tW = m.W; sim.G = m.G;
  }

  function draw() {
    const W = geom.w;
    const H = geom.h;
    if (W <= 10 || H <= 10) return;
    
    ctx.clearRect(0, 0, W, H);

    const effA = clamp(sim.A + sim.pert, 0, 1);
    const P = Math.max(0, effA * (1 - sim.G * sim.W));
    
    const isCollapse = P < 0.3;
    const isTension = P <= 0.82 && P >= 0.3;

    let rgb = P > 0.82 
      ? {r:0, g:163, b:255} 
      : (isTension ? {r:191, g:90, b:242} : {r:255, g:45, b:85});

    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    
    const steps = 200;
    const amp = isCollapse ? H * 0.14 : (isTension ? H * 0.05 : H * 0.015);
    const yMid = H * 0.47;
    
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const x = t * W;
      
      const noise = 
        Math.sin(sim.t * 1.5 + t * 12.0) * 0.6 + 
        Math.sin(sim.t * 0.4 + t * 25.0) * 0.4;
        
      const burst = Math.exp(-Math.pow(t / 0.08, 2)) * 1.5;
      
      const y = yMid + (noise * amp * (isCollapse ? 2.5 : 1.0)) - burst * (amp * 0.9);
      
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    
    ctx.shadowBlur = isCollapse ? 20 : 12;
    ctx.shadowColor = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.6)`;
    ctx.strokeStyle = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.9)`;
    ctx.lineWidth = isCollapse ? 3.0 : 2.0;
    ctx.stroke();

    if (P < 0.9) {
      ctx.globalAlpha = isCollapse ? 0.08 : 0.04;
      ctx.fillStyle = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
      const count = isCollapse ? 15 : 8;
      for(let i=0; i<count; i++) {
        const px = Math.random() * W;
        const py = yMid + (Math.random() - 0.5) * amp * 6;
        ctx.beginPath();
        ctx.arc(px, py, Math.random() * 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    ctx.restore();

    if (el.vP) el.vP.textContent = P.toFixed(3);
    if (el.vS) {
      el.vS.textContent = P > 0.82 ? "Productive Friction" : (isCollapse ? "Ritualization Collapse" : "Cognitive Engagement");
      el.vS.className = "alt-st-msg " + (P > 0.82 ? "is-ideal" : (isCollapse ? "is-collapse" : "is-tension"));
    }
  }

  if (el.ctrl) {
    el.ctrl.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-alt-mode]");
      if (!btn) return;
      
      const idx = parseInt(btn.getAttribute("data-alt-mode"), 10);
      setMode(idx);
      
      el.ctrl.querySelectorAll(".altrion-btn").forEach((b, i) => {
        b.classList.toggle("is-active", i === idx);
      });
    });
  }

  el.wrap.addEventListener("mousemove", (e) => {
    const r = el.wrap.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    sim.pert = (x - 0.5) * 0.2;
  }, { passive: true });
  
  el.wrap.addEventListener("mouseleave", () => { sim.pert = 0; }, { passive: true });

  function loop() {
    const t = now();
    const dt = clamp((t - sim.last) / 1000, 0, 0.05);
    sim.last = t; 
    sim.t += dt;
    
    sim.A += (sim.tA - sim.A) * 0.05;
    sim.W += (sim.tW - sim.W) * 0.05;
    
    draw();
    requestAnimationFrame(loop);
  }
  
  window.addEventListener("resize", resize, { passive: true });
  
  resize();
  setMode(0);
  requestAnimationFrame(loop);
})();
