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
- Attack V3: baseline `725` + exception-band `123` + electric-consensus subfloor `43` = `891` retained attacks.
- V4: `34` lower-primary corrections accepted only where exact electric-model pairwise evidence favored them.
- Combined V5 validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures.
- V5 render events: `967` baseline + `242` rescued.
- Metadata: `933` exact baseline events preserved; `276` conservative neutral events = `34` corrected + `242` rescued.
- Neutral policy: `preserve-exact-baseline-metadata-else-one-step-no-technique-no-relational-semantics`.
- Technique events: `21`; no invented technique identities. Four historical techniques are omitted only where corrected-primary replacement removed the old event.
- Source-only manifest: `debug/v143-contextual-prune/v5-professional-pdf/source-only-frozen-candidate-manifest.json`.
- Source-only validator: `analyzer/validate_v143_v5_source_only_frozen_candidate.py`.
- Source-only validation workflow run `32872086764` = **SUCCESS**; persisted validation report all green, reference unopened, no Modal, Production untouched.
- Pre-freeze commit pinned by manifest: `f415bf180fc402a3aa8292304a90b4916d32a5d3`.
- **Candidate bytes/content/timing/metadata/renderer-driven selection are immutable.**

## Current V5 PDF / scorer identity
- Current render: 6 Letter pages, `1209` events / `891` onsets / `113` measures / `21` technique events.
- Raw V5 render-stream SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- PDF SHA256: `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; 1,748,095 bytes.
- Inspection hashes: first `33693e32ee4a578e48f7e96360d0c06191bf0fff16f68d76d97e1e384f1aa5f3`; middle `1e265e8486e75505262de9ea33dea444f60731e025db20dea063dd1f75448775`; last `487df510c3931403017576dac2fe3e587479b9d827a496ea9d792fa5a2764671`.
- Reference-free scorer preflight workflow `.github/workflows/v143-v5-professional-scorer-preflight.yml` was added in commit `c03276298245021afcd91bf876606627847f580c`.
- Preflight run `32918988699` completed **SUCCESS**; bot result commit `fdac99e0c9d724187ef64720aa8e7d489a66b1d9`.
- Persisted report: `debug/v143-contextual-prune/v5-professional-pdf/scorer-preflight-report.json`.
- Preflight report: `passed=true`, `failedChecks=[]`, `candidateModified=false`, `professionalReferenceUsed=false`, `professionalHoldoutOpened=false`, `referencePayloadOpened=false`, `modalInvoked=false`, `productionModified=false`, `freezeReadyChanged=false`.
- **Canonical V5 scorer event SHA256 = `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.**
- Renderer-normalized PDF event SHA256 is exactly the same `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- PDF-event fidelity is exactly `1.0`; canonical event count `1209`; canonical measure count `113`.
- Therefore V5 is losslessly bound to the established generic scorer contract before any official reference payload access.

## Scorer control path
- Generic scorer: `validation/rhythm_holdout/score_rhythm_holdout.py`.
- Canonical schema: `validation/rhythm_holdout/canonical.py`.
- Freeze builder: `validation/rhythm_holdout/freeze_rhythm_analysis.py`.
- PDF-event fidelity validator: `validation/rhythm_holdout/verify_pdf_event_fidelity.py`.
- Reference completeness validator: `validation/rhythm_holdout/verify_reference_completeness.py`.
- Anti-leakage order is verified: source-only freeze + canonical hash + PDF-event fidelity must pass before any professional reference JSON is opened. Scorer is post-hoc and does not write analyzer corrections.
- Legacy `.github/workflows/v143-repaired-timing-precision-professional-score.yml` is obsolete for V5 (hard-coded 985-event candidate) and **must not be triggered**.

## Professional reference provenance — SOURCE PINNED
- Historical structured artifact `9502117311` expired; do not rely on it.
- Immutable professional image is in Git history at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577`, path `public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, size `979815` bytes.
- Existing recovery report records image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`, JPEG RGB `2160x3840`, post-freeze scoring only, no training/tuning/candidate selection.
- Structured professional source identity: Songsterr song `243`, revision `7868948`, rhythm track index `3`, image id `v0-3-2-TvYYK-mMQgzBsDxG`, exact track name `Craig Ross | 1953 Gibson Les Paul Goldtop | Rhythm Guitar`, tuning `[64,59,55,50,45,40]`.
- Exact structured-source SHA256 expected: `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Exact built reference SHA256 expected: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Expected reference completeness: 113 measures, 603 playable onsets, 946 playable notes, 104 populated measures.
- User screenshot showed committed `public/Professionalexample.jpg` and commit prefix `e0f91e7`; use only as provenance, never as tuning/scoring input.

## Final one-shot workflow — PREPARED / AUDITED / NOT TRIGGERED
- Workflow: `.github/workflows/v143-v5-final-professional-holdout.yml`.
- Prepared in commit `066743f7b0348a042d07cc837ca1679808c30b5f`.
- Trigger is **`workflow_dispatch` only**. Creating/auditing it did not run it and did not open the holdout.
- Concurrency is one fixed group with `cancel-in-progress:false`, so simultaneous attempts serialize instead of replacing an active run.
- First step checks branch for permanent result sentinel `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`; if it exists, the workflow exits before any reference access. This also blocks reruns after a persisted attempt.
- Before reference access it revalidates protected pipeline blob, raw V5 SHA, PDF SHA, source-only freeze, persisted green scorer preflight, exact canonical scorer hash, exact 1209 events/113 measures, and PDF-event fidelity `1.0`.
- First reference access is the immutable committed professional image at exact historical commit; its SHA must equal `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- It then retrieves only the exact structured source identity above from the historical CDN endpoints and requires structured-source SHA `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- It rebuilds the historical exact scorer reference and requires reference SHA `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac` and counts `(603 onsets, 946 notes, 104 populated measures, 113 total measures)`.
- It runs `verify_reference_completeness.py`, then exactly one `score_rhythm_holdout.py --minimum 0.99` invocation.
- Completion is recorded true only if scorer near-100 gate passes, `criticalMismatchCount == 0`, `pdfEventFidelity == 1.0`, and scorer `rhythmComplete == true`.
- Any exception **after** reference opening still writes a failure result sentinel in Python `finally`, removes transient reference/source/image files, then the `if: always()` step commits the sentinel. Thus a post-open network/hash/completeness/scoring failure consumes the one-shot and cannot be retried.
- Any failure **before** reference opening does not consume the holdout because the reference-opening step never runs.
- Static source audit completed after creation. No reference content was fetched or parsed during the audit.
- Current state remains `professionalHoldoutOpened=false` and final scorer untriggered.

## Current integrity
- Protected runtime untouched.
- `main`/Production untouched.
- Frozen V5 content/timing/metadata/thresholds/selection unchanged.
- No Modal/L4 used in this continuation.
- Final `freezeReady=false` sentinels remain unchanged.
- Rhythm remains incomplete until the one-shot professional result is persisted and all completion gates pass.

## Next exact actions
1. Create a minimal one-time dispatcher mechanism because the connected GitHub tool does not expose direct workflow-dispatch creation. The dispatcher must have `actions:write`, check that the final result sentinel is absent, and dispatch exactly `.github/workflows/v143-v5-final-professional-holdout.yml` on ref `v143-contextual-prune-lobo` once.
2. Monitor the final run to completion. Do not inspect transient reference payloads; read only the persisted final diagnostic result.
3. Immediately checkpoint the final result.
4. Regardless of pass/fail, **do not tune, modify, reselect, or replace V5 afterward.**
5. Keep `freezeReady=false` unless score >= `0.99`, critical mismatches `0`, and PDF fidelity `1.0` are all independently proven. Do not claim Rhythm complete before then.
