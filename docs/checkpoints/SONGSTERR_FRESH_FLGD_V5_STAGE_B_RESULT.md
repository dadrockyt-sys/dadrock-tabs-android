# Songsterr Fresh — FLGD V5 Stage B Result

Status: **IMMUTABLE NON-SCORING POPULATION / ANNOTATION RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Execution

Amended official Stage B entrypoint:
- `scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest_amended.py`
- pairing adapter implementation commit `26f38648634a1138da492e86e29af8084c705158`
- pairing amendment CI run `34719672583`, job `103623078740`: SUCCESS.

One amended real Stage B run:
- workflow `.github/workflows/songsterr-fresh-flgd-v5-real-stage-b-attempt2.yml`
- source commit `ac57c6c5379f00ad97c292415efec90c9ed32860`
- run `34719744595`
- job `103623274603`
- result: SUCCESS.

No Basic Pitch, V5 classification, estimate/reference matching or correctness metric was executed.

## Immutable report identities

- Stage B JSON SHA-256: `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256: `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256: `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256: `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- bound MIDI-edge audit report SHA-256: `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`
- uploaded report-only artifact ID: `10305323053`
- artifact ZIP digest: `138ce6006e7391d65729be0d83758d6f033156336938c985e55142f91d96aa18`.

## Frozen population

All 79 root `metadata.csv` rows are included. No post-hoc exclusions.

Metadata strata:
- split: train `62`, validate `8`, test `9`
- guitar type: nylon `40`, electric `35`, acoustic `3`, electric-band `1`.

Canonical media/reference membership remains one metadata-named `audio/` MP3 + one canonical `midi/` + one syncpoint JSON per performance. `test_set/` duplicates/model outputs remain forbidden as reference truth.

## Reference annotation structure

- included performances: `79`
- reference note events: `76,392`
- MIDI format: format 1 for all 79
- track count: 2 for all 79
- PPQ: 220 for all 79
- tempo domain: 500,000 microseconds/quarter only
- channel domain: channel 0 only
- same-key overlap count: `0`
- ignored audited duplicate releases: exactly `24`
- MIDI pitch range: `38..88`
- onset range: `0.03409090909090909 .. 408.5068181818182` s
- offset range: `0.33636363636363636 .. 413.84090909090907` s
- annotation-duration range: `0.004545454545450411 .. 14.513636363636351` s.

Syncpoint structural arities:
- arity 2 points: `1,832`
- arity 3 points: `20,543`.

Annotation duration statistics are diagnostics only and do not change release/duration authority.

## Policy boundary

The Stage B result has exactly:
- `basicPitchInvoked:false`
- `v5ClassifierInvoked:false`
- `demucsInvoked:false`
- `audioSamplesUsedForPitchAnalysis:false`
- `estimateReferenceMatchingPerformed:false`
- `correctnessMetricComputed:false`
- `protectedSongUsed:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`.

## Consequence

FLGD Stage B is complete. The holdout correctness outcome remains unseen.

The next required step is a separate final scoring preregistration, frozen before any Basic Pitch/V5 correctness execution. It must bind this exact Stage B population/report and freeze audio decoding, Basic Pitch runtime/settings, V5 implementation/runtime, matching, uncertainty, minimum sample/positive requirements, pooled/stratum gates, provenance and one-off execution semantics.
