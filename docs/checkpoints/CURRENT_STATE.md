# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; musical accuracy first, PDF second.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved source SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No tuning/selection from it.
- No Modal/L4 without fresh explicit user authorization. **None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.
- Completion gate remains score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**

## Frozen content state
- Authorized run `32805316807`, trigger SHA `74b0f815ff3f66f325220975c410621503de440f`.
- Baseline: eligible attacks `984`; retained `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`; candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Attack V3 validation commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`: baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **891 retained attacks**.
- Primary V4 validation commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`: 34 lower-primary corrections accepted only where exact electric model pairwise favored them.
- Combined V5 validation commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`; SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures. No invented/unplayable pitch, attack relocation, or timing change.
- Exact V5 render stream from artifact `9553423573` has `967` `v5AttackClass=baseline` events + **242 exact `v5AttackClass=rescued` events**. This directly identifies the rescued event set; no rescue-policy reconstruction is needed.
- V5 render currently preserves exact baseline performance metadata on `933` events; `34` primary-corrected baseline events + `242` rescued events remain neutral downstream metadata. PDF is therefore not freeze-ready.

## PDF state
- Renderer upgrade commit `08ee3bcc1cec3428641741a8281206aa4218cb8d`; V5 materializer commit `a6505ba21e30af1b0e985b945de71ae3698bf08f`.
- Successful V5 PDF workflow `32821861294`, artifact `9553423573`.
- PDF: 6 Letter pages, 1,748,093 bytes, SHA256 `bbd67f9054a3a112f4b24e5e22b3b3fc31b125e36ebdb97c36d693ace0ffa99b`; visual first/middle/last pages passed.

## Exact downstream algorithm
- Replay order from authorized wrapper: bends consensus -> legato enrichment -> semantic guard -> assembly -> direct/cascade pitch-energy views -> sustain shadow -> sustain promotion.
- Current replay-critical modules remain byte-identical to trigger:
  - sustain consensus `7bc16d01fd688394f22fd925c78544628fcb4b51`
  - bend evidence `2f5a9e6d8feb90bad26f16de1ca59507f55e9ca3`
  - bend consensus `7434e0e2ea8849942fa53d61a0efcc022638c2a2`
  - legato `69991ecab59438f18321a42ed27fd9a7aa2c4390`
  - semantic guard `d233b1982599c807248529744127da832d1eddbc`
  - sustain promotion `7542d726159795c42a3c54c17dd2f965bff2e327`
- Exact sustain constants: pre-onset `0.12s`, guard `0.03s`, attack `0.10s`, sustain start `0.04s`, threshold fraction `0.18`, max inactive gap `0.10s`, max sustain `3.0s`, same-string guard `0.01s`, 4 subdivisions/beat.

## Historical source-view blocker / closed archaeology
- Exact replay needs `direct-demucs6s-guitar.wav` and `bsroformer-demucs6s-guitar.wav`.
- Authorized one-shot workflow ID `341007940`, actual path `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`.
- Runs: `32801442757` = run #2 failure, artifact `9547279904`; `32805316807` = run #3 success, artifact `9548666053`. Historical run #1 is no longer retained.
- Trigger workflow source proves artifacts uploaded only product/manifest/guard/report JSON; stems were never uploaded or committed.
- Deterministic separator run `32692406659` proved cross-worker PCM determinism but retains only log artifact `9509611954` (14,213 bytes), not stems.
- Deterministic stem identities remain recorded but are not proven byte-identical to authorized-run stems; do not claim equivalence.
- Earlier product `9547279904` has zero exact overlap with all `166` rescued attack positions / `242` rescued V5 events, so it cannot directly supply rescued metadata.

## Source-only evidence now available locally
- Authorized artifact `9548666053` downloaded again. Full product is 15,276,258 bytes and contains:
  - all `967` exact baseline events with downstream metadata,
  - `precisionReplayEvidence` for all `984` eligible attacks and `10,585` candidate pitches,
  - scalar two-view candidate evidence for every V5 rescued pitch.
- Expanded downstream inspector artifact `9559978873` confirms all 967 baseline events have `rhythmSustain`; 669 have `rhythmSustainShadow`; 25 have legato/technique evidence.
- Exact join test: **967/967 baseline events** and **242/242 rescued V5 events** map to authorized `precisionReplayEvidence` candidate records by `(measure, step, midi)`.
- Strict 5-fold grouped and blocked holdout using only scalar candidate evidence + event-neighborhood structure predicts exact baseline `durationSteps` only about **71%** (MAE ~`0.71` steps; within-one-step ~`86%`). This is not trustworthy enough. Do not use the scalar-only reconstruction for production/freeze.

## Exact approved source capture — CPU-only, no Modal
- GitHub connector cannot return the >1 MB binary source directly, so a temporary one-shot Actions workflow was created only to package the already-checked-in file.
- Workflow commit `1b7dff297a07dec2453cebd149cf9053d8a27a14`; run `32866343856`; artifact `9570238003` (`v143-approved-source-audio`, retention 1 day).
- Downloaded source locally and independently verified SHA256 exactly `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Temporary workflow was immediately removed in commit `069798d534eabae61e297cfa28da5b61636af1d1`.
- No Modal/GPU was used. This capture enables CPU-only full-source trajectory experiments.

## Current live experiment
- New preferred path: build the **same harmonic CQT pitch-energy view from the exact approved full mix**, run the unchanged sustain evidence logic against the exact 967 baseline event graph, and measure how faithfully full-mix trajectories reproduce the historical two-separated-view consensus.
- This is materially stronger than scalar snapshots because it restores the full time trajectory while remaining reference-free and CPU-only.
- First local exact full-mix CQT attempt exceeded the single tool-call timeout during harmonic/CQT construction; it made no branch/content change. Continue via an interactive CPU process, not Modal.
- If full-mix holdout fidelity is insufficient, keep it shadow-only and record the blocker; do not invent a threshold to force agreement.

## Continuation checkpoint — resumed 2026-08-25
- Re-downloaded/materialized the trusted authorized product artifact `9548666053` and approved source artifact `9570238003` for the CPU sustain investigation.
- Reverified the approved source SHA256 exactly `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f` before analysis.
- Full-mix harmonic/CQT sustain evidence investigation is resumed locally. No protected runtime code, timing, main/Production, or Modal/L4 has been touched.

## Current integrity
- Protected runtime untouched.
- `main`/Production untouched.
- No professional reference/scorer used.
- No Modal/L4 used in this continuation.
- Only branch changes since the prior checkpoint were the temporary source-export workflow creation/removal and checkpoint commits.

## Next exact actions
1. Complete the CPU full-mix harmonic-CQT sustain pass and compare event-by-event against the 967 exact source-derived baseline sustains.
2. Evaluate exact duration-step accuracy, long-sustain discrimination, and failure structure under blocked holdout / repeated-riff consistency; no professional reference.
3. Only if source-only full-mix evidence validates strongly, generalize it conservatively to the 34 corrected + 242 rescued V5 events as a shadow candidate.
4. Separately validate bends/legato from full-mix evidence; techniques are sparse (25 baseline positives), so require conservative evidence and zero invented semantics.
5. Re-render V5 PDF only after downstream metadata completeness is proven.
6. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
