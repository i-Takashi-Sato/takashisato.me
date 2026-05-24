(() => {
  "use strict";

  const body = document.body;
  if (!body?.classList.contains("demo-page--part1")) return;

  const isTouch = matchMedia("(pointer: coarse)").matches || navigator.maxTouchPoints > 0;
  if (!isTouch) return;

  const stage = document.getElementById("stage");
  if (!stage) return;

  const interactiveSelector = "a,button,input,textarea,select,label,[role='button']";
  const isInteractive = (target) => !!target?.closest?.(interactiveSelector);
  const isInsideStage = (target) => target === stage || !!target?.closest?.("#stage");

  const clearSelection = () => {
    try { window.getSelection?.()?.removeAllRanges?.(); } catch {}
  };

  const blockIfVisualizerSurface = (event) => {
    if (!isInsideStage(event.target)) return;
    if (isInteractive(event.target)) return;
    event.preventDefault();
    clearSelection();
  };

  const clearSoon = () => {
    clearSelection();
    requestAnimationFrame(clearSelection);
    window.setTimeout(clearSelection, 0);
  };

  document.addEventListener("selectionchange", clearSoon, { passive: true });

  document.addEventListener("selectstart", blockIfVisualizerSurface, { passive: false, capture: true });
  document.addEventListener("contextmenu", blockIfVisualizerSurface, { passive: false, capture: true });
  document.addEventListener("dragstart", blockIfVisualizerSurface, { passive: false, capture: true });

  stage.addEventListener("touchstart", blockIfVisualizerSurface, { passive: false, capture: true });
  stage.addEventListener("touchmove", blockIfVisualizerSurface, { passive: false, capture: true });
  stage.addEventListener("touchend", clearSoon, { passive: true, capture: true });
  stage.addEventListener("touchcancel", clearSoon, { passive: true, capture: true });

  stage.addEventListener("pointerdown", blockIfVisualizerSurface, { passive: false, capture: true });
  stage.addEventListener("pointermove", blockIfVisualizerSurface, { passive: false, capture: true });
  stage.addEventListener("pointerup", clearSoon, { passive: true, capture: true });
  stage.addEventListener("pointercancel", clearSoon, { passive: true, capture: true });
})();
