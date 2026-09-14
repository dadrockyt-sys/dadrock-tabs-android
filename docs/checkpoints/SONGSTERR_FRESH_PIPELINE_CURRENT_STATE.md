# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 19:18 America/Toronto
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

Key detailed checkpoints remain authoritative for their individual findings, including:
- `docs/checkpoints/SONGSTERR_FRESH_GAPS_V1_1_RELEASE_DELTA_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_FRANCOIS_LEDUC_DATASET_METADATA_REFERENCE_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_EGDB_PG_V2_DERIVATIVE_HOLDOUT_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_EGDB_NDSP_DERIVATIVE_HOLDOUT_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_FIVE_GUITAR_DATASET_METADATA_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_SJSU_PATIL_2025_CORPUS_METADATA_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_FRETBOARDFLOW_METADATA_REFERENCE_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_TONETWIST_AFX_DERIVATIVE_HOLDOUT_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_GM_DATASET_METADATA_REFERENCE_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_LATE_SUMMER_2026_CORPUS_DELTA_REVIEW_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_V6_2026_09_14_EVENING_CORPUS_DELTA_SWEEP.md`
- `docs/checkpoints/SONGSTERR_FRESH_V6_2026_09_14_POST_HANDOFF_DELTA_SWEEP.md`
- `docs/checkpoints/SONGSTERR_FRESH_V6_2026_09_14_1827_CORPUS_DELTA_SWEEP.md`, commit `9bff78da4e2dd6fa3e9898ef36852d49f52e6543`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_2026_09_14_1907_CORPUS_DELTA_SWEEP.md`, commit `c36860abd62302a5aef049e42487b926660a4979`.

Latest sweep decision: `NO_NEW_ADMISSIBLE_REPLACEMENT_HOLDOUT`. Fresh 2025–2026 synchronized-audio/MIDI and note-level guitar searches resurfaced Guitar-TECHS, GAPS, MMIP, GuitarSet, IDMT, TART, GOAT literature, NSynth mirrors and non-performance guitar-tone metadata; no new primary source established all five pre-media gates simultaneously.

Public/institutional/commercial search is near exhausted but this is not proof that no qualifying corpus exists.

## PURPOSE-BUILT HOLDOUT — REOPENED UNDER EXPLICIT AUTHORIZATION

The purpose-built independent-sensor route is active again under the user's explicit 2026-09-14 19:18 ET authorization. The conservative order is binding: reconcile/freeze semantics and contract code -> synthetic-only tests/CPU CI -> reference-blind structural-audit tooling -> only then objectively necessary procurement/contact/calibration/data acquisition. Real holdout correctness remains forbidden until all frozen gates clear.

Design authority:
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`, commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`, commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`, commit `2b191b39f2f1c19564f1353381779acbc96fbeda`.

Current implementation baseline includes `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2.py` and `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2.py`. V2 adds separate evaluated-audio/pitch/birth paths, non-holdout/no-model calibration, independent clock/sync proof, machine-verifiable acquisition-failure evidence, and underlying-performance identity while remaining fail-closed for Basic Pitch/V6/correctness. A live review on reopening found one identity-rule inconsistency to resolve before treating V2 as CI-ready: retries intentionally reuse one `underlyingPerformanceId` within a slot, but the current global-duplicate check can reject that same-slot continuity. Required semantics: same-slot retries must retain the same underlying identity; the same underlying identity must be rejected across distinct slots/population units.

Existing eight-stage preregistration/artifact-proof governance remains historical PASS and should not be reopened absent a concrete new loophole. Successful declaration/governance may authorize only `mayAdvanceToReferenceBlindStructuralAudit:true`; it never establishes source truth, structural suitability, Basic Pitch/V6/correctness authorization, model validation, customer eligibility or delivery advancement.

## NEXT ALLOWED ACTION

1. Verify live branch head and this checkpoint before each continuation/mutation.
2. Repair and test the V2 same-slot-retry vs cross-slot-duplication identity semantics without weakening V1 first-valid-take chronology.
3. Complete synthetic-only V2 contract tests and ordinary GitHub CPU CI; keep all outputs fail-closed for correctness.
4. Freeze/reference the physical-reference structural-audit contract before any real calibration or holdout media are used.
5. Use procurement/contact/calibration/data acquisition only when the preceding paper/code/CI gates demonstrate they are necessary; record every such decision in this checkpoint before acting where practicable.
6. Do not perform real holdout correctness, tune V6, or alter frozen alignment/scoring rules from any holdout observation. Exactly one ordinary-GitHub-CPU correctness run remains the eventual maximum after all gates pass.
7. Archived V143/Gomyway, GOAT/reference scoring, Guitar-TECHS rescue, protected-song execution and the other explicitly closed lines remain closed despite this broader purpose-built authorization.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; NC/ND or otherwise restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate/simultaneous-view derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-corpus optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; purpose-built calibration/model decisions informed by admitted holdout correctness; Production/customer promotion without untouched external validation + separate policy review. Heavy GPU remains disfavored and should be used only if genuinely necessary; it is not necessary for current V2 contract/CI work.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`. Guitar-TECHS remains closed outcome C before correctness; V6 method/scoring remain frozen; no replacement-holdout correctness has been exposed. Public replacement-corpus search remains near exhausted with no current candidate clearing all five gates. On 2026-09-14 19:18 ET the user explicitly authorized actions deemed necessary, so the purpose-built route is reopened, but proceed conservatively: code/design/synthetic CPU CI before external spend/contact/acquisition. Current immediate issue is the V2 `underlyingPerformanceId` semantics: same-slot retries must preserve one identity while cross-slot reuse must fail. Preserve all fail-closed boundaries (`modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration paused, Policy C `UNENROLLED`, protected-song execution embargoed). Do not reopen V143/Gomyway or GOAT/reference scoring unless separately explicit.