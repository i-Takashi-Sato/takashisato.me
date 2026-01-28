/* =========================================================
   PART I — VIZ_ABSOLUTE_PROTOCOL_100 (Gemini layout)
   Scope: papers/part1.html only (body.part1)
   ========================================================= */

body.part1 .visualizer-wrapper{
  width:100%;
  position:relative;
  margin:clamp(56px,7vh,96px) 0;
  padding:0;
  z-index:1;
}

body.part1 .article-container .visualizer-wrapper{
  max-width:min(1100px, 100%);
  margin-left:auto;
  margin-right:auto;
}

/* Component root */
body.part1 .visualizer-wrapper .altrion-container{
  --alt-bg-base:#050507;
  --alt-bg-panel:#08080c;
  --alt-bg-canvas:#000000;

  --alt-border-s:rgba(255,255,255,0.10);
  --alt-border-d:rgba(255,255,255,0.07);

  --alt-ink:rgba(240,240,242,0.96);
  --alt-dim:rgba(255,255,255,0.55);
  --alt-dimmer:rgba(255,255,255,0.34);

  --alt-r-sm:16px;
  --alt-r-md:24px;
  --alt-r-lg:32px;

  --alt-pad-x:40px;
  --alt-gate-inset:12%;
  --alt-gutter:20px;

  width:100%;
  display:flex;
  flex-direction:column;

  background:var(--alt-bg-base);
  border:1px solid var(--alt-border-d);
  border-radius:var(--alt-r-lg);
  overflow:hidden;

  box-shadow:
    0 50px 170px -120px rgba(0,0,0,0.95),
    0 18px 60px -34px rgba(0,0,0,0.85);
}

/* Top viewport */
body.part1 .visualizer-wrapper .altrion-viewport{
  height:clamp(320px,44vh,480px);
  position:relative;
  overflow:hidden;
  background:var(--alt-bg-canvas);
}

/* Canvas */
body.part1 .visualizer-wrapper #scene{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  display:block;
  mix-blend-mode:screen;
}

/* Gate overlay */
body.part1 .visualizer-wrapper .altrion-gate-overlay{
  position:absolute;
  inset:0;
  display:flex;
  justify-content:space-between;
  padding:0 var(--alt-gate-inset);
  pointer-events:none;
}

body.part1 .visualizer-wrapper .altrion-gate{
  height:100%;
  width:1px;
  background:linear-gradient(
    to bottom,
    transparent,
    var(--alt-border-s) 40%,
    var(--alt-border-s) 60%,
    transparent
  );
  display:flex;
  flex-direction:column;
  justify-content:space-between;
  align-items:center;
}

body.part1 .visualizer-wrapper .altrion-gate-id{
  font-family: var(--font-mono, "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace);
  font-size:10px;
  letter-spacing:0.22em;
  color:rgba(255,255,255,0.34);
  transform:translateY(18px);
}

body.part1 .visualizer-wrapper .altrion-gate-lbl{
  font-family: var(--font-serif, "Cormorant Garamond", serif);
  font-style:italic;
  font-size:11px;
  letter-spacing:0.22em;
  color:rgba(255,255,255,0.22);
  writing-mode:vertical-rl;
  transform:rotate(180deg);
  padding-bottom:36px;
}

/* Console (bottom) */
body.part1 .visualizer-wrapper .altrion-console{
  display:grid;
  grid-template-columns: 1.2fr 1.5fr 1fr;
  gap:var(--alt-pad-x);
  padding:var(--alt-r-lg) var(--alt-pad-x);
  background:var(--alt-bg-panel);
  border-top:1px solid var(--alt-border-d);
}

/* Typography */
body.part1 .visualizer-wrapper .alt-h1{
  font-family: var(--font-serif, "Cormorant Garamond", serif);
  font-weight:300;
  font-size:32px;
  line-height:1.0;
  letter-spacing:-0.01em;
  margin:0;
  color:#fff;
}

body.part1 .visualizer-wrapper .alt-sub{
  font-family: var(--font-mono, "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace);
  font-size:10px;
  letter-spacing:0.22em;
  text-transform:uppercase;
  color:rgba(255,255,255,0.40);
  margin-top:12px;
}

body.part1 .visualizer-wrapper .alt-val{
  font-family: var(--font-mono, "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace);
  font-size:42px;
  font-weight:200;
  letter-spacing:-0.02em;
  margin-top:4px;
  color:#fff;
}

body.part1 .visualizer-wrapper .alt-st-msg{
  font-family: var(--font-mono, "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace);
  font-size:12px;
  font-weight:600;
  letter-spacing:0.18em;
  margin-top:10px;
  text-transform:uppercase;
  color:rgba(255,255,255,0.78);
}

/* Buttons */
body.part1 .visualizer-wrapper .altrion-btn-stack{
  display:flex;
  flex-direction:column;
  gap:8px;
  margin-top:var(--alt-r-sm);
}

body.part1 .visualizer-wrapper .altrion-btn{
  background:transparent;
  border:1px solid var(--alt-border-s);
  color:rgba(255,255,255,0.42);
  height:48px;
  padding:0 20px;
  font-family: var(--font-mono, "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace);
  font-size:10px;
  letter-spacing:0.18em;
  text-transform:uppercase;
  text-align:left;
  cursor:pointer;
  transition: border-color 0.25s ease, color 0.25s ease, background 0.25s ease;
}

body.part1 .visualizer-wrapper .altrion-btn:hover{
  border-color:#fff;
  color:#fff;
}

body.part1 .visualizer-wrapper .altrion-btn.is-active{
  background:#fff;
  color:#000;
  border-color:#fff;
  font-weight:700;
}

/* Mobile editorial */
@media (max-width: 844px){
  body.part1 .visualizer-wrapper{
    margin:48px 0;
  }

  body.part1 .article-container .visualizer-wrapper{
    max-width:100%;
  }

  body.part1 .visualizer-wrapper .altrion-viewport{
    height:clamp(280px,42vh,400px);
  }

  body.part1 .visualizer-wrapper .altrion-console{
    display:flex;
    flex-direction:column;
    padding:var(--alt-r-md) var(--alt-gutter);
    gap:var(--alt-r-md);
  }

  body.part1 .visualizer-wrapper .alt-h1{
    font-size:28px;
    line-height:1.05;
  }

  body.part1 .visualizer-wrapper .altrion-btn-stack{
    gap:10px;
  }
}
