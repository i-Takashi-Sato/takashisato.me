# Live release verification

A passing build is not proof that the custom domain is serving the release. On main pushes and manual dispatch, the release audit fetches canonical HTTPS routes directly from the public domain. It compares bytes to the checked-out commit and checks critical media types, rejects redirects, retries boundedly to accommodate deployment propagation, and fails if any expected resource remains stale or unavailable. The check does not access third-party services or send credentials. It supplements, not replaces, the archive, browser, and Lighthouse gates. Browser caches, search crawlers, social caches, DNS from other regions, and physical-device rendering are separate observations.

Run locally from a release checkout: `python tools/verify_live.py`. Tests use only a loopback HTTP server: `python tools/test_verify_live.py`.
