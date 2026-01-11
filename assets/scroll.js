(function(){
  const root = document.documentElement;
  let ticking = false;

  function onScroll(){
    if(ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const h = Math.max(1, document.body.scrollHeight - innerHeight);
      const v = Math.min(1, Math.max(0, scrollY / (h * 0.65)));
      root.style.setProperty('--scroll', v.toFixed(4));
      ticking = false;
    });
  }

  addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();
