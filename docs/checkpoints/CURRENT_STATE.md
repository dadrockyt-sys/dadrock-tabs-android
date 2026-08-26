# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; musical accuracy first, PDF second.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved source SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Source-only candidate is irreversibly frozen. The professional reference/scorer may be opened only for the one final immutable holdout; **no tuning, candidate modification, threshold adjustment, candidate selection, or replacement may follow from its results.**
- No Modal/L4 without fresh explicit user authorization. **None is currently authorized.**
- Timing frozen; tempo exactly `129.19921875`.
- Completion gate remains professional score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- Existing `freezeReady=false` values are deliberate final-gate safety sentinels. Do not weaken them before all final gates pass.

## Frozen V5 candidate — VALIDATED / IMMUTABLE
- Authorized run `32805316807`, trigger SHA `74b0f815ff3f66f325220975c410621503de440f`.
- Baseline: eligible attacks `984`; retained `725`; selected pitches `970`; rendered `967`; voicing drops `3`; measures `1-113`; candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Attack V3 retained `891`; V4 corrected primaries `34`.
- Combined V5 validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures.
- V5 render events: `967` baseline + `242` rescued.
- Metadata: `933` exact baseline events preserved; `276` conservative neutral events = `34` corrected + `242` rescued.
- Neutral policy: `preserve-exact-baseline-metadata-else-one-step-no-technique-no-relational-semantics`; technique events `21`; no invented technique identities.
- Source-only validation workflow run `32872086764` = **SUCCESS**; persisted validation report all green, reference unopened, no Modal, Production untouched.
- Pre-freeze commit pinned by manifest: `f415bf180fc402a3aa8292304a90b4916d32a5d3`.
- **Candidate bytes/content/timing/metadata/renderer-driven selection are immutable.**

## Current V5 PDF / scorer identity
- Current render: 6 Letter pages, `1209` events / `891` onsets / `113` measures / `21` technique events.
- Raw V5 render-stream SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- PDF SHA256: `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; 1,748,095 bytes.
- Inspection hashes: first `33693e32ee4a578e48f7e96360d0c06191bf0fff16f68d76d97e1e384f1aa5f3`; middle `1e265e8486e75505262de9ea33dea444f60731e025db20dea063dd1f75448775`; last `487df510c3931403017576dac2fe3e587479b9d827a496ea9d792fa5a2764671`.
- Reference-free scorer preflight run `32918988699` = **SUCCESS**; bot result commit `fdac99e0c9d724187ef64720aa8e7d489a66b1d9`.
- Persisted report `debug/v143-contextual-prune/v5-professional-pdf/scorer-preflight-report.json`: `passed=true`, `failedChecks=[]`, candidate/reference/Modal/Production untouched.
- **Canonical V5 scorer event SHA256 = `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.**
- Renderer-normalized PDF event SHA256 equals the same hash; PDF-event fidelity `1.0`; canonical event count `1209`; canonical measure count `113`.
- Therefore V5 is losslessly bound to the established generic scorer contract before any official reference payload access.

## Professional reference provenance — SOURCE PINNED
- Immutable professional image: commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`, path `public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, size `979815` bytes.
- Image SHA256 from existing recovery report: `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source identity: Songsterr song `243`, revision `7868948`, rhythm track index `3`, image id `v0-3-2-TvYYK-mMQgzBsDxG`, exact track name `Craig Ross | 1953 Gibson Les Paul Goldtop | Rhythm Guitar`, tuning `[64,59,55,50,45,40]`.
- Exact structured-source SHA256 expected: `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Exact built reference SHA256 expected: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Expected completeness: 113 measures, 603 playable onsets, 946 playable notes, 104 populated measures.
- User screenshot showed the committed image and commit prefix `e0f91e7`; use only as provenance, never as tuning/scoring input.

## Final one-shot workflow — PREPARED / AUDITED / NOT YET RUN
- Workflow: `.github/workflows/v143-v5-final-professional-holdout.yml`.
- Prepared in commit `066743f7b0348a042d07cc837ca1679808c30b5f` and statically audited before any trigger.
- Current trigger is `workflow_dispatch` only; creating/auditing it did not run it or open reference data.
- It has fixed concurrency, a branch-persisted result sentinel guard, full V5 pre-reference revalidation, exact source/revision/hash pins, exact reference completeness/hash checks, one scorer invocation at `--minimum 0.99`, transient reference cleanup, and a permanent result sentinel even on post-open failure.
- Completion can be true only if near-100 scorer gate passes, `criticalMismatchCount == 0`, `pdfEventFidelity == 1.0`, and scorer `rhythmComplete == true`.
- Current state remains `professionalHoldoutOpened=false`; final scorer untriggered.

## Failed API dispatcher — SAFE / HOLDOUT NOT CONSUMED
- Pre-dispatch checkpoint commit: `58b168aab9ff10a5eabcd3b0a04dfd6c05bdd2d0`.
- Minimal API launcher `.github/workflows/v143-dispatch-v5-final-professional-holdout-once.yml` created in commit `325e4a4d5cc5a98575d1fdbe92f399dcd2a183c5`.
- Launcher run `32919421673` completed **FAILURE** only in its dispatch step.
- Its audited-state verification step passed; it had no professional reference access.
- GitHub returned HTTP `404 Not Found` from the workflow-dispatch API because the target workflow exists only on this feature branch rather than the default branch.
- **No final workflow run was created. No professional source/reference was fetched. Holdout remains unopened.**
- Do not rerun this API launcher; it cannot solve branch-only workflow dispatch.

## Current integrity
- Protected runtime untouched.
- `main`/Production untouched.
- Frozen V5 content/timing/metadata/thresholds/selection unchanged.
- No Modal/L4 used in this continuation.
- Final `freezeReady=false` sentinels unchanged.
- Rhythm remains incomplete.

## Next exact actions
1. Modify only the **trigger stanza** of `.github/workflows/v143-v5-final-professional-holdout.yml` so it also listens for a push on `v143-contextual-prune-lobo` touching exactly one dedicated trigger file, e.g. `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-trigger.txt`. Keep all audited scoring/source logic unchanged.
2. Updating the workflow must not itself match that path, so it must not run. Audit the changed trigger stanza and save this checkpoint again before creating the trigger file.
3. Create the dedicated trigger file exactly once. That push should start the final workflow on the feature branch without API dispatch.
4. Monitor the final run; read only run status and persisted final diagnostic, never transient reference payloads.
5. Immediately checkpoint the result. Regardless of pass/fail, **do not tune, modify, reselect, or replace V5 afterward.**
6. Keep `freezeReady=false` unless score >= `0.99`, critical mismatches `0`, and PDF fidelity `1.0` are all independently proven. Do not claim Rhythm complete before then.
