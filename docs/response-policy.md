# Public response policy review

The public archive is delivered through GitHub Pages and Cloudflare. The application is static; HTML source changes alone cannot set HTTP response headers. Cloudflare Pages-specific _headers files must not be assumed to work on a GitHub Pages origin.

The read-only response policy audit observes five canonical HTTPS routes, recording only an allowlist of browser protection headers. It neither changes provider configuration nor tests exploitability. Header presence is not evidence of sufficient policy semantics, and a missing optional header is not automatically an exploitable vulnerability. Report-only CSP is not an enforced CSP. Results describe a single GitHub Actions location and request context.

Assess actual response values before proposing changes. For policies such as CSP and HSTS, use staged, compatibility-tested changes through authorized hosting controls; do not change DNS, training permissions, certificate settings, or externally managed policies without access and verification. Preserve the site's native navigation, structured research metadata, and accessible progressive enhancement.

References: https://developers.cloudflare.com/rules/transform/response-header-modification/ ; https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
