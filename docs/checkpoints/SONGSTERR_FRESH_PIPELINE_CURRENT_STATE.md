# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 19:28 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- GuitarSet/V3, IDMT/V4, V5/FLGD, duration research and protected-song execution remain closed/revealed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected-song embargoed.
- Ordinary metadata research/coding/GitHub/CPU/checkpoint work may proceed.
- **2026-09-14 19:18 ET user authorization:** the purpose-built route is explicitly reopened and the user authorizes actions reasonably deemed necessary. Apply that authorization conservatively: design/coding/synthetic CPU CI first; procurement/spending, performer/vendor contact or hiring, calibration recording, holdout recording/data acquisition, or gated compute may proceed only when objectively necessary to advance the frozen validation plan. Do not spend/contact/acquire merely because authorization exists. V6/scoring/correctness constraints below remain unchanged.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve every decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance match onset <= `0.050 s`, pitch <= `50 cents`; V6-positive precision with one-sided 95% Wilson LB; >=`1,000` pooled V6-positive estimates; pooled Wilson LB >=`0.9900`; player/category strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact `guitar-techs-v6-alignment-inventory`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.

Artifact/inventory integrity was independently reverified 2026-09-14 18:27 ET:
- job `completed/success`;
- artifact live/unexpired;
- GitHub archive digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`;
- fresh downloaded ZIP independently SHA-256 matched the same digest;
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`;
- 104 DI/MIDI pairs, 18,934 reference events, all 104 alignment statuses `OK`;
- structural anomalies 5 same-key overlaps + 7 unmatched note-ons;
- frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`.

Run status was rechecked again at 2026-09-14 19:07 ET and remained `completed/success` on the correct branch/head.

Basic Pitch/V6/correctness were never run on Guitar-TECHS. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after a structural pass may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

## REPLACEMENT CORPUS STATUS

No currently reviewed public candidate clears all five gates.

Closed/rejected or otherwise non-qualifying families include: Guitar-TECHS (closed C), AG-PT-set, GAPS v1.1/v2, François Leduc Guitar Dataset, EGSet12, IDMT-SMT-Audio-Effects / GUITAR-FX-DIST, EG-Solo / G&N / TENT, EG-IPT, Multimodal Electric Guitar Data, MMIP, M-M Guitar / Perez-Carrillo, GIHME, MUSMET, Klangio GST-MM-2025, EGFxSet as narrow backup only, EGDB / EGDB-PG, EGDB-NDSP, GuitarDuets, DoMP, Geoff Bremner Multimodal Music Corpus as private-license lead only, GRAUX / Water commercial packs, PolyMap, TART 2026, Five guitar dataset, SJSU Patil 2025 thesis corpus, FretboardFlow, ToneTwist AFx, GM Dataset (Chieppa et al. 2025), Semantic Timbre, and other previously logged non-qualifying synthetic/stem/robot/chord-only leads. GOAT mentions remain literature-only and do not reopen archived GOAT/reference scoring.

Latest sweep decision remains `NO_NEW_ADMISSIBLE_REPLACEMENT_HOLDOUT`. Public/institutional/commercial search is near exhausted but this is not proof that no qualifying corpus exists.

## PURPOSE-BUILT HOLDOUT — ACTIVE UNDER EXPLICIT AUTHORIZATION

The purpose-built independent-sensor route is active under the user's explicit 2026-09-14 19:18 ET authorization. Conservative order remains binding: semantics/contract -> synthetic-only CI -> reference-blind structural-audit tooling -> only then objectively necessary procurement/contact/calibration/data acquisition. Real holdout correctness remains forbidden until all frozen gates clear.

Design authority:
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`, commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`, commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`, commit `2b191b39f2f1c19564f1353381779acbc96fbeda`.

### Capture-manifest V2.1 — SYNTHETIC CI PASS

V2 historical implementation remains inherited history. It contained one demonstrated internal contradiction: a nominal valid failed-attempt -> admitted-retry fixture reused one `underlyingPerformanceId` within the same frozen slot, while V2 globally rejected any repeated underlying ID across attempts.

V2.1 fixes only that identity semantics defect while preserving all V1/V2 fail-closed boundaries:
- same-slot retries must retain the same `underlyingPerformanceId`;
- changing the underlying identity within a slot fails;
- reuse of one underlying identity across distinct slots/population units fails;
- first-transport-valid-take chronology remains inherited from V1.

Implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`, commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`.
Synthetic tests: `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2_1.py`, commit `ff5717a4aeb9b74e971694703f6d6cb785389845`.
Workflow head: `3d7f1770a3b8df0018008a49defe189db306de39`.
Successful GitHub-hosted CPU run: `34908936464`, job `104191861049`, conclusion `success`.
Detailed checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_MANIFEST_V2_1_SYNTHETIC_CI_2026-09-14.md`, commit `9d3b17b392bd486753cb657318c048a7ae2460a7`.

The successful run explicitly reasserted that a nominal declaration may reach only `mayAdvanceToReferenceBlindStructuralAudit:true`; all of `authoritativeStructuralSuitabilityEstablished`, `basicPitchAuthorized`, `v6Authorized`, and `correctnessAuthorized` remain false.

Initial run `34908849001` failed because the first workflow version also required the superseded contradictory V2 test suite to pass. That demonstrated the known V2 contradiction rather than a V2.1 safety failure. The final authoritative gate runs V1 + V2.1; V2 remains inherited implementation history.

Existing eight-stage preregistration/artifact-proof governance remains historical PASS and should not be reopened absent a concrete new loophole. Successful declaration/governance never establishes source truth, structural suitability, Basic Pitch/V6/correctness authorization, model validation, customer eligibility or delivery advancement.

## NEXT ALLOWED ACTION

1. Verify live branch head and this checkpoint before each continuation/mutation.
2. Freeze and implement the purpose-built **reference-blind physical-reference structural audit** using only independent pitch/birth reference streams, configuration/calibration, hashes and clock/sync evidence; evaluated DI/model outputs are forbidden inputs.
3. Synthetic-test and ordinary-GitHub-CPU-CI that structural-audit contract before any real calibration/holdout data is used.
4. Structural audit must fail closed on ambiguous pitch state at birth, unmatched events, nonmonotonic timestamps, impossible transitions, same-key overlaps, sensor/configuration/hash mismatch, and clock/sync failure outside frozen non-holdout-calibrated limits.
5. Use procurement/contact/calibration/data acquisition only when the structural-audit paper/code/CI gate demonstrates those steps are actually necessary; record the decision before acting where practicable.
6. Do not perform real holdout correctness, tune V6, or alter frozen alignment/scoring rules from any holdout observation. Exactly one ordinary-GitHub-CPU correctness run remains the eventual maximum after all gates pass.
7. Archived V143/Gomyway, GOAT/reference scoring, Guitar-TECHS rescue, protected-song execution and the other explicitly closed lines remain closed despite this broader purpose-built authorization.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; NC/ND or otherwise restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate/simultaneous-view derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-corpus optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; purpose-built calibration/model decisions informed by admitted holdout correctness; Production/customer promotion without untouched external validation + separate policy review. Heavy GPU remains unnecessary for the current structural-audit contract/CI stage.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`. Guitar-TECHS remains closed outcome C before correctness; V6 method/scoring remain frozen; no replacement-holdout correctness has been exposed. Public replacement-corpus search remains near exhausted with no current candidate clearing all five gates. User authorization at 2026-09-14 19:18 ET keeps the purpose-built route active, but proceed conservatively. Capture-manifest V2.1 has now passed synthetic GitHub CPU CI at run `34908936464`, job `104191861049`; it authorizes only the next reference-blind structural-audit tooling stage. Current immediate action is to implement/freeze/synthetic-test that physical-reference structural audit without evaluated DI or model inputs. Preserve all fail-closed boundaries (`modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration paused, Policy C `UNENROLLED`, protected-song execution embargoed). Do not reopen V143/Gomyway or GOAT/reference scoring unless separately explicit.