#!/usr/bin/env python3
"""Apply the v6.11 archive refinement to generator/runtime sources.

Idempotent by design so the branch build workflow can safely re-run.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one migration anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    build = ROOT / "tools" / "build_site.py"
    verify = ROOT / "tools" / "verify_v62.py"
    runtime = ROOT / "assets" / "archive-v62.js"

    replace_once(build, 'ASSET_VERSION = "6.10.4"', 'ASSET_VERSION = "6.11.0"')
    replace_once(verify, 'ASSET_VERSION = "6.10.4"', 'ASSET_VERSION = "6.11.0"')

    old_head = '''          <link rel="stylesheet" href="/assets/archive-v62.css?v={ASSET_VERSION}">
          <script src="/assets/archive-v62.js?v={ASSET_VERSION}"></script>'''
    new_head = '''          <link rel="stylesheet" href="/assets/archive-v62.css?v={ASSET_VERSION}">
          <link rel="stylesheet" href="/assets/archive-v66.css?v=6.7.0" data-v66>
          <link rel="stylesheet" href="/styles/archive-v68.css?v=6.8.0" data-v68>
          <link rel="stylesheet" href="/styles/archive-v611.css?v={ASSET_VERSION}" data-v611>
          <script src="/assets/archive-v62.js?v={ASSET_VERSION}"></script>
          <script src="/scripts/archive-v611.js?v={ASSET_VERSION}" defer></script>'''
    replace_once(build, old_head, new_head)

    gate_anchor = '''          </div>
          <p>All-PASS yields <strong>EXECUTION ELIGIBLE</strong> only. The actual act remains governed by a separate, versioned execution contract. A preliminary BLOCK is not a final denial, authority availability is not a decision event, and UNKNOWN cannot silently become PASS.</p>'''
    gate_markup = '''          </div>
          <div class="gate-probe" data-gate-probe>
            <div class="gate-probe-head">
              <div>
                <p class="eyebrow">Conceptual probe · Stage 1</p>
                <h3>Change the three gate states. Observe only the typed route.</h3>
              </div>
              <p>This probe illustrates the paper’s routing semantics. It is not a decision engine, policy rule, legal test, or execution authorization.</p>
            </div>
            <div class="gate-probe-grid">
              <fieldset class="probe-gate" data-gate="g1">
                <legend>Gate 1 · admissibility</legend>
                <div class="probe-states">
                  <button type="button" data-state="PASS" aria-pressed="false">PASS</button>
                  <button type="button" data-state="REVIEW" aria-pressed="false">REVIEW</button>
                  <button type="button" data-state="BLOCK" aria-pressed="false">BLOCK</button>
                  <button type="button" data-state="UNKNOWN" aria-pressed="true">UNKNOWN</button>
                </div>
              </fieldset>
              <fieldset class="probe-gate" data-gate="g2">
                <legend>Gate 2 · value / conflict</legend>
                <div class="probe-states">
                  <button type="button" data-state="PASS" aria-pressed="false">PASS</button>
                  <button type="button" data-state="REVIEW" aria-pressed="false">REVIEW</button>
                  <button type="button" data-state="BLOCK" aria-pressed="false">BLOCK</button>
                  <button type="button" data-state="UNKNOWN" aria-pressed="true">UNKNOWN</button>
                </div>
              </fieldset>
              <fieldset class="probe-gate" data-gate="g3">
                <legend>Gate 3 · temporal validity</legend>
                <div class="probe-states">
                  <button type="button" data-state="PASS" aria-pressed="false">PASS</button>
                  <button type="button" data-state="REVIEW" aria-pressed="false">REVIEW</button>
                  <button type="button" data-state="BLOCK" aria-pressed="false">BLOCK</button>
                  <button type="button" data-state="UNKNOWN" aria-pressed="true">UNKNOWN</button>
                </div>
              </fieldset>
            </div>
            <div class="probe-route" aria-live="polite">
              <span>Current route</span>
              <strong data-route>EVIDENCE HOLD</strong>
              <small data-route-note>UNKNOWN cannot silently become PASS; unresolved input keeps the case out of execution eligibility.</small>
            </div>
            <button type="button" class="probe-reset" data-probe-reset>RESET TO UNKNOWN</button>
            <p class="caveat">The probe deliberately stops at a typed Stage-1 route. Signed institutional disposition and execution remain separate contracts.</p>
          </div>
          <p>All-PASS yields <strong>EXECUTION ELIGIBLE</strong> only. The actual act remains governed by a separate, versioned execution contract. A preliminary BLOCK is not a final denial, authority availability is not a decision event, and UNKNOWN cannot silently become PASS.</p>'''
    replace_once(build, gate_anchor, gate_markup)

    verify_old = '''        expected_stylesheet = f"/assets/archive-v62.css?v={ASSET_VERSION}"
        expected_enhancement = f"/assets/archive-v62.js?v={ASSET_VERSION}"
        styles = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "stylesheet"]
        if styles != [expected_stylesheet]:
            fail(errors, f"{rel}: stylesheet contract mismatch: {styles}")
        enhancement_scripts = [
            attrs
            for tag, attrs in parser.tags
            if tag == "script" and attrs.get("src", "").startswith("/assets/archive-v62.js")
        ]
        if [attrs.get("src") for attrs in enhancement_scripts] != [expected_enhancement]:
            fail(errors, f"{rel}: enhancement script contract mismatch: {enhancement_scripts}")
        elif any("defer" in attrs or "async" in attrs for attrs in enhancement_scripts):
            fail(errors, f"{rel}: enhancement script must execute in head before body parsing")
        if expected_enhancement not in text.partition("</head>")[0]:
            fail(errors, f"{rel}: enhancement script is not loaded from head")'''
    verify_new = '''        expected_styles = [
            f"/assets/archive-v62.css?v={ASSET_VERSION}",
            "/assets/archive-v66.css?v=6.7.0",
            "/styles/archive-v68.css?v=6.8.0",
            f"/styles/archive-v611.css?v={ASSET_VERSION}",
        ]
        expected_enhancement = f"/assets/archive-v62.js?v={ASSET_VERSION}"
        expected_refinement = f"/scripts/archive-v611.js?v={ASSET_VERSION}"
        styles = [attrs.get("href", "") for tag, attrs in parser.tags if tag == "link" and attrs.get("rel") == "stylesheet"]
        if styles != expected_styles:
            fail(errors, f"{rel}: stylesheet contract mismatch: {styles}")
        enhancement_scripts = [
            attrs
            for tag, attrs in parser.tags
            if tag == "script" and attrs.get("src", "").startswith("/assets/archive-v62.js")
        ]
        if [attrs.get("src") for attrs in enhancement_scripts] != [expected_enhancement]:
            fail(errors, f"{rel}: enhancement script contract mismatch: {enhancement_scripts}")
        elif any("defer" in attrs or "async" in attrs for attrs in enhancement_scripts):
            fail(errors, f"{rel}: enhancement script must execute in head before body parsing")
        refinement_scripts = [
            attrs
            for tag, attrs in parser.tags
            if tag == "script" and attrs.get("src", "").startswith("/scripts/archive-v611.js")
        ]
        if [attrs.get("src") for attrs in refinement_scripts] != [expected_refinement]:
            fail(errors, f"{rel}: refinement script contract mismatch: {refinement_scripts}")
        elif any("defer" not in attrs for attrs in refinement_scripts):
            fail(errors, f"{rel}: refinement script must be deferred")
        head_text = text.partition("</head>")[0]
        if expected_enhancement not in head_text or expected_refinement not in head_text:
            fail(errors, f"{rel}: runtime scripts are not loaded from head")'''
    replace_once(verify, verify_old, verify_new)

    runtime_text = runtime.read_text(encoding="utf-8")
    for obsolete in [
        'if(!d.querySelector("link[data-v610]")){let l=d.createElement("link");l.rel="stylesheet";l.href="/styles/archive-v610.css?v=6.10.4";l.dataset.v610="";d.head.append(l)}\n',
        'if(!d.querySelector("script[data-liquid]")){let s=d.createElement("script");s.src="/scripts/research-fluid.js?v=6.10.4";s.defer=true;s.dataset.liquid="";d.head.append(s)}\n',
    ]:
        runtime_text = runtime_text.replace(obsolete, "")
    runtime.write_text(runtime_text, encoding="utf-8")


if __name__ == "__main__":
    main()
