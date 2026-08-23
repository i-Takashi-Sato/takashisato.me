(()=>{"use strict";
const d=document,b=d.body;if(!b||matchMedia("(hover:none),(pointer:coarse)").matches)return;
const reduce=matchMedia("(prefers-reduced-motion:reduce)").matches;
const targets=[];
const hero=d.querySelector(".paper-hero");if(hero)targets.push(hero);
if(b.dataset.page==="home"||b.dataset.page==="papers")targets.push(...d.querySelectorAll(".sequence-row"));
if(!targets.length)return;
const clean=s=>(s||"").replace(/\s+/g," ").trim();
function titleOf(t){return clean(t.querySelector("h1,.sequence-title,h2,h3")?.textContent)||"The Proper Ending Index"}
function metaOf(t){return clean(t.querySelector(".paper-meta,.sequence-meta,.record-row,.eyebrow")?.textContent)||"Working paper · v6.2 · preserved research record"}
function paper(title,meta){let p=d.createElement("div");p.className="research-paper";let k=d.createElement("p");k.className="research-paper-kicker";k.textContent="THE PROPER ENDING INDEX / RESEARCH RECORD";let h=d.createElement("div");h.className="research-paper-title";h.textContent=title;let m=d.createElement("div");m.className="research-paper-meta";m.textContent=meta;let lines=d.createElement("div");lines.className="research-paper-lines";for(let i=0;i<22;i++)lines.append(d.createElement("i"));p.append(k,h,m,lines);return p}
function mount(t){let membrane=d.createElement("div");membrane.className="research-membrane";membrane.setAttribute("aria-hidden","true");let base=paper(titleOf(t),metaOf(t)),refract=d.createElement("div"),clone=base.cloneNode(true),caustic=d.createElement("div");refract.className="research-refraction";caustic.className="research-caustic";refract.append(clone);membrane.append(base,refract,caustic);t.prepend(membrane);t.classList.add("has-research-membrane");if(reduce)return;
let px=0,py=0,pt=performance.now(),v=0,raf=0;
const move=e=>{if(e.pointerType==="touch")return;let r=t.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height,now=performance.now(),dx=e.clientX-px,dy=e.clientY-py,dt=Math.max(8,now-pt);v=Math.min(1,Math.hypot(dx,dy)/dt/1.1);px=e.clientX;py=e.clientY;pt=now;if(raf)return;raf=requestAnimationFrame(()=>{raf=0;t.style.setProperty("--lx",(x*100).toFixed(2)+"%");t.style.setProperty("--ly",(y*100).toFixed(2)+"%");t.style.setProperty("--vx",Math.max(-18,Math.min(18,dx*.16)).toFixed(2)+"px");t.style.setProperty("--vy",Math.max(-14,Math.min(14,dy*.14)).toFixed(2)+"px");t.style.setProperty("--fluid-v",v.toFixed(3));t.classList.add("is-fluid-active")})};
const leave=()=>{t.classList.remove("is-fluid-active");t.style.setProperty("--fluid-v","0");t.style.setProperty("--vx","0px");t.style.setProperty("--vy","0px")};
t.addEventListener("pointermove",move,{passive:true});t.addEventListener("pointerleave",leave,{passive:true})}
targets.forEach(mount);
})();