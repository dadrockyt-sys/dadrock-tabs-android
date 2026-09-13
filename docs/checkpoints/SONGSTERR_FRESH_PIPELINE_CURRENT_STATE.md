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

Metadata/license/structure research checkpoints:
- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md`, latest substantive update commit `64d9516d0efbba380769bd6cc52f93572393180a`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_SEARCH_UPDATE_2026-09-13.md`, commit `8d2cf13c1e776be190ee026c18625c1e41e27165`.

No V6 correctness has been run on any replacement candidate.

### GAPS — REJECTED ON EXPLICIT RIGHTS TERMS

GAPS is scientifically attractive (~14 h, 300 performances, >200 performers, high-resolution note-level MIDI), and the current Hugging Face repository advertises MIT metadata. However the official GAPS companion site explicitly states that the dataset contains copyright material, is limited to non-commercial research, is permission-bound to the signing researcher/organisation, and may not be sold/leased/published/distributed to third parties without written permission.

Disposition: **do not use/download/audit GAPS for this V6 admission path unless explicit written permission is later obtained from the GAPS administrator.**

### EGSet12 — REJECTED AS NOT UNTOUCHED

A controlled full-history audit found pre-search corpus/project exposure in 21 distinct reachable commits.

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_EGSET12_CONTAMINATION_AUDIT_RESULT.md`
commit `a4fc980a51a151332625acd7e8a69154589d6a2a`.

Controlled audit run `34760898067`, job `103733427004`; reachable commits `7662`; match lines `42`; unique matching pre-search commits `21`; artifact ID `10318981287`; artifact ZIP SHA-256 `858da60e05998cacbee0a78cb566533403859c9fa632789240b190f50bf31301`.

Disposition: **do not download/score EGSet12 for V6 admission, do not rewrite history to restore untouched status, and do not create a V6 binding for it.**

### GUITAR-FX-DIST / IDMT-SMT-Audio-Effects — REJECTED ON RIGHTS

GUITAR-FX-DIST derives its source recordings from IDMT-SMT-Audio-Effects. Fraunhofer's official dataset terms provide that corpus for evaluation under **CC BY-NC-ND 4.0**. That is not a defensible permissive basis for the V6 product-validation holdout.

Disposition: **do not download/audit/score GUITAR-FX-DIST or IDMT-SMT-Audio-Effects for V6 admission.**

### EG-Solo — REJECTED ON RECORDING PROVENANCE

Public metadata describes 76 clips / 6,833 annotated notes, but the audio comes from professional electric-guitar demonstration videos on YouTube, including popular-song solos with backing tracks. Note annotations do not grant rights to the underlying third-party recordings.

Disposition: **do not download/audit/score EG-Solo for V6 admission.**

### EG-IPT — METADATA-ONLY LEAD, NOT AUDIT-READY

Zenodo record `15205644` describes 52,320 monophonic real electric-guitar files totaling 28 h 22 m 56 s, 96 kHz/24-bit, across 19 playing techniques, with six simultaneous capture paths including DI and three pickup configurations. Archive metadata reports `EG-IPT.zip`, ~23.8 GB, MD5 `48a5135adfd090515ff0af7dc5c3c32f`.

The accompanying public code repository `nbrochec/nime2025` builds technique-class CSVs from file paths/directories and trims silence for classification. Surfaced metadata/code does **not** establish a separate immutable performed note-level pitch/onset reference stream suitable for the frozen V6 matcher. The code repository is GPL-3.0, but that does not establish the audio archive's license.

Disposition: **keep metadata-only; do not download/audit yet.** First resolve dataset-audio license/provenance and whether immutable pitch/onset truth exists independently of model/detector output. Never manufacture onset truth by trimming or onset detection.

### Backup: EGFxSet

Real electric-guitar hardware recordings, stable Zenodo release, CC BY 4.0/open-access description, 8,970 five-second files. Only 690 unique clean performances exist; most material is derived effects variants, and public metadata does not establish high-resolution note-onset timing. It remains a narrow structural backup rather than an audit-ready holdout.

### Metadata lead: GIHME — DATASET STILL UNRESOLVED

Public metadata describes ~10 hours of richly annotated real hexaphonic-guitar improvisations with note/technique/tuning/effect annotations. UMONS/ORBi confirms the 2022 work and links DOI `10.5281/zenodo.6573697`, but surfaced Zenodo records still resolve to conference-paper artifacts rather than a clearly licensed multi-hour corpus package. Dataset package location, license, exact annotation timing representation and immutable audio/reference identities remain unresolved.

Explicit exclusions now include GuitarSet, IDMT-SMT-Guitar, Guitar-TECHS, GAPS, EGSet12, GUITAR-FX-DIST / IDMT-SMT-Audio-Effects, EG-Solo, Slakh/SynthTab and GuitarJam.

## NEXT ALLOWED ACTION

1. Continue metadata/license/structure search for a **different untouched, permissively licensed real-guitar corpus** with performed immutable note-level timing and enough independent event volume to plausibly satisfy the frozen >=1,000 V6-positive gate.
2. Resolve GIHME dataset location/license/annotation representation; do not treat a paper record as the dataset.
3. Resolve EG-IPT dataset-audio license and whether raw metadata exposes pitch plus immutable onset truth; do not derive reference onsets from trimming/detection.
4. Keep EGFxSet as a narrow backup; effect duplicates may not be counted as independent evidence merely to satisfy the volume gate.
5. For any newly surfaced candidate, perform branch-specific contamination/history review before selection; default-branch search is insufficient.
6. Select one replacement only after rights/provenance/untouched status, reference semantics and plausible evidence volume are defensible without duplication/rescue rules.
7. Freeze a corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio/reference pairs.
8. Run only structural/alignment audit first. If unsuitable, reject without correctness. If suitable, bind immutable identities into the already-frozen V6 scoring framework, build controlled no-real-correctness harness CI, then launch exactly one ordinary-GitHub-CPU official correctness run after prerequisites are green.
9. Ask the user only if Modal, Vercel heavy-GPU or L4 execution becomes necessary.

## STILL FORBIDDEN

- any Guitar-TECHS V6 correctness
- post-hoc repair/exclusion of Guitar-TECHS anomalies to rescue the holdout
- any GAPS audit/correctness under current explicit non-commercial/copyright-material terms absent written permission
- EGSet12 V6 admission scoring/binding or history rewriting to restore untouched status
- GUITAR-FX-DIST / IDMT-SMT-Audio-Effects V6 admission use under CC BY-NC-ND terms
- EG-Solo V6 admission use from third-party YouTube/professional-song recordings
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

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. Guitar-TECHS is closed with outcome C and no V6 correctness. GAPS and GUITAR-FX-DIST/IDMT-SMT-Audio-Effects are rejected on rights; EGSet12 is rejected as branch-history contaminated; EG-Solo is rejected on third-party recording provenance. EG-IPT is a new metadata-only lead with substantial real DI audio but unresolved dataset-audio license and no yet-established immutable note-level pitch/onset truth. GIHME remains scientifically promising but its actual corpus package/license is unresolved. EGFxSet remains a narrow backup. V6 method/scoring framework remain frozen and no replacement-holdout V6 correctness has been exposed. Do not audit real candidate media until rights, untouched status, reference semantics and a corpus-specific reference-blind preregistration are frozen.
