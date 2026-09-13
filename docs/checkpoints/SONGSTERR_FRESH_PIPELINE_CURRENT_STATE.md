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

Official audit run `34754519541`, job `103716527380`: **SUCCESS**.
All nine exact package audits, merged-result generation, fail-closed verification and artifact upload completed successfully.

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Artifact:
- ID `10317695640`
- archive digest / downloaded ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`

Audit facts:
- 9 verified packages
- 104 paired DI/MIDI performances
- 18,934 paired reference events
- 0 unpaired DI / 0 unpaired MIDI
- all 104 alignment statuses `OK`
- pairing identity manifest `24ff1b4eef07f28eb678f38fbec80f8cc26668329812868a89992e20eb73efa7`
- alignment lag manifest `95b244d78014e20ea0f468ecf88aacf90e8442f4aef675b246845202d98fcc84`
- proposed-population manifest `bd239d63ba39a370f7c9e09df544b3b207596acf523b09e2be57bbc49cf0b765`
- lag range -8..+10 hops, median -5 hops; all-within-one-hop false
- MIDI anomalies: 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs

The preregistered structural gate requires zero MIDI anomalies. Official decision:

`C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`

`datasetStructurallySuitable:false`.

Basic Pitch was not invoked, V6 was not invoked, correctness was not computed. Guitar-TECHS is closed as the V6 external holdout: do not score, repair/drop events to rescue, or create an A/B binding.

## CURRENT ACTIVE WORK — REPLACEMENT UNTOUCHED HOLDOUT SEARCH

Metadata/license/structure research checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md`
latest refinement commit `f91c25c5b3a781a87ea024e296af1e9231df14af`.

No correctness has been run on any replacement candidate.

### Leading candidate: GAPS — STILL BLOCKED

Public metadata describes GAPS (Guitar-Aligned Performance Scores) as ~14 hours / 300 real solo classical-guitar performances from >200 performers with high-resolution note-level MIDI/MusicXML alignment. Hugging Face v1.1 includes audio, exposes audio/match/midi/musicxml resources, is ~16.4 GB, and its dataset-card metadata declares MIT.

Fresh review also confirms the older Zenodo release distributed aligned MIDI/scores/downbeats while pointing to YouTube URLs for audio/video and recommends the later Hugging Face release that includes audio.

This does **not** resolve the pre-audit rights gate: no separate surfaced statement explicitly grants redistribution/relicensing rights for every underlying third-party performance recording. Do not assume repository-level MIT metadata clears independent audio copyright/provenance. Do not download/audit GAPS audio yet.

Contamination review remains incomplete: exact-corpus-name GitHub code search returned no indexed hit and generic `GAPS` hits were unrelated analyzer variables, but repository search is not a guaranteed branch-history audit of `songsterr-fresh-pipeline-v1`. A branch-specific contamination check is still required before selection.

### Backup: EGFxSet

Real electric-guitar hardware recordings, stable Zenodo release, CC BY 4.0/open-access description, 8,970 five-second files. However only 690 unique clean tones exist and public metadata does not establish high-resolution onset times. It is probably too narrow/duplicative for the official admission holdout unless those issues can be resolved pre-correctness.

### Metadata lead: GIHME — PAPER FOUND, DATASET STILL UNRESOLVED

Public metadata describes ~10 hours of richly annotated real hexaphonic-guitar improvisations with note/technique/tuning/effect annotations. The surfaced Zenodo record `6798338` is definitively the conference paper only (`79.pdf`, ~680.6 kB), not the underlying dataset. Dataset package location, license, exact annotation timing representation and immutable audio/reference identities remain unresolved.

Explicit exclusions: GuitarSet (V3 revealed), IDMT (V4 revealed), Guitar-TECHS (outcome C), Slakh/SynthTab (synthetic), GuitarJam (no surfaced note-level truth).

## NEXT ALLOWED ACTION

1. Continue GAPS rights/provenance research, seeking explicit audio redistribution/reuse authority rather than relying solely on repository-level MIT metadata.
2. Perform a branch-specific contamination audit of `songsterr-fresh-pipeline-v1` for prior GAPS corpus truth/correctness use.
3. Resolve GIHME dataset location/license/annotation representation; do not treat the paper record as the dataset.
4. Keep EGFxSet as a narrow backup and determine whether a fixed/preregisterable note onset exists.
5. Select one replacement only after rights/provenance/untouched status are defensible.
6. Freeze a corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio/reference pairs.
7. Run only structural/alignment audit first. If unsuitable, reject without correctness. If suitable, bind immutable identities into the already-frozen V6 scoring framework, build controlled no-real-correctness harness CI, then launch exactly one ordinary-GitHub-CPU official correctness run after prerequisites are green.
8. Ask the user only if Modal, Vercel heavy-GPU or L4 execution becomes necessary.

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

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. Guitar-TECHS audit is complete and immutable with outcome C; do not score or rescue it. V6 method and scoring framework remain frozen and no V6 real-corpus correctness has been exposed. Current work is replacement-holdout metadata/license/structure research. GAPS remains the strongest scientific lead but is still blocked on explicit audio-rights/provenance and a branch-specific contamination audit. GIHME's surfaced Zenodo item is only the paper, not the dataset. No candidate may be exposed to correctness before a new corpus-specific preregistered reference-blind audit and immutable suitable result.
