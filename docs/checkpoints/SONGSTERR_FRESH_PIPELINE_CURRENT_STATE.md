# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless explicitly reopened by the user.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected song embargoed.

## USER COMPUTE AUTHORIZATION RULE

Ordinary research/coding/GitHub/CPU/test/checkpoint work may proceed at assistant discretion. Explicit user authorization is required before any Modal, Vercel heavy-GPU, or L4 GPU run.

## CLOSED / REVEALED LINES

V1/V2 rejected diagnostics. GuitarSet/V3 and IDMT/V4 closed/revealed. V5/FLGD closed/rejected and may not be rerun or tuned. Archived V143/Gomyway and GOAT/reference scoring remain closed.

## V6 — METHOD + SCORING FRAMEWORK FROZEN / NO REAL CORRECTNESS YET

Final V6 method preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.

Frozen implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`
commit `3a6cbb144fec5613ab6350deb6539297d713df28`
blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

External scoring framework preregistration:
`docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Do not change V6 constants, Basic Pitch settings, DI-only canonical audio path, event-preservation rule, matcher, 50 ms/50-cent tolerances, Wilson statistic, admission gates, strata rules, or deferred-reveal/single-run rule from holdout observations.

## GUITAR-TECHS V6 AUDIT — COMPLETE / REJECTED BEFORE CORRECTNESS

Frozen audit preregistration:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_PREREGISTRATION.md`
commit `29818b9bfcb11b0da2b3e9efb57c5f2cd51193ae`.

Official audit run `34754519541`, job `103716527380`: **SUCCESS**.
All workflow steps completed successfully, including all nine exact package audits, merge, fail-closed verification and artifact upload.

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Artifact:
- name `guitar-techs-v6-alignment-inventory`
- ID `10317695640`
- GitHub archive digest / downloaded ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`

Audit population facts:
- 9 verified packages
- 104 paired DI/MIDI performances
- 18,934 paired reference events
- 0 unpaired DI / 0 unpaired MIDI
- all 104 alignment statuses `OK`
- WAV: 102 at 48 kHz, 2 at 44.1 kHz; 44 mono, 60 stereo; all PCM_24
- MIDI: all format 1, all PPQ 960
- pairing identity manifest `24ff1b4eef07f28eb678f38fbec80f8cc26668329812868a89992e20eb73efa7`
- alignment lag manifest `95b244d78014e20ea0f468ecf88aacf90e8442f4aef675b246845202d98fcc84`
- proposed-population manifest `bd239d63ba39a370f7c9e09df544b3b207596acf523b09e2be57bbc49cf0b765`
- lag range -8..+10 hops, median -5 hops; all-within-one-hop false

Reference-blind MIDI anomalies:
- 5 same-key overlaps
- 7 unmatched note-ons
- 0 unmatched note-offs

The preregistered structural gate requires zero MIDI anomalies. Therefore the official frozen decision is:

`C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`

`datasetStructurallySuitable:false`.

This is a structural/reference-blind rejection, not a model-correctness result. Basic Pitch was not invoked, V6 was not invoked, and correctness was not computed.

### Consequence

Guitar-TECHS is closed as the V6 external holdout. Do **not** score it, repair/drop anomalous events to rescue it, create an A/B scoring binding, or rerun it for correctness. Its lag/population identities remain reproducibility records only.

## CURRENT ACTIVE WORK — REPLACEMENT UNTOUCHED HOLDOUT SEARCH

Search only metadata, license, downloadable structure and pre-correctness alignment feasibility for a new untouched real-guitar corpus.

A candidate must be defensibly usable for V6 admission validation, ideally with:
- real isolated guitar audio (prefer clean DI or equivalent);
- note-level MIDI or equivalent pitch/onset reference;
- enough material for >=1,000 potential V6-positive events to be plausible;
- clear redistribution/research license and stable public artifact identity;
- no prior use in V3/V4/V5 or protected-song work;
- no model correctness inspection before a new corpus-specific audit preregistration;
- reference/audio alignment that can be audited reference-blind before scoring.

Metadata/license/structure investigation is allowed. Do not run Basic Pitch/V6 correctness on any replacement corpus before a corpus-specific audit preregistration, immutable inventory/alignment result, and frozen population identities.

## NEXT ALLOWED ACTION

1. Search public metadata/licensing for candidate untouched real-guitar datasets.
2. Shortlist candidates without correctness testing.
3. For the strongest candidate, document source/version/license/files/reference type and contamination check.
4. Before downloading/auditing real audio/reference pairs, freeze a corpus-specific reference-blind inventory/alignment preregistration analogous to the Guitar-TECHS process.
5. Run only that structural/alignment audit first.
6. If unsuitable, reject without correctness and continue search. If suitable, bind immutable identities into the already-frozen V6 scoring framework, build controlled no-real-correctness harness CI, then launch one official CPU correctness run only after all prerequisites are green.
7. Ask the user only if Modal, Vercel heavy-GPU or L4 execution becomes necessary.

## STILL FORBIDDEN

- any Guitar-TECHS V6 correctness
- post-hoc repair/exclusion of Guitar-TECHS anomalies to rescue the holdout
- V5 FLGD rerun/post-result tuning
- using FLGD/IDMT/GuitarSet/protected-song correctness to tune V6
- changing frozen V6/scoring rules from any holdout observation
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus optimizer/threshold sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without untouched external validation + separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. Guitar-TECHS audit is complete and immutable with outcome C; do not score or rescue it. V6 method and scoring framework remain frozen and no V6 real-corpus correctness has been exposed. Current work is metadata/license/structure search for a new untouched real-guitar holdout, followed by a newly preregistered reference-blind structural/alignment audit before any correctness.
