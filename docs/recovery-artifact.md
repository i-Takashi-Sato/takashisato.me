# Verified repository recovery

The manual **Verified repository recovery** workflow exports the selected published commit
and its reachable history into a self-contained Git bundle. Its pull-request check uses the
PR base commit rather than unpublished work. It includes no separate account credentials,
other branch refs or tag refs, DNS state, CDN settings or external scholarly records.

CI verifies the bundle, restores it into a separate checkout, checks Git objects and the
commit identity, runs the deterministic site and image generators, validates the archive
(including preserved PDFs), and requires an unchanged tree. The resulting artifact contains
`archive.bundle`, `SHA256SUMS`, and `RECOVERY.txt`. Download it before its seven-day
retention expires and retain it outside the hosting account. A successful CI artifact alone
is not independent long-term storage.

Offline recovery:

```sh
sha256sum -c SHA256SUMS
git clone --branch recovery-main archive.bundle restored-archive
git -C restored-archive fsck --full
git -C restored-archive rev-parse HEAD
```

Compare the commit against RECOVERY.txt. Before a public recovery, reinstall the pinned
build dependencies, repeat the deterministic build and archive validation, and run the
normal release checks. Do not publish a historical commit over a newer release without
explicit review. Credentials, account recovery, registrar control, domain renewal, and
provider settings remain separate operator responsibilities.
