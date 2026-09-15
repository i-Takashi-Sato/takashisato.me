"""Versioned human-readable research summaries for Parts I–III."""

from __future__ import annotations

from textwrap import dedent

def part1_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>Can oversight be specified as a case contract?</h2>
          <p class="lead">A person may be formally “in the loop” while lacking admissible evidence, time, authority, review capacity, or a usable fallback. Part I makes those conditions explicit and typed.</p>
          <p>The paper shifts the unit of governance from the model alone to the institutional workflow that defines evidence, routes exceptions, allocates authority, and turns a recommendation into action. Its contribution is deliberately narrow: a falsifiable state-and-authority grammar for case routing.</p>
          <div class="fact-grid">
            <article class="fact"><code>DOMAIN CONTRACT</code><h3>Define before deployment</h3><p>Decision scope, evidence, authority, execution, capacity, fallback, record, and remedy are versioned objects—not assumptions left to an interface.</p></article>
            <article class="fact"><code>TYPE DISCIPLINE</code><h3>Keep unlike conditions unlike</h3><p>Missing evidence, unavailable capacity, nominal authority, and fallback readiness do not silently collapse into approval or denial.</p></article>
          </div>
        </section>

        <section id="contract">
          <p class="eyebrow">The contract</p>
          <h2>Three diagnostics. Two stages. No silent action.</h2>
          <div class="model">
            <div class="model-head"><h3>Stage 1 · total routing semantics</h3><span>routing status ≠ execution event</span></div>
            <div class="gate-flow">
              <div class="gate"><span class="meta-label">Gate 1</span><b>Hard constraints &amp; admissibility</b><small>Scope, prohibitions, and minimum evidentiary preconditions.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="gate"><span class="meta-label">Gate 2</span><b>Value, impact &amp; conflict</b><small>Proportionality, material tension, and rights-sensitive tradeoffs.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="gate"><span class="meta-label">Gate 3</span><b>Temporal validity &amp; reliability</b><small>Evidence, policy, system version, and assumptions remain current.</small><div class="state-line"><i>PASS</i><i>REVIEW</i><i>BLOCK</i><i>UNKNOWN</i></div></div>
              <div class="route-box"><span class="meta-label">Route</span><b>Typed status only</b><small>Execution eligible · Evidence hold · Authorized review · Fallback · Unresolved</small></div>
            </div>
            <div class="model-head model-head-spaced"><h3>Stage 2 · signed institutional disposition</h3><span>authorized review only</span></div>
            <div class="disposition-grid" role="list" aria-label="Signed dispositions"><span role="listitem">RELEASE</span><span role="listitem">MODIFIED ACTION</span><span role="listitem">FINAL STOP</span><span role="listitem">AUTHORIZED DEFER</span><span role="listitem">FALLBACK</span></div>
          </div>
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
          <p>All-PASS yields <strong>EXECUTION ELIGIBLE</strong> only. The actual act remains governed by a separate, versioned execution contract. A preliminary BLOCK is not a final denial, authority availability is not a decision event, and UNKNOWN cannot silently become PASS.</p>
          <p>Review authority and review capacity are distinct inputs. Fallback authorization and operational readiness are distinct inputs. If either member of a pair is absent, that route is unavailable.</p>
        </section>

        <section id="verification">
          <p class="eyebrow">Finite-domain verification</p>
          <h2>Complete over the declared truth tables.</h2>
          <div class="verification" role="list" aria-label="Verification results">
            <div role="listitem"><strong>1,024</strong><span>Stage-1 configurations enumerated</span></div>
            <div role="listitem"><strong>1,248</strong><span>applicable Stage-2 configurations enumerated</span></div>
            <div role="listitem"><strong>9 / 9</strong><span>isolated guard mutations produced a counterexample</span></div>
          </div>
          <p class="caveat"><strong>Result:</strong> the authored functions produced zero invariant violations. “Exhaustive” means complete over the declared finite abstraction; it is not proof that the invariants are complete, comparison with external ground truth, or evidence of legal or field effectiveness.</p>
          <div class="fact-grid">
            <article class="fact"><code>CROSS-STAGE TEST</code><h3>Defer is not evidence hold</h3><p>A dedicated mutation catches any collapse of signed DEFER back into the Stage-1 EVIDENCE HOLD label.</p></article>
            <article class="fact"><code>PUBLIC RECORDS</code><h3>Traceability, not validation</h3><p>Fifteen author-coded units from three official investigations trace evidence, reasons, review access, authority, proportionality, feedback, and remedy.</p></article>
          </div>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>What Part I does not establish.</h2>
          <ul>
            <li>That three gates are optimal or the risk decomposition is exhaustive.</li>
            <li>That the routing priority is legally sufficient in any jurisdiction.</li>
            <li>That signatures, identity proofing, cryptography, coercion, or legal authority are solved by a Boolean input.</li>
            <li>That the architecture improves outcomes, can be resourced in practice, or is suitable where lawful fallback and effective authority cannot be established.</li>
          </ul>
        </section>
        """
    ).strip()

def part2_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>Can procedure remain visible after governing capacity has declined?</h2>
          <p class="lead">Part II models a joint institutional state in which observable process remains stable or improves while independent judgment, practical actionability, and a predeclared protected function materially deteriorate.</p>
          <p>The primary construct is <strong>PMGCL</strong>: Procedurally Masked Governing-Capacity Loss. It is descriptive and does not assign an ordinary or malicious cause. <strong>PAC</strong>—Pre-Abuse Collapse—is only a provisional etiological subtype and requires an additional identified causal boundary.</p>
        </section>

        <section id="state-model">
          <p class="eyebrow">Descriptive state model</p>
          <h2>Four objects must remain separate.</h2>
          <div class="model">
            <div class="model-head"><h3>Declared workflow · protected function · population · interval I</h3><span>formative, non-interchangeable elements</span></div>
            <div class="construct-grid">
              <div class="construct"><strong>P</strong><b>Procedural fidelity</b><span>Visible steps, approvals, documentation, and service-level completion.</span></div>
              <div class="construct"><strong>J</strong><b>Judgment contribution</b><span>Case-level evidence or reasoning beyond the AI output and template.</span></div>
              <div class="construct"><strong>G</strong><b>Governing capacity</b><span>Practical ability to alter, resource, escalate, remedy, or stop.</span></div>
              <div class="construct"><strong>N</strong><b>Protected function</b><span>An independently measured, predeclared outcome—not model accuracy by default.</span></div>
            </div>
            <div class="formula">PMGCL(I) = 1 iff F<sub>P</sub>(I) ∧ D<sub>J</sub>(I) ∧ D<sub>G</sub>(I) ∧ I<sub>N</sub>(I)<br>PAC(I) = 1 iff PMGCL(I) = 1 ∧ S<sub>NA</sub>(I) = IDENTIFIED</div>
          </div>
          <p>If judgment and capacity are credibly declining but protected-function impairment is not yet demonstrated, the correct state is <strong>incipient governing-capacity-loss risk</strong>. If all four descriptive conjuncts are established but the causal condition is unidentified, the correct state is <strong>realized PMGCL with etiology unresolved</strong>—not PAC.</p>
        </section>

        <section id="mechanisms">
          <p class="eyebrow">Four candidate mechanisms</p>
          <h2>Pathways to loss, not a closed taxonomy.</h2>
          <div class="fact-grid">
            <article class="fact"><code>01</code><h3>Cognitive externalization</h3><p>Reviewers increasingly treat the model output as both the starting and ending representation of the case, displacing complementary scrutiny.</p></article>
            <article class="fact"><code>02</code><h3>Legibility capture</h3><p>Actors optimize countable completion, agreement, or documentation artifacts while the protected function deteriorates.</p></article>
            <article class="fact"><code>03</code><h3>Responsibility inversion</h3><p>Formal accountability concentrates on the reviewer who bears the cost of deviation but lacks power over the system.</p></article>
            <article class="fact"><code>04</code><h3>Voice attenuation</h3><p>Unremedied or punished concerns reduce the future supply of dissent and deprive the institution of corrective information.</p></article>
          </div>
          <p class="caveat">The set is provisional and theory-directed. Deskilling, vendor lock-in, update opacity, dependency, resource withdrawal, or other mechanisms should be added or preferred when they improve identification.</p>
        </section>

        <section id="propositions">
          <p class="eyebrow">Falsifiability</p>
          <h2>Five derived propositions—and what would count against them.</h2>
          <div class="table-wrap" role="region" aria-label="Scrollable research table" tabindex="0">
            <table class="research-table">
              <caption class="sr-only">Five Part II propositions, target contrasts, and evidence against</caption>
              <thead><tr><th scope="col">Proposition</th><th scope="col">Target contrast</th><th scope="col">Evidence against</th></tr></thead>
              <tbody>
                <tr><th scope="row">P1 · Capacity-strain decoupling</th><td>Change in independent judgment relative to procedural completion after exogenous throughput pressure.</td><td>Judgment remains stable or the decline is explained by case mix, model improvement, or learning.</td></tr>
                <tr><th scope="row">P2 · Target conversion</th><td>Visible artifact and its conditional relation to evidence or the protected outcome after a completion target.</td><td>Both procedure and protected function improve without hidden burden displacement.</td></tr>
                <tr><th scope="row">P3 · Voice-efficacy feedback</th><td>Effect of prior remedy efficacy on later risk-adjusted dissent.</td><td>No temporal association, or the relation is explained by fewer opportunities to dissent.</td></tr>
                <tr><th scope="row">P4 · Coupled-trace discrimination</th><td>Held-out gain from joint rationale, time, and voice traces.</td><td>Single raw metrics perform equally well, or the coupled signal fails under benign efficiency.</td></tr>
                <tr><th scope="row">P5 · Comparative state validity</th><td>Calibrated, decision-relevant gain over continuous components and established baselines.</td><td>The gain vanishes under leakage controls or a simpler model chooses the same intervention.</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>Classification is not a detector or an accusation.</h2>
          <ul>
            <li>The framework does not establish that any real institution satisfies PMGCL or PAC.</li>
            <li>A verbal absence of malice, a directed acyclic graph alone, or retrospective conditioning on “no documented malice” cannot establish the PAC subtype.</li>
            <li>The shared fifteen-unit official-record corpus supports theory-directed traceability, not frequency, necessity, sufficiency, prediction, or independent triangulation.</li>
            <li>Thresholds, measurement validity, site transportability, causal identification, and intervention utility remain empirical questions.</li>
          </ul>
        </section>
        """
    ).strip()

def part3_content() -> str:
    return dedent(
        """
        <section id="overview">
          <p class="eyebrow">Research question</p>
          <h2>How should a failing workflow end?</h2>
          <p class="lead">Detection is not governance. An accountable exit is incomplete if service collapses, evidence disappears, affected people lose remedy, or unresolved decisions have no accountable owner.</p>
          <p>Part III connects investigation, a reversible Circuit Breaker, Resolution Collapse, Proper Ending, and Authority Return. Its stronger contribution is institutional structure: containment and retirement are authorized acts, indicators do not make those decisions, and closure cannot erase unresolved obligations.</p>
          <div class="fact-grid">
            <article class="fact"><code>CIRCUIT BREAKER</code><h3>Reversible containment</h3><p>A bounded response for a workflow that may be corrected, narrowed, replaced, or otherwise recovered under an independent authorization record.</p></article>
            <article class="fact"><code>PROPER ENDING</code><h3>Accountable retirement</h3><p>A dependency-constrained transition that preserves continuity, evidence, notice, remedy, post-exit responsibility, assurance, and closure.</p></article>
          </div>
        </section>

        <section id="proper-ending">
          <p class="eyebrow">Proper Ending</p>
          <h2>Nine evidence-producing functions—not a shutdown button.</h2>
          <div class="model">
            <div class="model-head"><h3>Dependency-constrained institutional transition</h3><span>parallel work where prerequisites permit</span></div>
            <ol class="protocol">
              <li><b>Authorize</b><span>Record the lawful decision maker, scope, effective time, and review path.</span></li>
              <li><b>Contain</b><span>Use tested fallback or a separately authorized emergency safe-stop.</span></li>
              <li><b>Preserve</b><span>Freeze versions, logs, decisions, notices, and investigative evidence lawfully.</span></li>
              <li><b>Notify</b><span>Give accurate, accessible notice appropriate to rights and risks.</span></li>
              <li><b>Remedy</b><span>Identify affected decisions, open review and relief, correct records, and prioritize severe cases.</span></li>
              <li><b>Transfer</b><span>Assign the continuing function to an accepting successor—or residual duties to a named custodian.</span></li>
              <li><b>Decommission</b><span>Revoke integrations and credentials, dispose safely, and verify shadow use has ceased.</span></li>
              <li><b>Assure</b><span>Independently confirm continuity, remedy progress, security, and absence of unauthorized restart.</span></li>
              <li><b>Learn &amp; close</b><span>Publish a proportionate account, assign follow-up owners, and record closure after the assurance cutoff.</span></li>
            </ol>
            <p class="protocol-note">Containment history enables preservation, notice, and remedy in parallel. Preservation and branch-specific responsibility must converge before decommissioning; assurance precedes final closure. No affected case or remedy obligation may be left without an accountable owner.</p>
          </div>
          <p>Urgent protective remedy may begin before individual notice where lawful and necessary, but the exception and later notice must be recorded. Transfer may accept incomplete remedy obligations; it must not falsely certify that every remedy is complete.</p>
        </section>

        <section id="authority-return">
          <p class="eyebrow">Authority Return</p>
          <h2>Ending software does not restore the capacity it displaced.</h2>
          <p class="lead">Authority Return identifies power embedded in data definitions, rankings, defaults, access controls, and queue architecture, then reconstitutes or reassigns the practical capacity to decide, explain, correct, and resource the function.</p>
          <div class="fact-grid">
            <article class="fact"><code>CONTINUING FUNCTION</code><h3>Accepting successor</h3><p>The successor must be able to exercise judgment, operate without a defeating undisclosed dependency, and accept records, resources, queues, cases, and remedy obligations.</p></article>
            <article class="fact"><code>ABOLISHED FUNCTION</code><h3>Residual custodian</h3><p>A named custodian or remedy authority accepts records, unresolved cases, appeals, compensation pathways, incomplete remedies, and residual liabilities.</p></article>
            <article class="fact"><code>CAPACITY</code><h3>People, budget, tools</h3><p>Formal title is insufficient. Competence, protected time, staffing, budget, interpretive knowledge, and operational access must move.</p></article>
            <article class="fact"><code>STANDING</code><h3>Affected-party challenge</h3><p>The destination and terms of return remain normative and legal questions subject to appropriate participation, review, and appeal.</p></article>
          </div>
        </section>

        <section id="verification">
          <p class="eyebrow">Finite-state safety verification</p>
          <h2>The guard model is executable—and bounded.</h2>
          <div class="verification" role="list" aria-label="Finite-state verification results">
            <div role="listitem"><strong>8,564</strong><span>reachable states under exhaustive breadth-first exploration</span></div>
            <div role="listitem"><strong>36,096</strong><span>enabled transitions explored</span></div>
            <div role="listitem"><strong>30</strong><span>mutation-adequate guards with a minimal counterexample when weakened</span></div>
          </div>
          <p class="caveat"><strong>Result:</strong> no authored-invariant violation in the unmutated model. This is executable consistency testing of a selected abstraction—not certification, semantic validation, or proof that a real institution records facts honestly or performs remedy effectively.</p>
        </section>

        <section id="measurement">
          <p class="eyebrow">Measurement boundary</p>
          <h2>Indicators route investigation. They do not authorize action.</h2>
          <p>The Governance Drift Indicator layer asks whether rationales add held-out information, review time remains responsive to legitimate complexity, and corrective voice is supplied and acted upon. It is subordinate to the authorization protocol and is not a prerequisite for Proper Ending.</p>
          <p>Aggregate monitoring misses 92 of 100 constructed localized-collapse streams in the frozen benchmark. The added fixed subgroup rule recovers 97 of 100, and the union 98 of 100—but the subgroup definition matches the synthetic generator’s declared failure boundary. Those are internal implementation results, not field sensitivity, specificity, discovery, or a validated real-world threshold.</p>
        </section>

        <section id="boundary">
          <p class="eyebrow">Claim boundary</p>
          <h2>What Part III does not verify.</h2>
          <ul>
            <li>That the synthetic indicators have prospective lead time, open-world validity, or an operationally justified threshold.</li>
            <li>That retirement bases are lawful, notice intelligible, remedy accessible, staffing sufficient, or successor and custodian roles legitimate in substance.</li>
            <li>Repeated incidents, contested facts, parallel authorities, partial-population rollback, real calendar time, and jurisdictional conflict.</li>
            <li>That “independence” is more than a label unless organizational separation, conflicts, evidence access, competence, power, reasons, and review routes are actually established.</li>
          </ul>
        </section>
        """
    ).strip()
