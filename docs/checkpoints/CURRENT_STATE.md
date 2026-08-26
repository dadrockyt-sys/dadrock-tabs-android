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
- Validation workflow: `.github/workflows/v143-validate-source-only-frozen-candidate.yml`; run `32872086764` = **SUCCESS**.
- Persisted validation report: `debug/v143-contextual-prune/v5-professional-pdf/source-only-freeze-validation-report.json`; all checks true, mismatches empty, `sourceOnlyFrozen=true`, `referenceFree=true`, `professionalReferenceUsed=false`, `professionalHoldoutOpened=false`, `modalInvoked=false`, `productionModified=false`.
- Pre-freeze commit pinned by manifest: `f415bf180fc402a3aa8292304a90b4916d32a5d3`.
- **Candidate bytes/content/timing/metadata/renderer-driven selection are now immutable.**

## Current V5 PDF
- Current render: 6 Letter pages, `1209` events / `891` onsets / `113` measures / `21` technique events.
- V5 render-stream SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- PDF SHA256: `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; 1,748,095 bytes.
- Inspection hashes: first `33693e32ee4a578e48f7e96360d0c06191bf0fff16f68d76d97e1e384f1aa5f3`; middle `1e265e8486e75505262de9ea33dea444f60731e025db20dea063dd1f75448775`; last `487df510c3931403017576dac2fe3e587479b9d827a496ea9d792fa5a2764671`.
- V5 renderer path pinned by manifest: `scripts/v143-render-v5-shadow-pdf.mjs` blob `9292073c81e8c98eb292bd6e94d773e568cc4485`; `lib/createV143RhythmPdf.js` blob `4f0e1372dd5903c05c25f0f0a302dd35e81de36b`; `lib/v143RenderContract.js` blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- `scripts/v143-render-v5-shadow-pdf.mjs` passes exact `stream.events` into `createV143RhythmPdf`; the PDF renderer calls `validateV143RenderEvents(renderEvents)` before drawing.

## Closed source-only research
- Full-mix sustain and bends/legato experiments are closed as promotion sources; they did not justify replacing historical two-view metadata or inferring semantics for neutral V5 events.
- Exact replay archaeology cannot recover the original two separated-view stems from the authorized run; do not claim deterministic later stems are byte-identical to that run.
- No Modal/GPU was used for the CPU experiments in this phase.

## Professional scorer/control path — PRE-REFERENCE GATE GREEN
- Generic post-hoc scorer: `validation/rhythm_holdout/score_rhythm_holdout.py`.
- Canonical event schema: `validation/rhythm_holdout/canonical.py`.
- Freeze builder: `validation/rhythm_holdout/freeze_rhythm_analysis.py`.
- PDF-event fidelity validator: `validation/rhythm_holdout/verify_pdf_event_fidelity.py`.
- Generic scorer anti-leakage order is correct: validate reference-free safety, frozen event hash, and exact PDF-event identity **before** resolving/opening any reference JSON. The scorer is post-hoc only and does not write corrections into analyzer output.
- V5 field compatibility with the canonical scorer is confirmed. V5 provenance-only extras are ignored by canonicalization; required musical fields are preserved.
- Added CPU-only reference-free workflow `.github/workflows/v143-v5-professional-scorer-preflight.yml` in commit `c03276298245021afcd91bf876606627847f580c`.
- Preflight run `32918988699` completed **SUCCESS**. Bot result commit: `fdac99e0c9d724187ef64720aa8e7d489a66b1d9`.
- Persisted report: `debug/v143-contextual-prune/v5-professional-pdf/scorer-preflight-report.json`.
- Report `passed=true`; `failedChecks=[]`; `candidateModified=false`; `referenceFree=true`; `professionalReferenceUsed=false`; `professionalHoldoutOpened=false`; `referencePayloadOpened=false`; `modalInvoked=false`; `productionModified=false`; `freezeReadyChanged=false`.
- **Canonical V5 scorer event SHA256: `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.**
- Renderer-normalized PDF event SHA256 is exactly the same: `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- PDF-event fidelity is exactly `1.0`; canonical event count `1209`; canonical measure count `113`.
- Current raw V5 stream SHA and current PDF SHA were reverified exact during preflight.
- Therefore the frozen V5 is now losslessly bound to the established generic scorer contract **before any official reference payload access**.

## Legacy scorer workflow — DO NOT TRIGGER FOR V5
- Historical `.github/workflows/v143-repaired-timing-precision-professional-score.yml` is hard-coded to obsolete freeze artifact `9511117529`, event hash `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `985` events, and historical freeze head `23a64776333a8fd44dd092890d87e08a4a767e14`.
- It would score the wrong candidate and **must not be triggered** for V5.
- Historical professional-score logs are implementation history only, not the current final holdout.

## Professional reference provenance — SOURCE RECOVERABLE, FINAL HOLDOUT STILL CLOSED
- Historical structured scorer-only artifact `9502117311` (`v143-professional-source-raw-track`) is `expired:true`; recorded digest `sha256:380165b5eb160cc8a35196192032c7d50224402880e453de448eed906c3b7dcb`.
- Expiry is not fatal to source provenance because the immutable professional image is committed in Git history.
- Exact pinned source commit: `e0f91e74c815b9ecdf0a72fae6d1523414b34577`; path `public/Professionalexample.jpg`.
- Git tree metadata: blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, size `979815` bytes.
- Existing recovery report `debug/v143-contextual-prune/rhythm-professional-reference-recovery.json` records reference SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`, JPEG RGB, `2160x3840`, with `referenceModified=false`, `runtimeAccessAllowed=false`, `analyzerTrainingAllowed=false`, `analyzerTuningAllowed=false`, `candidateSelectionAllowed=false`, `postFreezeScoringOnly=true`.
- Recovery report deliberately has `wholeSongCoverageVerified=false` and `finalScoringAuthorized=false`; do not silently promote those flags.
- Historical scorer-source structure pins Songsterr song `243`, rhythm track index `3`, revision `7868948`, image id `v0-3-2-TvYYK-mMQgzBsDxG`, 6 tracks, default/popular track `3`, human/editor-created (`aiGenerated=false`).
- Old final scorer expected exact structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`, and built structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac` with 113 measures, 603 playable onsets, 946 playable notes, 104 populated measures.
- User supplied a GitHub screenshot showing committed `public/Professionalexample.jpg` and commit prefix `e0f91e7`. **Use only as path/commit provenance; do not analyze visible musical content or use it for tuning/scoring.**
- No official scorer-side professional reference payload has been fetched/parsed in the current V5 audit. Final V5 scorer remains untriggered. `professionalHoldoutOpened=false`.

## Current integrity
- Protected runtime untouched.
- `main`/Production untouched.
- Frozen V5 content/timing/metadata/thresholds/selection unchanged.
- No Modal/L4 used in this continuation.
- Reference-free scorer preflight passed without official reference payload access.
- Final `freezeReady=false` sentinels remain unchanged.
- Rhythm remains incomplete until all three completion gates pass independently.

## Next exact actions
1. Prepare a **single-use final V5 professional scorer workflow** with `workflow_dispatch` only, so creating/auditing it cannot automatically open the holdout.
2. Pin it to the exact frozen V5 identities above and require the persisted green scorer-preflight report/canonical hash before any reference access.
3. Pin professional source retrieval to exact song `243`, revision `7868948`, image id `v0-3-2-TvYYK-mMQgzBsDxG`, rhythm track index `3`, exact structured-source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`, and exact professional image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9` where independently verifiable.
4. Audit the final workflow source and save this checkpoint again **before dispatching it**.
5. Then run the immutable final scorer exactly once. Persist the result and **never tune, modify, or replace the candidate afterward**, regardless of pass/fail.
6. Keep `freezeReady=false` unless score >= `0.99`, critical mismatches `0`, and PDF fidelity `1.0` are all independently proven. Do not claim Rhythm complete before then.
