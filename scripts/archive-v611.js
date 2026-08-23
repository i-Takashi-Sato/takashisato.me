(()=>{"use strict";
const d=document;
function initGateProbe(){
  const root=d.querySelector("[data-gate-probe]");if(!root)return;
  const groups=[...root.querySelectorAll("[data-gate]")],route=root.querySelector("[data-route]"),note=root.querySelector("[data-route-note]"),routeBox=root.querySelector(".probe-route");
  if(!routeBox)return;
  const flags=d.createElement("fieldset");
  flags.className="probe-flags";
  flags.innerHTML='<legend>Route-local institutional inputs</legend><p>These are separate case-time availability inputs, not substitutes for the three diagnostic gates.</p><div class="probe-flag-grid"><button type="button" data-flag="r" aria-pressed="true"><span>Review authority</span><b>AVAILABLE</b></button><button type="button" data-flag="c" aria-pressed="true"><span>Review capacity</span><b>AVAILABLE</b></button><button type="button" data-flag="b" aria-pressed="true"><span>Fallback authorization</span><b>AVAILABLE</b></button><button type="button" data-flag="f" aria-pressed="true"><span>Fallback readiness</span><b>READY</b></button></div>';
  routeBox.before(flags);
  const flagButtons=[...flags.querySelectorAll("button[data-flag]")];
  const readStates=()=>groups.map(g=>g.querySelector('button[aria-pressed="true"]')?.dataset.state||"UNKNOWN");
  const flag=k=>flagButtons.find(b=>b.dataset.flag===k)?.getAttribute("aria-pressed")==="true";
  const render=()=>{
    const states=readStates(),unknown=states.includes("UNKNOWN"),nonPass=states.some(s=>s==="REVIEW"||s==="BLOCK"),r=flag("r"),c=flag("c"),b=flag("b"),f=flag("f");
    let label,text;
    if(states.every(s=>s==="PASS")){
      label="EXECUTION ELIGIBLE";
      text="All three diagnostics PASS. This is eligibility to enter the domain-defined execution control, not the execution event itself.";
    }else if(unknown&&r&&c){
      label="EVIDENCE HOLD";
      text="UNKNOWN has priority when authorized, resourced review exists: complete required evidence and rerun rather than imputing PASS.";
    }else if(!unknown&&nonPass&&r&&c){
      label="AUTHORIZED REVIEW";
      text="A REVIEW or preliminary BLOCK routes judgment to an authorized, resourced reviewer. The routing status is not a final institutional act.";
    }else if(b&&f){
      label="FALLBACK";
      text="The required primary evidence/review route is unavailable; fallback is both authorized and operationally ready.";
    }else{
      label="UNRESOLVED";
      text="No permissible operational route exists under the declared inputs. Missing capacity is not missing evidence, and no state is silently converted into approval or denial.";
    }
    route.textContent=label;note.textContent=text;root.dataset.route=label.toLowerCase().replace(/[^a-z]+/g,"-");
    flagButtons.forEach(btn=>{const on=btn.getAttribute("aria-pressed")==="true",out=btn.querySelector("b");if(out)out.textContent=btn.dataset.flag==="f"?(on?"READY":"NOT READY"):(on?"AVAILABLE":"UNAVAILABLE")});
  };
  root.addEventListener("click",e=>{
    const state=e.target.closest("button[data-state]");
    if(state&&root.contains(state)){const group=state.closest("[data-gate]");group.querySelectorAll("button[data-state]").forEach(x=>x.setAttribute("aria-pressed",String(x===state)));render();return}
    const input=e.target.closest("button[data-flag]");if(input&&root.contains(input)){input.setAttribute("aria-pressed",String(input.getAttribute("aria-pressed")!=="true"));render()}
  });
  root.querySelector("[data-probe-reset]")?.addEventListener("click",()=>{groups.forEach(g=>g.querySelectorAll("button[data-state]").forEach(btn=>btn.setAttribute("aria-pressed",String(btn.dataset.state==="UNKNOWN"))));flagButtons.forEach(btn=>btn.setAttribute("aria-pressed","true"));render()});
  render();
}
function init(){initGateProbe()}
d.readyState==="loading"?d.addEventListener("DOMContentLoaded",init,{once:true}):init();})();
