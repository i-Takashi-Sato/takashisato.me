/* Part I — Typed Gate conceptual probe.
 *
 * This is a research instrument for declared routing semantics, not an
 * operational decision engine. Missing capacity never becomes missing evidence.
 */
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
