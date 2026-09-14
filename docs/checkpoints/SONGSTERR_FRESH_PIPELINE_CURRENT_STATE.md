# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 19:07 America/Toronto
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
- Explicit user authorization is required before Modal, Vercel heavy-GPU, L4 GPU, purpose-built spending/procurement, performer/vendor contact or hiring, or recording/data acquisition.

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

## BRANCH-HEAD SCOPE NOTE

At the 2026-09-14 19:07 ET continuation start, the live branch head was `a06fc603e2b49e416483679813622ebedebbe07e` with purpose-built V2 design/implementation/test commits made after the prior canonical checkpoint timestamp. Those commits are outside the current continuation authority. They were not extended, executed, interpreted as authority, or used to reopen purpose-built acquisition. This canonical checkpoint remains controlling for current scope.

## PURPOSE-BUILT HOLDOUT

Purpose-built independent-sensor capture remains design-only background and is not an active execution path under the current user instruction to continue only replacement-holdout metadata/license/alignment search after Guitar-TECHS outcome C. No purchase, contact, hiring, calibration recording, holdout recording, or data acquisition without explicit user authorization.

Existing design checkpoints remain frozen historical authority and are not being advanced in this scope:
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`, commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`, commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`.

## NEXT ALLOWED ACTION

1. Verify live branch head and this checkpoint before each continuation.
2. Continue metadata/license/alignment search only for genuinely new untouched real-guitar holdout evidence, authoritative rights changes, or a newly established independent performed onset+pitch reference.
3. If a candidate clears all five pre-media gates, stop before media access and freeze a candidate-specific reference-blind inventory/alignment preregistration.
4. Do not perform correctness, tune V6, or alter frozen alignment/scoring rules from any holdout observation.
5. Ask before Modal, Vercel heavy-GPU, L4 GPU, purpose-built spending/contact/acquisition, or other explicitly gated compute/acquisition work.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; NC/ND or otherwise restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate/simultaneous-view derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-corpus optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; Production/customer promotion without untouched external validation + separate policy review; Modal/Vercel heavy-GPU/L4 without explicit authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`. Guitar-TECHS is closed outcome C before correctness; the official successful audit artifact remains integrity-verified with archive SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125` and merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`. V6 method/scoring remain frozen. No replacement-holdout correctness has been exposed. Latest metadata/license/reference sweep found no new candidate clearing all five pre-media gates. Purpose-built V2 commits currently present on the branch are outside this continuation scope and must not be treated as reopening that path. Continue only genuinely new untouched real-guitar holdout research; stop before media access if a candidate clears the gates. Keep `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration paused, Policy C `UNENROLLED`, protected-song execution embargoed.
