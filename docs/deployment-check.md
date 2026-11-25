# Release verification

A successful pull-request check and merge establish the repository state, not the bytes served by the public host. Run from the intended release checkout:

```sh
python tools/test_check_deployment.py
python tools/check_deployment.py
python tools/check_deployment.py --pdfs
```

The checker enumerates canonical sitemap pages, their immutable CSS/JS references, machine-readable indexes, the feed, the manifest and orientation file. The optional PDF pass includes the preserved trilogy manuscripts. Requests use a release-derived query key, no-cache directives and identity encoding; redirects are not accepted. Each fetched body is compared to the local generated file. Exit 0 means every inspected resource matched byte for byte. Exit 1 means at least one observed difference; exit 2 means incomplete verification or invalid local output. A difference alone does not diagnose its cause: edge rewriting, cache or a different deployment may account for it. The tool does not establish search indexing, visual quality, uptime, or the state of uninspected routes.
