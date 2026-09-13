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

Immutable result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`
commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.

Artifact facts:
- artifact ID `10317695640`
- ZIP SHA-256 `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`
- 9 verified packages
- 104 paired DI/MIDI performances
- 18,934 paired reference events
- 0 unpaired DI / 0 unpaired MIDI
- all 104 alignment statuses `OK`
- pairing manifest `24ff1b4eef07f28eb678f38fbec80f8cc26668329812868a89992e20eb73efa7`
- lag manifest `95b244d78014e20ea0f468ecf88aacf90e8442f4aef675b246845202d98fcc84`
- proposed population `bd239d63ba39a370f7c9e09df544b3b207596acf523b09e2be57bbc49cf0b765`
- lag range -8..+10 hops, median -5 hops
- MIDI anomalies: 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs

Frozen decision: `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`.

Basic Pitch was not invoked, V6 was not invoked, correctness was not computed. Guitar-TECHS is closed as the V6 external holdout. Do not score it, repair/drop events to rescue it, or create an A/B binding.

## CURRENT ACTIVE WORK — REPLACEMENT UNTOUCHED HOLDOUT SEARCH

Continue metadata/license/reference-semantic research only until one corpus has explicit permissive dataset-audio rights, real guitar, immutable performed note-level onset+pitch truth independent of evaluated audio, plausible >=1,000-positive evidence volume, and defensible untouched status.

No V6 correctness has been run on any replacement candidate.

### Active research checkpoints

- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_METADATA_SEARCH.md`, commit `64d9516d0efbba380769bd6cc52f93572393180a`.
- `docs/checkpoints/SONGSTERR_FRESH_V6_REPLACEMENT_HOLDOUT_SEARCH_UPDATE_2026-09-13.md`, commit `e8d8080c6944038a48150c9c42711a16cf92da6b`.
- `docs/checkpoints/SONGSTERR_FRESH_AGPTSET_RIGHTS_REVIEW_2026-09-13.md`, commit `5f4b9c6042eba77225eb5f146fdd5c73c3bee5b3`.
- `docs/checkpoints/SONGSTERR_FRESH_MULTIMODAL_ELECTRIC_GUITAR_METADATA_REVIEW_2026-09-13.md`, commit `1f64818fa63327ca17c23586cc79017c74b83446`.
- `docs/checkpoints/SONGSTERR_FRESH_GIHME_METADATA_RELEASE_REVIEW_2026-09-13.md`, commit `1c440f0e9a4e8281c49cf90877e786b5c2c9d9cd`.
- `docs/checkpoints/SONGSTERR_FRESH_MMIP_METADATA_RIGHTS_REVIEW_2026-09-13.md`, commit `dd44674afa5b1d394cf760a192bbb1a2cae67b83`.
- `docs/checkpoints/SONGSTERR_FRESH_EGDB_METADATA_RIGHTS_REFERENCE_REVIEW_2026-09-13.md`, commit `a15aef9df3f90d7076cc71d5ae470c9fb1fc7db0`.

### AG-PT-set — SCIENTIFICALLY STRONG / RIGHTS BLOCKED

Zenodo record `10159492`, ~6.7 GB, ~15 h 55 m audio, with 32,592 musician-annotated millisecond-level onset events and released pitch metadata. Scientifically strong, but the actual data/audio archive has no authoritative permissive data-file license in the surfaced Zenodo rights metadata.

Disposition: do not download/audit unless an authoritative permissive data-file license or explicit rights-holder permission is established. If rights later clear, run branch-specific contamination/history audit before media access.

### GAPS — REJECTED ON EXPLICIT RIGHTS TERMS

Scientifically attractive (~14 h, 300 performances, >200 performers, note-level MIDI), but official terms limit use to non-commercial research and impose permission/distribution restrictions.

Disposition: do not use/download/audit absent explicit written permission that clears this product-validation use.

### EGSet12 — REJECTED AS NOT UNTOUCHED

Controlled full-history audit found 21 distinct pre-search matching commits among 7,662 reachable commits.

Immutable result: `docs/checkpoints/SONGSTERR_FRESH_EGSET12_CONTAMINATION_AUDIT_RESULT.md`, commit `a4fc980a51a151332625acd7e8a69154589d6a2a`.

Disposition: do not download/score/bind and do not rewrite history to restore untouched status.

### GUITAR-FX-DIST / IDMT-SMT-Audio-Effects — REJECTED ON RIGHTS

Source corpus terms are CC BY-NC-ND 4.0.

Disposition: do not download/audit/score for V6 admission.

### EG-Solo — REJECTED ON RECORDING PROVENANCE

Annotations are tied to professional YouTube guitar-demo/popular-song audio whose underlying recording rights are not cleared by annotation metadata.

Disposition: do not download/audit/score for V6 admission.

### G&N / TENT — REJECTED ON SOURCE-RECORDING RIGHTS

Audio comes from a commercial guitar-textbook CD.

Disposition: do not acquire/audit/score for V6 admission.

### EG-IPT — METADATA-ONLY / NOT AUDIT-READY

Zenodo record `15205644`: 52,320 real electric-guitar files, ~28 h 23 m, six simultaneous capture paths including DI. Surfaced materials establish technique labels and silence trimming, not an independent immutable performed onset+pitch stream. Dataset-audio license also remains unresolved.

Disposition: metadata-only; do not download/audit. Never manufacture onset truth by trimming or onset detection.

### Multimodal Electric Guitar Data — RIGHTS CLEANER / REFERENCE INSUFFICIENT

Zenodo family `6470235` / `6470236`, ~32.5 GB, 36 real guitarists, current indexed metadata indicates CC BY 4.0. Public materials establish action classes and multimodal signals, not immutable note-level onset+pitch truth.

Disposition: do not download for V6 admission unless an authoritative released note-level performed onset+pitch reference is established.

### MMIP — REJECTED ON RIGHTS + REFERENCE PROVENANCE

Authoritative license is CC BY-NC-SA 4.0, and guitar MIDI is produced after recording using Ableton audio-to-MIDI conversion rather than independently captured performed truth.

Disposition: do not download/audit/score for V6 admission.

### GIHME — NOT AUDIT-READY / RELEASE NEVER MATERIALIZED

Paper describes ~10 h of hexaphonic guitar improvisations and annotations, but the official repository remains a two-commit placeholder with no completed corpus, annotation package, checksums, or dataset license.

Disposition: do not reconstruct or score from demos/videos/detector output. Reconsider only if an authoritative completed release appears.

### EGFxSet — NARROW BACKUP ONLY

Real electric-guitar hardware recordings with CC BY 4.0 signal, but only ~690 unique clean performances under the effect-expanded set and no established high-resolution performed onset reference.

Disposition: not audit-ready; effect duplicates cannot be counted as independent evidence merely to meet volume.

### EGDB / EGDB-PG — REJECTED / NOT AUDIT-READY BEFORE MEDIA ACCESS

Immutable review:
`docs/checkpoints/SONGSTERR_FRESH_EGDB_METADATA_RIGHTS_REFERENCE_REVIEW_2026-09-13.md`
commit `a15aef9df3f90d7076cc71d5ae470c9fb1fc7db0`.

Scientific facts from the original EGDB paper:
- real Stratocaster-type electric guitar with hexaphonic pickup;
- clean DI captured while a professional guitarist performed 240 tablatures against click tracks;
- 118 minutes of unique real DI performance, subsequently re-rendered through multiple amplifier/timbre paths.

Two independent gates fail:
1. authoritative permissive dataset-audio rights are not established. The original project publicly links data but surfaces no dataset license; the newer EGDB-PG Zenodo record family also exposes a blank Rights/License field.
2. reference onset timing is not independently captured performed truth. The paper says expected onsets come from tabs/BPM, an onset detector is run on each recorded DI string signal to estimate actual onsets, pitches are assigned from the closest expected tab onset, and the resulting annotations are manually checked/corrected. Thus onset truth is materially derived from the evaluated audio family rather than a contemporaneous independent MIDI/note-capture stream.

Disposition: do not download/audit/bind/score EGDB or EGDB-PG for V6 admission. Author permission could resolve rights but would not alone resolve reference provenance. Reconsider only if an authoritative independently captured performed onset+pitch reference exists, then run untouched-history screening before media access.

## NEXT ALLOWED ACTION

1. Continue metadata-only search for a replacement corpus satisfying all rights/reference/volume/untouched gates.
2. Continue resolving EG-IPT only at metadata/license/reference level.
3. AG-PT-set may advance only if its data-file rights become authoritative and permissive.
4. Multimodal Electric Guitar Data may advance only if a released performed note-level onset+pitch reference is established.
5. Keep EGFxSet as a narrow backup; do not count effect variants as independent evidence.
6. Select a replacement only after rights, provenance, untouched status, reference semantics and plausible evidence volume are defensible without duplication or rescue rules.
7. Before any selected corpus media access, freeze a corpus-specific reference-blind inventory/alignment preregistration.
8. Run structural/alignment audit first. If unsuitable, reject without correctness. If suitable, bind immutable identities into the already-frozen V6 scoring framework, build controlled no-real-correctness harness CI, and only then launch exactly one ordinary-GitHub-CPU official correctness run.
9. Ask the user only if Modal, Vercel heavy-GPU or L4 execution becomes necessary.

## STILL FORBIDDEN

- any Guitar-TECHS V6 correctness or post-hoc anomaly repair/exclusion
- downloading/auditing AG-PT-set without authoritative permissive data-file rights
- GAPS V6 use absent written permission clearing current restrictions
- EGSet12 V6 scoring/binding/history rewriting
- GUITAR-FX-DIST / IDMT-SMT-Audio-Effects use under current CC BY-NC-ND terms
- EG-Solo use from third-party YouTube/professional-song recordings
- G&N/TENT use from commercial textbook-CD recordings
- MMIP use under CC BY-NC-SA terms or with Ableton-derived guitar MIDI as truth
- reconstructing/scoring GIHME from demos/videos/detector output
- EGDB/EGDB-PG media access or V6 use under current missing-rights and audio-derived-onset-reference evidence
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

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. Guitar-TECHS is closed with outcome C and no V6 correctness. The active task is metadata-only replacement holdout search. AG-PT-set is scientifically strong but blocked on data-file rights; EG-IPT remains unresolved metadata-only; Multimodal Electric Guitar Data has cleaner rights but lacks established note-level performed truth; EGFxSet is only a narrow backup. GAPS, EGSet12, GUITAR-FX-DIST/IDMT-SMT-Audio-Effects, EG-Solo, G&N/TENT, MMIP, GIHME and EGDB/EGDB-PG are not usable under current evidence. Do not download a candidate until rights/reference/untouched/volume gates are defensible and a corpus-specific reference-blind audit preregistration is frozen. V6 method/scoring framework remain frozen and no replacement-holdout V6 correctness has been exposed.