# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Keep timing frozen unless new source-only evidence proves otherwise. Tempo remains exactly `129.19921875`.

## Historical professional-score state — reference now closed
- Score 1 retired: 725 attacks → 985 notes, 113 measures, PDF fidelity 1.0; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Score 2 retired after harmonic contradiction guard: 889 events, PDF fidelity 1.0; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; critical mismatches `1635`.
- Do not score/tune against either retired identity again.

## Successful paid capture — preserved for CPU reuse
- Authorized retry workflow run `32805316807` completed successfully.
- Successful capture/replay commit: `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`.
- Exactly one Modal command was used for the successful retry; no automatic retry is allowed.
- Final lock is `captureState=completed`, `singlePaidCaptureConsumed=true`, `automaticRetryAllowed=false`.
- Capture counts: input/eligible attacks `984`; retained `725`; pruned `259`; original observed pitch hypotheses `7535`; eligible replay pitch hypotheses `10585`; stored selected pitches `970`; rendered pitches `967`; voicing drops `3`; fail-safe attacks `0`; measures `1–113`.
- CPU replay comparison: legacy selected pitches `891`; precision-v2 selected `970`; v2 adds `79`, removes `0`, across `75` attacks.
- All strict replay mismatch counts are zero. Deterministic voicing/string/fret/grid/onset replay is green.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Replay validation SHA256 `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`.
- Replay compare SHA256 `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`.
- Capture lock SHA256 `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Actions artifact `v143-precision-v2-one-shot-32805316807`, artifact ID `9548666053`, is only a secondary copy.

### Durable fixture
- Permanent manifest: `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`, commit `87b4b698010fa11c62e76e061a2bbe91825de5ba`.
- CPU-only materializer: `analyzer/materialize_v143_precision_fixture.py`, commit `72f43d8c82629b9ff388fa0013fe6e06b024a660`.
- Materializer reconstructs the exact successful files from pinned commit `c1451df...` and verifies SHA256 before use.
- Standard future workflow: materialize this fixture and do precision diagnostics/replay CPU-only first. A new paid capture requires fresh explicit authorization and should only be considered if a needed source-evidence dimension is absent from the preserved fixture.

## Precision-v2 fixed-retained pitch policy
Module: `analyzer/v143_contextual_prune_precision_shadow_v2.py`
Policy: `envelope-balanced-secondary-v2`.
- Non-harmonic observed secondaries use 2-of-3 score/attack/body at existing `0.80` floor.
- Harmonic upper secondaries `{12,19,24,28,31,36}` remain strict 3-of-3 at `0.92`.
- Primary/fundamental, no-invention and harmonic protections preserved.
- Replay schema 2 persists eligible attacks, retained identities, source-view A/B evidence, candidate MIDI universe, attack/body/continuity/score, grid/onset/error, precision strength and support counts.
- Exact replay scope is post existing `_best_rows_by_slot`; alternate raw carrier rows are not replayable.

## Exact CPU replay validators
- `analyzer/v143_precision_replay_artifact_validator.py`: reconstructs source-view aggregation, score/strength, exact attack policy, render subset and measure coverage.
- `analyzer/check_v143_precision_replay_corruption_rejection.py`: negative corruption guard.
- `analyzer/v143_precision_replay_policy_compare.py`: independently recomputes primary and legacy/v2 pitch sets.
- `analyzer/v143_precision_replay_voicing_validator.py`: exact deterministic string/fret plus grid/onset replay.
- `analyzer/v143_precision_paid_capture_finalizer.py`: strict lock binding.
- Successful paid product passed all of these before final lock.

## Attack-pruning diagnosis
Legacy precision attack gate:
- positive best pitch requires attack `>0.0` and body `>-0.25`.
- transient/body ratio `>=0.70`: retain.
- ratio `<0.60`: prune.
- ratio `0.60–0.70`: retain only if body-heavy composite `precisionStrength` beats all same-measure neighbors within ±2 sixteenth steps by `+0.20`.
- `precisionStrength = strongest pitch score + .10*min(4,sweepSupportMax) + .03*min(16,detectionCountSum) - 2*gridError`.
- Baseline CPU recomputation exactly reproduces all `725` retained attacks from the `984` eligible universe; mismatch count `0`.
- Original prune reasons: `130` ratio<0.60; `123` ratio 0.60–0.70 but not local composite max; `6` nonpositive attack/body.

### Attack shadow v1 — local transient peak
- `analyzer/v143_contextual_prune_attack_shadow_v1.py`, commit `674dd4de5331e079f80e6f2fc798b9c80de9d289`.
- `analyzer/v143_attack_shadow_v1_replay_validator.py`, commit `d917e1193bf57d3b31bebce2427fae9523ac7057`.
- Durable validation: `debug/v143-contextual-prune/precision-attack-shadow-v1-validation.json`, commit `bf25366d68561fc7c995e2b115e5e1314f8e7ff4`.
- Reuses the existing ±2-step radius and +0.20 local margin on the actual transient/attack dimension instead of composite strength; introduces no new numeric threshold.
- Adds `26`, removes `0` => `751` shadow attacks. `25` are sub-0.60 local transient peaks; `1` is exception-band.
- Independent pitch replay: `36` observed pitches; deterministic voicing drops `0`; unplayable primary `0`; invented pitch `0`; baseline grid-time collision `0`.

### Attack shadow v2 — existing exception band without composite-local-max
- `analyzer/v143_contextual_prune_attack_shadow_v2.py`, commit `1f4477291b138ec04d843369bdc35f3dcb590167`.
- `analyzer/v143_attack_shadow_v2_replay_validator.py`, commit `ab4642a463227385a28136767688b68ab7b42d0f`.
- Durable validation: `debug/v143-contextual-prune/precision-attack-shadow-v2-validation.json`, commit `43beb3cbba6d576171614cd47ad03aac78a8baaf`.
- Inside the already-existing `0.60–0.70` exception band, removes only the requirement to also be a composite-strength local maximum. Below `0.60`, retains only the v1 local-transient-peak rescue. **No new numeric threshold.**
- Exception-band source comparison strongly argues composite local dominance is relative loudness rather than detection quality:
  - retained band `33`, pruned band `123`;
  - median grid error retained `0.028569614160971923` vs pruned `0.019600000607709944` (pruned tighter);
  - median detection count retained `31` vs pruned `40`;
  - median A/B attack consistency retained `0.9663834710211912` vs pruned `0.9965938158894608`;
  - stemSupportMax=2: retained `32/33`, pruned `122/123`;
  - sweepSupportMax=4: retained `29/33`, pruned `108/123`.
- V2 adds `148` attacks total (`123` exception-band + `25` subfloor local transient peaks), removes `0`; shadow retained = `873`; remaining pruned = `111` (`105` positive subfloor nonlocal + `6` nonpositive).
- Independent v2 pitch replay on the 148 rescues: `214` observed/source-supported selected pitches; pitch-count distribution `94×1`, `44×2`, `8×3`, `2×4`; invented/unobserved `0`.
- Deterministic standard-tuning voicing renders `212`; only 2 drops:
  - measure 19 step 6: selected `[52,86]` → rendered `[52]`;
  - measure 113 step 14: selected `[43,44]` → rendered `[43]`.
- Unplayable primaries `0`; baseline grid-time collisions `0`.
- Structural recurrence is diagnostic only, not used for selection: `124/148` share step+primary with an already-retained attack elsewhere; `81/148` share exact step+primary+selected-pitch-set.

## Upstream correction contract
- Producer order: protected contextual prune → source-only correction → precision-v2 → promoted-harmonic guard → replay capture → deterministic voicing → downstream technique/sustain.
- Successful product `correctionDiagnostics` stores counts only:
  - `baseEventCount=952`
  - `correctedEventCount=984`
  - `rescuedEventCount=32`
  - `observedSlotCount=1795`
  - `strictSlotCount=1649`
  - `baseEventsPreserved=true`
  - `rescuesAreObservedSlots=true`
  - `localPeakRescueEnabled=true`
- Therefore the `984` precision inputs are already-selected/corrected attacks (`952` protected contextual-prune events + `32` strict source-only correction rescues), not raw slots. Precision then deletes `259` of those selected attacks.
- The pinned product does **not** preserve identities distinguishing the 32 correction rescues from the 952 base events; only counts survive. Do not invent that split.

## Remaining unresolved attack group
- After v2, `111` remain pruned: `105` physically positive ratio<0.60 nonlocal attacks plus `6` nonpositive.
- The 105 positive subfloor nonlocal attacks are statistically very similar to the 25 subfloor local-peak rescues on precision strength, grid error, detections, stem/sweep support and A/B attack agreement.
- However low transient/body ratio can still plausibly represent sustained bleed, so **do not broaden below the existing 0.60 floor without an independent source-only discriminator**.
- Next CPU-only goal: find an existing persisted artifact/diagnostic that can distinguish upstream protected-base vs correction-rescue identities, or derive another independent onset/transient criterion from already-persisted evidence. If unavailable, stop at v2 rather than guessing.

## Downstream replay boundary
- Schema 2 exactly supports precision attack/pitch policy experiments and deterministic voicing/string/fret/grid timing/physical onset.
- It does **not** persist the full downstream CQT/stem pitch-energy universe needed to recompute every bend/legato/sustain annotation for hypothetical newly retained attacks.
- Attack shadows v1/v2 are therefore validated **precision shadows**, not freeze-ready candidates. Do not fabricate downstream technique/sustain evidence.

## Timing state
- Relative sixteenth spacing remains strongly source-supported; at residual <=0.20 step, 697/697 pairs exactly match labeled grid gaps.
- Tempo remains exactly `129.19921875`.
- Beat repair has no leading phase-index error.
- Absolute bar phase remains weak/section-dependent; no global timing mutation justified.

## Current mutation/cost state
- No new Modal/L4 run after successful run `32805316807`.
- No professional scorer/reference invoked.
- No Production or `main` modification.
- No protected runtime modification.
- No freeze-ready candidate yet.

## Next exact actions
1. Reverify branch head and protected runtime blob after this checkpoint.
2. Stay CPU-only and use the pinned successful fixture.
3. Search current/historical source-only correction artifacts for a persisted identity split or other independent onset evidence; do not infer missing identities from counts.
4. Keep attack-shadow v2 as the strongest supported attack correction so far.
5. Do not broaden the remaining 105 positive subfloor events unless independent source evidence supports it.
6. Do not freeze or professional-score while newly rescued attacks lack recomputable downstream technique/sustain evidence.
7. No Modal/L4 unless user gives fresh explicit authorization for a clearly identified missing evidence dimension.
8. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
