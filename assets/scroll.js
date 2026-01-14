(function(){
  const root = document.documentElement;
  let ticking = false;

  function clamp01(n){ return Math.min(1, Math.max(0, n)); }

  function setScroll(){
    const h = Math.max(1, document.body.scrollHeight - innerHeight);
    const v = clamp01(scrollY / (h * 0.65));
    root.style.setProperty('--scroll', v.toFixed(4));
  }

  function setPointer(x, y){
    const px = clamp01(x / Math.max(1, innerWidth)) * 100;
    const py = clamp01(y / Math.max(1, innerHeight)) * 100;
    root.style.setProperty('--mx', px.toFixed(2) + '%');
    root.style.setProperty('--my', py.toFixed(2) + '%');
  }

  function onScroll(){
    if(ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      setScroll();
      ticking = false;
    });
  }

  function onPointerMove(e){
    const p = e.touches ? e.touches[0] : e;
    if(!p) return;
    setPointer(p.clientX, p.clientY);
  }

  addEventListener('scroll', onScroll, {passive:true});
  addEventListener('mousemove', onPointerMove, {passive:true});
  addEventListener('touchmove', onPointerMove, {passive:true});

  // init
  setScroll();
})();
