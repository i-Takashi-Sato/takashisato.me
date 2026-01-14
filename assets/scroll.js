/* assets/scroll.js - The Decay Engine */

document.addEventListener("DOMContentLoaded", () => {
  
  // --- Configuration ---
  const CONFIG = {
    // Colors: Blue (#5e6ad2) to Red (#ef4444)
    startColor: { r: 94, g: 106, b: 210 },
    endColor:   { r: 239, g: 68, b: 68 },
    threshold:  0.1 // Scroll reveal threshold
  };

  // --- 1. Mouse Tracking (Linear Glow) ---
  // Keeps the border glow following the mouse
  const cards = document.querySelectorAll('.paper');
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      card.style.setProperty('--lx', `${x}px`);
      card.style.setProperty('--ly', `${y}px`);
    });
  });

  // --- 2. The Decay System (Dynamic Color Shift) ---
  // Calculates scroll percentage and shifts the accent color
  const root = document.documentElement;
  
  function updateDecay() {
    const scrollTop = window.scrollY;
    const docHeight = document.body.scrollHeight - window.innerHeight;
    const scrollPercent = Math.min(Math.max(scrollTop / docHeight, 0), 1); // 0.0 to 1.0

    // Interpolate colors (Linear blending)
    const r = Math.round(CONFIG.startColor.r + (CONFIG.endColor.r - CONFIG.startColor.r) * scrollPercent);
    const g = Math.round(CONFIG.startColor.g + (CONFIG.endColor.g - CONFIG.startColor.g) * scrollPercent);
    const b = Math.round(CONFIG.startColor.b + (CONFIG.endColor.b - CONFIG.startColor.b) * scrollPercent);

    // Apply the new color to the CSS variable
    const dynamicColor = `rgb(${r}, ${g}, ${b})`;
    root.style.setProperty('--accent-current', dynamicColor);
    
    // Optional: Also update the main glow for text
    root.style.setProperty('--glow-primary', dynamicColor);
  }

  // Optimize scroll event (Passive listener)
  window.addEventListener('scroll', () => {
    requestAnimationFrame(updateDecay);
  }, { passive: true });


  // --- 3. Scroll Reveal Animation (Existing) ---
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: CONFIG.threshold, rootMargin: "0px 0px -50px 0px" });

  const targets = document.querySelectorAll('h1, .who, .lead, .paper, footer');
  targets.forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${i * 0.05}s`;
    observer.observe(el);
  });
  
  // Initialize color once on load
  updateDecay();
});
