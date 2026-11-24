(() => {
'use strict';
const doc = document;
const root = doc.documentElement;
const desktopPaper = matchMedia('(min-width:44.01rem)');
const reducedMotion = matchMedia('(prefers-reduced-motion:reduce)');
const nativeScrollTimeline = Boolean(
window.CSS?.supports?.('animation-timeline: scroll()'),
);
const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
root.classList.add('js');
const initializationFallback = setTimeout(() => root.classList.remove('js'), 3000);
function initReadingState() {
const sections = [...doc.querySelectorAll('.content > section[id]')];
const links = [...doc.querySelectorAll('.toc a[href^="#"]')];
if (!sections.length || !links.length || !window.IntersectionObserver) return;
const linksById = new Map(links.map((link) => [link.hash.slice(1), link]));
function setCurrent(section) {
sections.forEach((item) => item.classList.toggle('is-current', item === section));
links.forEach((link) => link.removeAttribute('aria-current'));
linksById.get(section.id)?.setAttribute('aria-current', 'location');
}
const observer = new IntersectionObserver((entries) => {
const visible = entries
.filter((entry) => entry.isIntersecting)
.sort((a, b) => (
Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top)
));
if (visible[0]) setCurrent(visible[0].target);
}, {
rootMargin: '-18% 0px -66% 0px',
threshold: [0, 0.08, 0.2],
});
sections.forEach((section) => observer.observe(section));
setCurrent(sections[0]);
}
function initScrollState(reduceMotion) {
const homeHero = doc.querySelector('body[data-page="home"] .hero');
const paperHero = doc.querySelector('.paper-hero');
const apparatus = paperHero?.querySelector('.paper-apparatus');
const paperTone = doc.body?.dataset?.tone || '';
const footer = doc.querySelector('.site-footer');
let scheduled = false;
function clearPaperFallback() {
if (!apparatus) return;
apparatus.style.removeProperty('--trace-a');
apparatus.style.removeProperty('--trace-b');
apparatus.style.removeProperty('--trace-c');
apparatus.style.removeProperty('--capacity-opacity');
apparatus.style.removeProperty('--closure-scale');
apparatus.style.removeProperty('--closure-opacity');
apparatus.style.removeProperty('transform');
}
function updatePaperMechanism() {
if (
!paperHero
|| !apparatus
|| reduceMotion
|| !desktopPaper.matches
|| nativeScrollTimeline
) {
clearPaperFallback();
return;
}
const travel = Math.max(paperHero.offsetHeight * 0.82, innerHeight * 0.72);
const progress = clamp(scrollY / travel);
if (paperTone === 'part-2') {
apparatus.style.setProperty('--trace-a', `${(progress * 10).toFixed(2)}px`);
apparatus.style.setProperty('--trace-b', `${(progress * -6).toFixed(2)}px`);
apparatus.style.setProperty('--trace-c', `${(progress * 4).toFixed(2)}px`);
apparatus.style.setProperty('--capacity-opacity', (1 - progress * 0.14).toFixed(4));
} else if (paperTone === 'part-3') {
apparatus.style.setProperty('--closure-scale', (1 - progress * 0.12).toFixed(4));
apparatus.style.setProperty('--closure-opacity', (0.74 - progress * 0.20).toFixed(4));
} else {
clearPaperFallback();
}
}
function update() {
const maximum = root.scrollHeight - innerHeight;
root.style.setProperty('--scroll', (maximum ? clamp(scrollY / maximum) : 0).toFixed(4));
if (homeHero && !reduceMotion) {
const progress = clamp(scrollY / Math.max(homeHero.offsetHeight * 1.15, innerHeight));
root.style.setProperty('--home-scroll', progress.toFixed(4));
}
updatePaperMechanism();
if (footer) {
const footerRect = footer.getBoundingClientRect();
const terminalTravel = Math.max(1, Math.min(innerHeight, footerRect.height));
const ending = clamp((innerHeight - footerRect.top) / terminalTravel);
root.style.setProperty('--ending', ending.toFixed(4));
root.classList.toggle('is-ending', ending > 0.48);
}
}
addEventListener('scroll', () => {
if (scheduled) return;
scheduled = true;
requestAnimationFrame(() => {
update();
scheduled = false;
});
}, { passive: true });
addEventListener('resize', () => requestAnimationFrame(update), { passive: true });
update();
}
function initReveal(reduceMotion) {
const items = [...doc.querySelectorAll('[data-reveal]')];
if (reduceMotion || !window.IntersectionObserver) {
items.forEach((item) => item.classList.add('is-visible'));
return;
}
const observer = new IntersectionObserver((entries) => {
entries.forEach((entry) => {
if (!entry.isIntersecting) return;
entry.target.classList.add('is-visible');
observer.unobserve(entry.target);
});
}, {
rootMargin: '0px 0px -9% 0px',
threshold: 0.08,
});
items.forEach((item) => observer.observe(item));
}
function hardenExternalLinks() {
doc.querySelectorAll('a[target="_blank"]').forEach((anchor) => {
const rel = new Set((anchor.rel || '').split(/\s+/).filter(Boolean));
rel.add('noopener');
rel.add('noreferrer');
anchor.rel = [...rel].join(' ');
});
}
function initCitationCopy() {
const citation = doc.querySelector('#citation .citation');
const actions = doc.querySelector('#citation .paper-actions');
if (!citation || !actions || !navigator.clipboard?.writeText) return;
const button = doc.createElement('button');
button.type = 'button';
button.className = 'button';
button.textContent = 'Copy citation';
button.dataset.citationCopy = '';
const status = doc.createElement('span');
status.setAttribute('role', 'status');
status.className = 'sr-only';
button.addEventListener('click', async () => {
try {
await navigator.clipboard.writeText(citation.textContent.trim());
button.textContent = 'Citation copied';
status.textContent = 'Citation copied to clipboard.';
} catch {
const selection = window.getSelection();
if (selection) {
const range = doc.createRange();
range.selectNodeContents(citation);
selection.removeAllRanges();
selection.addRange(range);
status.textContent = 'Citation selected. Copy it manually.';
} else {
status.textContent = 'Copy unavailable. Select the citation manually.';
}
button.textContent = 'Copy citation';
}
});
actions.prepend(button);
actions.append(status);
}
function initArchive() {
const reduceMotion = reducedMotion.matches;
initScrollState(reduceMotion);
initReveal(reduceMotion);
hardenExternalLinks();
initReadingState();
initCitationCopy();
clearTimeout(initializationFallback);
}
if (doc.readyState === 'loading') {
doc.addEventListener('DOMContentLoaded', initArchive, { once: true });
} else {
initArchive();
}
})();
(() => {
'use strict';
const doc = document;
function initGateProbe() {
const root = doc.querySelector('[data-gate-probe]');
if (!root) return;
const gates = [...root.querySelectorAll('[data-gate]')];
const route = root.querySelector('[data-route]');
const note = root.querySelector('[data-route-note]');
const routeBox = root.querySelector('.probe-route');
if (!routeBox || !route || !note) return;
const inputs = doc.createElement('fieldset');
inputs.className = 'probe-flags';
inputs.innerHTML = `
      <legend>Route-local institutional inputs</legend>
      <p>These are separate case-time availability inputs, not substitutes for the three diagnostic gates.</p>
      <div class="probe-flag-grid">
        <button type="button" data-flag="r" aria-pressed="true"><span>Review authority</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="c" aria-pressed="true"><span>Review capacity</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="b" aria-pressed="true"><span>Fallback authorization</span><b>AVAILABLE</b></button>
        <button type="button" data-flag="f" aria-pressed="true"><span>Fallback readiness</span><b>READY</b></button>
      </div>`;
routeBox.before(inputs);
const inputButtons = [...inputs.querySelectorAll('button[data-flag]')];
function gateStates() {
return gates.map((gate) => (
gate.querySelector('button[aria-pressed="true"]')?.dataset.state || 'UNKNOWN'
));
}
function inputAvailable(key) {
return inputButtons.find((button) => button.dataset.flag === key)
?.getAttribute('aria-pressed') === 'true';
}
function renderRoute() {
const states = gateStates();
const hasUnknown = states.includes('UNKNOWN');
const hasNonPass = states.some((state) => state === 'REVIEW' || state === 'BLOCK');
const reviewAuthority = inputAvailable('r');
const reviewCapacity = inputAvailable('c');
const fallbackAuthorized = inputAvailable('b');
const fallbackReady = inputAvailable('f');
let label;
let explanation;
if (states.every((state) => state === 'PASS')) {
label = 'EXECUTION ELIGIBLE';
explanation = 'All three diagnostics PASS. This is eligibility to enter the domain-defined execution control, not the execution event itself.';
} else if (hasUnknown && reviewAuthority && reviewCapacity) {
label = 'EVIDENCE HOLD';
explanation = 'UNKNOWN has priority when authorized, resourced review exists: complete required evidence and rerun rather than imputing PASS.';
} else if (!hasUnknown && hasNonPass && reviewAuthority && reviewCapacity) {
label = 'AUTHORIZED REVIEW';
explanation = 'A REVIEW or preliminary BLOCK routes judgment to an authorized, resourced reviewer. The routing status is not a final institutional act.';
} else if (fallbackAuthorized && fallbackReady) {
label = 'FALLBACK';
explanation = 'The required primary evidence/review route is unavailable; fallback is both authorized and operationally ready.';
} else {
label = 'UNRESOLVED';
explanation = 'No permissible operational route exists under the declared inputs. Missing capacity is not missing evidence, and no state is silently converted into approval or denial.';
}
route.textContent = label;
note.textContent = explanation;
root.dataset.route = label.toLowerCase().replace(/[^a-z]+/g, '-');
inputButtons.forEach((button) => {
const enabled = button.getAttribute('aria-pressed') === 'true';
const output = button.querySelector('b');
if (!output) return;
output.textContent = button.dataset.flag === 'f'
? (enabled ? 'READY' : 'NOT READY')
: (enabled ? 'AVAILABLE' : 'UNAVAILABLE');
});
}
root.addEventListener('click', (event) => {
const stateButton = event.target.closest('button[data-state]');
if (stateButton && root.contains(stateButton)) {
const gate = stateButton.closest('[data-gate]');
gate.querySelectorAll('button[data-state]').forEach((button) => {
button.setAttribute('aria-pressed', String(button === stateButton));
});
renderRoute();
return;
}
const inputButton = event.target.closest('button[data-flag]');
if (inputButton && root.contains(inputButton)) {
inputButton.setAttribute(
'aria-pressed',
String(inputButton.getAttribute('aria-pressed') !== 'true'),
);
renderRoute();
}
});
root.querySelector('[data-probe-reset]')?.addEventListener('click', () => {
gates.forEach((gate) => {
gate.querySelectorAll('button[data-state]').forEach((button) => {
button.setAttribute('aria-pressed', String(button.dataset.state === 'UNKNOWN'));
});
});
inputButtons.forEach((button) => button.setAttribute('aria-pressed', 'true'));
renderRoute();
});
renderRoute();
}
if (doc.readyState === 'loading') {
doc.addEventListener('DOMContentLoaded', initGateProbe, { once: true });
} else {
initGateProbe();
}
})();
(function () {
'use strict';
const win = window;
const doc = document;
function cleanText(value) {
return (value || '').replace(/\s+/g, ' ').trim().slice(0, 120);
}
function pageId() {
return doc.body?.dataset?.page || location.pathname.replace(/^\/|\/$/g, '') || 'home';
}
function linkKind(url) {
const path = url.pathname.toLowerCase();
const host = url.hostname.toLowerCase();
if (path.endsWith('.pdf')) return 'pdf';
if (host.includes('ssrn.com')) return 'ssrn';
if (host.includes('doi.org')) return 'doi';
if (host.includes('orcid.org')) return 'orcid';
if (host.includes('scholar.google')) return 'scholar';
if (path.startsWith('/papers/')) return 'paper';
if (path === '/' || path === '') return 'home';
if (url.protocol === 'mailto:') return 'email';
return url.origin === location.origin ? 'internal' : 'external';
}
function emit(name, detail) {
const payload = {
page_id: pageId(),
page_path: location.pathname,
page_title: doc.title,
...detail,
};
win.dispatchEvent(new CustomEvent('site-analytics:event', {
detail: { name, payload },
}));
if (typeof win.gtag === 'function') win.gtag('event', name, payload);
if (typeof win.plausible === 'function') win.plausible(name, { props: payload });
}
doc.addEventListener('click', function (event) {
const anchor = event.target.closest?.('a[href]');
if (!anchor) return;
const href = anchor.getAttribute('href');
if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
const url = new URL(href, location.href);
emit('link_open', {
link_kind: linkKind(url),
link_url: url.href,
link_text: cleanText(anchor.textContent || anchor.getAttribute('aria-label')),
outbound: url.origin !== location.origin,
});
}, { capture: true });
win.takashisatoTrack = emit;
emit('page_view', {});
})();
