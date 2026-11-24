# Live release verification

A passing build is not proof that the custom domain is serving the release. On main pushes and manual dispatch, the release audit fetches canonical HTTPS routes directly from the public domain. It compares bytes to the checked-out commit and checks critical media types, rejects redirects, retries boundedly to accommodate deployment propagation, and fails if any expected resource remains stale or unavailable. The check does not access third-party services or send credentials. It supplements, not replaces, the archive, browser, and Lighthouse gates. Browser caches, search crawlers, social caches, DNS from other regions, and physical-device rendering are separate observations.

Run locally from a release checkout: `python tools/verify_live.py`. Tests use only a loopback HTTP server: `python tools/test_verify_live.py`.

## Managed crawler policy

On 25 November 2026 JST the public robots response was inspected from GitHub Actions. Cloudflare returned a 2,799-byte response containing a managed policy followed by the unchanged 123-byte origin file. The observed prefix is retained byte-for-byte as a test fixture. The verifier accepts either an exact origin response or an exact concatenation of the pinned managed prefix and current origin; any other bytes fail. The current policy declares search=yes, ai-train=no, use=reference and blocks listed training crawlers. This does not prove all search or AI retrieval is available; no Cloudflare setting was changed. Provider policy changes require review, not silent normalization. All other routes retain strict byte equality.

## Runtime cache isolation

Release `621bf0b8` delivered 46 of 48 expected responses; the two unversioned shared bundles returned bytes of the prior size after all 16 attempts. The HTML used query-versioned paths, which were not directly verified by that run. The new build references SHA-256-named files instead; each new content digest receives a distinct URL. The audit now also checks those exact referenced URLs and retains strict checking of both old aliases. No CDN settings or cache policies are changed by this migration; failure of either alias remains visible and fails the audit. Historical fingerprinted bundles are retained for cached HTML.

## Coherent confirmation after propagation

After accumulating successes across multiple attempts, the audit requires a fresh full sweep with every route matching. This is a bounded single sweep, not an atomic or multi-region observation. A regression returns the affected route to the bounded retry set. HTTP errors and byte mismatches include allowlisted cache response metadata when provided; no cookies or credentials are logged. No acceptance thresholds, canonical URLs, or provider settings are changed.
