(() => {
  "use strict";

  if (!document.body?.classList.contains("demo-page--part1")) return;

  const isTouch = matchMedia("(pointer: coarse)").matches;
  if (!isTouch) return;

  const stage = document.getElementById("stage");
  if (!stage) return;

  const isControl = (target) => !!target.closest?.("a,button,input,textarea,select,label");
  const clearSelection = () => {
    try { window.getSelection?.()?.removeAllRanges?.(); } catch {}
  };

  document.addEventListener("selectionchange", clearSelection, { passive: true });

  document.addEventListener("selectstart", (event) => {
    if (!isControl(event.target)) event.preventDefault();
    clearSelection();
  }, { passive: false });

  document.addEventListener("contextmenu", (event) => {
    if (!isControl(event.target)) event.preventDefault();
    clearSelection();
  }, { passive: false });

  stage.addEventListener("touchstart", (event) => {
    if (!isControl(event.target)) event.preventDefault();
    clearSelection();
  }, { passive: false });

  stage.addEventListener("touchmove", (event) => {
    if (!isControl(event.target)) event.preventDefault();
    clearSelection();
  }, { passive: false });

  stage.addEventListener("touchend", clearSelection, { passive: true });
  stage.addEventListener("touchcancel", clearSelection, { passive: true });
})();
