# Recovery and live-browser audit

The archive has a deterministic static build and immutable v6.2 paper originals. The custom-domain release verifier tests exact delivered bytes; the local browser suite tests bounded layouts and interaction. Neither verifies real browser execution of the CDN-delivered site. The public-browser audit therefore observes six core pages in three engines, with desktop/mobile and JavaScript disabled cases (54 observations). It records browser errors, policy violations, failed first-party responses, external host requests, cookie names and browser storage keys, without capturing cookie values or following third-party links. Provider-set cookies are observations requiring interpretation, not automatically first-party tracking.

Recovery procedure (not a performed outage exercise):
1. Record the known-good main commit, its tree, and the exact immutable PDF hashes in the research model. Maintain a separate owner-controlled repository backup outside the hosting provider; do not rely on Actions artifacts with limited retention.
2. Restore a verified checkout, install pinned build verification requirements, run build_site.py and generate_og.py, require a clean generated diff, then run verify_v62.py and local verification tests.
3. Deploy the generated static files to an authorized HTTPS host with the same canonical routes and intact fingerprinted assets. DNS, certificate and registrar changes require owner authorization and access; do not make them as a routine release test.
4. Run byte, HTTP policy and real browser verification against the restored public domain. Inspect DOI/SSRN/ORCID/Scholar identity separately. Do not send IndexNow updates solely because a host was restored without content changes.

A successful clean build is evidence of build repeatability, not proof of an independent backup, provider failover, or domain recovery. Physical-device, assistive-technology and external record availability require separate observations.

The live-browser matrix isolates each browser and input mode in an independent bounded job, retains partial per-page results, and reports timeout as an incomplete observation. It does not await a JavaScript font promise in the disabled-JavaScript case. The original layout and navigation checks remain in place.
