# Final release candidate: merge blockers

This is the single draft PR for the agreed final design. The source and generated CSS/HTML candidate implement the approved system Mincho fallback, name spacing/weight/size/colors, and Japanese guide CSS. The production guide stays on system fonts and line-height 2.05. The reading-resilience diagnostics record potential overflow elements without relaxing assertions.

The temporary read-only font preview verifies the exact Noto Serif CJK JP Medium upstream Git blob, creates a renamed four-codepoint OTF and WOFF2 and emits their bytes for review. It must be removed before merge. The generated font, license/copyright, build integration, CSS @font-face, CI validation and cache migration remain mandatory. Do not merge until every item is verified; the old CSS alias is still generated under the existing contract. The reported WebKit issue must be reproduced or investigated on a repeated run, not marked solved by diagnostics alone. Inspect the header during scroll before changing opacity.

Run all existing gates on the final exact head; verify all deployed resources with no relaxed byte comparison. Independently confirm the Cloudflare cache policy, Lighthouse seven-page parity, accessibility 100, CLS 0, and before/after screenshots at both agreed widths. No research manuscript or historical asset is to be changed.
