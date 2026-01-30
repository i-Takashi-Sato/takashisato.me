(() => {
  "use strict";

  const stage = document.getElementById("stage");
  const dust = document.getElementById("dust");
  const strands = document.getElementById("strands");
  const cursor = document.getElementById("cursor");

  if (!stage || !dust || !strands) return;

  let W=0,H=0,DPR=1;
  const ctxD = dust.getContext("2d");
  const ctxS = strands.getContext("2d");

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;

    for(const c of [dust, strands]){
      c.width = Math.floor(W * DPR);
      c.height = Math.floor(H * DPR);
      c.style.width = W+"px";
      c.style.height = H+"px";
    }
    ctxD.setTransform(DPR,0,0,DPR,0,0);
    ctxS.setTransform(DPR,0,0,DPR,0,0);
  }

  window.addEventListener("resize", resize);
  resize();

  window.addEventListener("mousemove", (e) => {
    if (!cursor) return;
    cursor.style.left = e.clientX + "px";
    cursor.style.top  = e.clientY + "px";
  });

  // smoke test render
  function loop(t){
    ctxD.clearRect(0,0,W,H);
    ctxS.clearRect(0,0,W,H);

    ctxD.fillStyle = "rgba(255,255,255,0.03)";
    ctxD.fillRect((W/2)-1, (H/2)-60, 2, 120);

    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
