# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; musical accuracy first, PDF second.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved source SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Source-only candidate is now irreversibly frozen. The professional reference/scorer may be opened only for the one final immutable holdout; **no tuning, candidate modification, or candidate selection may follow from its results.**
- No Modal/L4 without fresh explicit user authorization. **None is currently authorized.**
- Timing frozen; tempo exactly `129.19921875`.
- Completion gate remains score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**

## Frozen content state
- Authorized run `32805316807`, trigger SHA `74b0f815ff3f66f325220975c410621503de440f`.
- Baseline: eligible attacks `984`; retained `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`; candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Attack V3 validation commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`: baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **891 retained attacks**.
- Primary V4 validation commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`: 34 lower-primary corrections accepted only where exact electric model pairwise favored them.
- Combined V5 validation commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`; SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: `891` attacks / `1214` selected / `1209` rendered / `5` voicing drops / `113` measures. No invented/unplayable pitch, attack relocation, or timing change.
- Exact V5 render stream has `967` `v5AttackClass=baseline` events + **242 exact `v5AttackClass=rescued` events**. The rescued event set is explicit; no rescue-policy reconstruction is needed.
- Exact baseline performance metadata is preserved on `933` V5 events. The `34` corrected-primary notes + `242` rescued notes use the validated conservative neutral metadata fallback.

## PDF state
- Renderer upgrade commit `08ee3bcc1cec3428641741a8281206aa4218cb8d`; V5 materializer commit `a6505ba21e30af1b0e985b945de71ae3698bf08f`.
- Original successful V5 PDF workflow `32821861294`, artifact `9553423573`.
- Neutral-policy validator commit `4153614d58f286e9e218207393582b420bf24622`; workflow integration commit `06a57ca1cef84204a8b8a097980de7974989db0b`.
- CPU-only rerender persisted in bot commit `f160d2a7c0d047584650913d182cf3b427b8d1a2` with policy validation PASS.
- Current render remains 6 Letter pages, `1209` events / `891` onsets / `113` measures / `21` technique events.
- V5 render-stream SHA256 remains exactly `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Current PDF SHA256 is `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5` (1,748,095 bytes). It differs from the prior PDF SHA only because the PDF CreationDate/ModDate changed during rerender; the first/middle/last inspection PNG SHA256 values are byte-identical to the prior run, so inspected visual output is unchanged.

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

## Source-only evidence available
- Authorized artifact `9548666053` contains all `967` exact baseline events with downstream metadata, `precisionReplayEvidence` for all `984` eligible attacks and `10,585` candidate pitches, and scalar two-view candidate evidence for every V5 rescued pitch.
- Expanded downstream inspector artifact `9559978873` confirms all 967 baseline events have `rhythmSustain`; 669 have `rhythmSustainShadow`; 25 have legato/technique evidence.
- Exact join test: **967/967 baseline events** and **242/242 rescued V5 events** map to authorized `precisionReplayEvidence` candidate records by `(measure, step, midi)`.
- Strict grouped/blocked scalar-only reconstruction predicts exact baseline `durationSteps` only about **71%** (MAE ~`0.71` steps; within-one-step ~`86%`). It remains rejected for production/freeze.

## Exact approved source capture — CPU-only, no Modal
- Source export workflow commit `1b7dff297a07dec2453cebd149cf9053d8a27a14`; run `32866343856`; artifact `9570238003` (`v143-approved-source-audio`, retention 1 day).
- Downloaded source independently verified SHA256 exactly `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Temporary workflow removed in commit `069798d534eabae61e297cfa28da5b61636af1d1`.
- No Modal/GPU was used for the CPU experiments.

## Full-mix sustain result — CLOSED as a promotion source
- Exact approved full mix produced sustain evidence for `695/967` baseline events (`71.87%`).
- Against the `669` historical two-separated-view shadows, full mix produced evidence for `580`; exact duration-step agreement was only **72.59%**, MAE `0.714` steps, within-one-step `87.59%`.
- Against final promoted baseline duration, exact agreement with no-evidence treated as one step was only **74.77%**, MAE `0.724` steps, within-one-step `87.69%`.
- Long-sustain discrimination is unreliable: >=4 steps precision `49.5%`, recall `66.2%`; >=8 steps precision `31.4%`, recall `55.0%`.
- **Decision:** no threshold tuning, no promotion, no generalization to the 34 corrected or 242 rescued V5 events.

## Full-mix bends/legato result — CLOSED as a promotion source
- Historical authorized baseline has `25` technique-positive events: slide-up `10`, slide-down `7`, pull-off `4`, hammer-on `4`; zero bend positives.
- Unchanged single-view bend detector on exact full mix produced **238 bend predictions** against zero historical two-view-consensus positives.
- Unchanged single-view legato detector produced `49` predictions: `14` exact-type TPs, `35` FPs, `11` FNs; precision **28.57%**, recall **56.0%**.
- **Decision:** no threshold tuning and no full-mix semantic inference for corrected/rescued events.

## Conservative neutral metadata policy — VALIDATED
- Policy: `preserve-exact-baseline-metadata-else-one-step-no-technique-no-relational-semantics`.
- Validator: `analyzer/validate_v143_v5_neutral_metadata_policy.py`.
- Persisted report: `debug/v143-contextual-prune/v5-professional-pdf/neutral-metadata-policy-report.json`.
- Validation PASS: `1209` rendered; `933` exact preserved metadata; `276` neutral = `34` corrected baseline primary + `242` rescued.
- Every neutral event is one-step, technique-empty, and contains no durationSeconds/sustainTier/bend/legato relational semantics.
- Preserved identity/duration/techniques exactly match the authorized baseline source.
- No preserved legato link targets a neutral event.
- Historical technique identities: `25`; lost through corrected-primary replacement: `4`; invented technique identities: **0**. All four omissions occur only at corrected attacks.
- `metadataPolicyResolved=true`, `neutralFallbackConservative=true`, `validationPassed=true`, while `freezeReady=false` remains intentionally unchanged.

## Freeze-readiness audit — COMPLETE
- Protected runtime blob was re-read from the branch and is still exactly `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- `materialize-report.txt` has `validationPassed=true` and `freezeReady=false`; `neutral-metadata-policy-report.json` has every listed check true, `validationPassed=true`, `metadataPolicyResolved=true`, and `freezeReady=false`; `render-report.json` is reference-free and also carries `freezeReady=false`.
- Materializer commit `a6505ba21e30af1b0e985b945de71ae3698bf08f` sets `freezeReady` to literal `False`; it is not computed from a failing check.
- Neutral-policy validator commit `4153614d58f286e9e218207393582b420bf24622` likewise sets `freezeReady` to literal `False` after computing `validationPassed` independently from all policy checks.
- Current render script `scripts/v143-render-v5-shadow-pdf.mjs` explicitly refuses any input whose `freezeReady` is not `false`, then emits `freezeReady:false` in its render report. The render sentinel is therefore deliberate, not a failed render invariant.
- **Conclusion:** all observed `freezeReady=false` values are final-gate safety sentinels. They must remain false and must not be weakened to represent source-only freeze readiness.

## Source-only frozen candidate — VALIDATED / FROZEN
- Pre-freeze branch commit pinned by manifest: `f415bf180fc402a3aa8292304a90b4916d32a5d3`.
- Frozen-candidate manifest created in commit `1525f04c9b1750860afe7070bebc4eeae1947f0c`: `debug/v143-contextual-prune/v5-professional-pdf/source-only-frozen-candidate-manifest.json`.
- Manifest pins protected runtime, materializer, neutral validator, renderer, render contract, V3/V4/V5 evidence blobs, exact render stream/PDF/inspection blobs, known SHA256 identities, counts, tempo, and closed-gate semantics.
- Source-only freeze validator created in commit `17254353bb64944f410741792052f3ea85aaeaef`: `analyzer/validate_v143_v5_source_only_frozen_candidate.py`.
- Dedicated CPU-only validation workflow created in commit `f771707af5ed5ae16efbc36c199eb6f3a1d1b479`: `.github/workflows/v143-validate-source-only-frozen-candidate.yml`.
- Workflow run `32872086764` completed **SUCCESS**. Persisted report: `debug/v143-contextual-prune/v5-professional-pdf/source-only-freeze-validation-report.json`, Git blob `2f28ca4d382b0cbe78dabfdc647691edfbbba78e`.
- Report verdict: `sourceOnlyFreezeValidationPassed=true`, `sourceOnlyFrozen=true`, all checks true, `mismatches=[]`, `referenceFree=true`, `professionalReferenceUsed=false`, `professionalHoldoutOpened=false`, `modalInvoked=false`, `productionModified=false`.
- Exact Git-blob pins and exact SHA256 pins all passed from committed branch bytes. Counts, tempo, neutral policy, render report, render stream, PDF, and inspection evidence all passed their frozen identities.
- Existing final-gate `freezeReady=false` sentinels remain intentionally untouched.
- **Candidate is now immutable. No content, timing, metadata, renderer-driven selection, threshold tuning, or candidate replacement is permitted before or after opening the final professional holdout.**

## Professional holdout/scorer audit — IN PROGRESS
- Audit began on 2026-08-25 on the exact branch `v143-contextual-prune-lobo`, after the source-only freeze had already passed.
- The frozen manifest/validator state explicitly records `professionalReferenceUsed=false` and `professionalHoldoutOpened=false`; therefore the source-only freeze did not invoke or depend on the professional scorer/reference.
- Initial repository-wide path/content search found no authoritative file literally named `holdout`; generic `scorer` hits predominantly point at older Modal-era analyzer versions. Those paths are **not** being treated as authoritative because the current checkpoint forbids Modal/GPU use and authorizes only a source-only CPU audit.
- No professional reference/holdout content has been opened. No scoring run has been triggered. No Modal/GPU has been used.
- Frozen candidate content, timing, metadata, thresholds, renderer, and selection remain unchanged.
- Audit must next identify the exact authoritative scorer entrypoint, invocation, reference completeness checks, scoring semantics, immutable-candidate binding, and one-time/no-retuning safeguards **without opening the reference data itself**.
- This audit state was intentionally persisted before any deeper scorer inspection or any possible final holdout trigger.

## Current integrity
- Protected runtime untouched.
- `main`/Production untouched.
- Source-only freeze was completed without professional reference/scorer access.
- Professional holdout/reference remains unopened; final scorer remains untriggered.
- No Modal/L4 used in this continuation.
- Current persisted hashes remain render stream `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`, PDF `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`, inspection first `33693e32ee4a578e48f7e96360d0c06191bf0fff16f68d76d97e1e384f1aa5f3`, middle `1e265e8486e75505262de9ea33dea444f60731e025db20dea063dd1f75448775`, last `487df510c3931403017576dac2fe3e587479b9d827a496ea9d792fa5a2764671`.

## Next exact actions
1. Continue the audit by locating the exact final professional holdout/reference/scorer entrypoint and reading scorer/control-path source only; do not open reference payloads.
2. Save the completed audit state before triggering any final holdout.
3. If and only if the reference is complete and the official holdout path is valid, run it once against the immutable frozen candidate. Persist the result; **do not tune, modify, or select a replacement candidate from failures.**
4. Keep final-gate `freezeReady=false` sentinels false unless score >=0.99, critical mismatches=0, PDF fidelity=1.0 are all independently proven.
5. Do not claim Rhythm complete before all final completion gates pass.
