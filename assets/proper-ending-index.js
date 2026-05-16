(() => {
  const body = document.body;
  if (!body.classList.contains('proper-ending-index')) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const timePlot = document.querySelector('[data-time-dots]');
  if (timePlot) {
    const points = [
      [4,22],[8,54],[12,32],[16,72],[20,45],[24,83],[28,18],[32,62],[36,38],[40,78],
      [47,44],[52,48],[57,46],[62,49],[67,47],[72,50],[77,49],[82,50],[87,49],[92,50]
    ];
    for (const [x,y] of points) {
      const dot = document.createElement('i');
      dot.style.left = `${x}%`;
      dot.style.top = `${y}%`;
      timePlot.appendChild(dot);
    }
  }

  if (reduce) return;

  const ending = document.querySelector('.pei-ending');
  if (ending) {
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) document.documentElement.classList.add('ending-visible');
      }
    }, { threshold: 0.35 });
    observer.observe(ending);
  }
})();
