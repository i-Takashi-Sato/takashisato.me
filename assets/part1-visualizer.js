(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const el = {
    wrap: $("opus-wrap"), canvas: $("scene")
  };
  if (!el.wrap || !el.canvas) return;

  const ctx = el.canvas.getContext("2d", { alpha: true });
  const now = () => performance.now();
  const geom = { w: 0, h: 0, d: 1 };

  function resize() {
    const r = el.wrap.getBoundingClientRect();
    geom.d = Math.min(window.devicePixelRatio || 1, 2);
    geom.w = r.width;
    geom.h = r.height;
    el.canvas.width = geom.w * geom.d;
    el.canvas.height = geom.h * geom.d;
    el.canvas.style.width = `${geom.w}px`;
    el.canvas.style.height = `${geom.h}px`;
    ctx.scale(geom.d, geom.d);
  }

  const sim = { t: 0, last: now() };

  function draw() {
    const W = geom.w;
    const H = geom.h;
    
    ctx.clearRect(0, 0, W, H);

    ctx.save();
    ctx.globalCompositeOperation = "screen";
    
    const lines = 60;
    const yMid = H * 0.5;
    
    for (let i = 0; i < lines; i++) {
      const p = i / lines;
      
      ctx.beginPath();
      
      const alpha = (Math.sin(p * Math.PI) * 0.15 + 0.02) * (1 + Math.sin(sim.t * 0.5) * 0.1);
      ctx.strokeStyle = `rgba(210, 235, 220, ${alpha})`;
      ctx.lineWidth = 1;

      for (let x = 0; x <= W; x += 8) {
        const xNorm = x / W;
        
        const y1 = Math.sin(xNorm * 4 + sim.t * 0.5 + p * 2) * 40;
        const y2 = Math.sin(xNorm * 8 - sim.t * 0.3 + p * 5) * 20;
        const y3 = Math.cos(xNorm * 12 + sim.t * 0.8) * 10;
        
        const envelope = Math.sin(xNorm * Math.PI); 
        
        const y = yMid + (y1 + y2 + y3) * envelope * 1.5 + (p - 0.5) * 160; 
        
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
    
    ctx.beginPath();
    ctx.strokeStyle = `rgba(255, 255, 255, 0.5)`;
    ctx.lineWidth = 1.5;
    for (let x = 0; x <= W; x += 8) {
       const xNorm = x / W;
       const y = yMid + Math.sin(xNorm * 4 + sim.t * 0.5) * 40 * Math.sin(xNorm * Math.PI);
       if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.restore();
  }

  function loop() {
    const t = now();
    const dt = (t - sim.last) / 1000;
    sim.last = t;
    sim.t += dt * 0.8;
    draw();
    requestAnimationFrame(loop);
  }
  
  window.addEventListener("resize", resize, { passive: true });
  resize();
  loop();
})();
