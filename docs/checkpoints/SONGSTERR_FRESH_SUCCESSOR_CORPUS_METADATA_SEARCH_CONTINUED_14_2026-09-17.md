# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 15

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only

## Frozen boundary

- No successor PRE or model/correctness run is authorized.
- Do not resume archived V143/Gomyway.
- Do not reopen closed/exposed GuitarSet, IDMT, FLGD/François Leduc, GAPS, GOAT, EG-IPT, Guitar-TECHS, AG-PT, EGDB, EGSet12 or other frozen historical lines as “untouched.”
- No successor corpus media or annotation payload may be opened before a candidate clears prospective source/rights/reference/provenance gates and a new PRE is frozen.
- Reference truth must contain deterministic actual-performance note onset plus integer-MIDI pitch tied to the recorded performance and independent of Basic Pitch or any other AMT/pitch-estimation output.

## RWC 2.0 track-level QC

Search 14 established RWC 2.0 as a stable, scrapeable public lead: Zenodo audio plus aligned MIDI in `rwc-music/rwc-annotations`, both under CC BY-NC 4.0, with five guitar-only Jazz tracks (`RWC_J006` through `RWC_J010`).

A public maintainer issue in `rwc-music/rwc-annotations` (`#258`, “Add aligned MIDIs”) contains a track-level problem table and materially changes the prospective subset:

- `RWC_J006`: explicit status/comment says warping improved but **onsets are not matching**. Prospectively exclude J006 from any candidate evaluation subset.
- `RWC_J008`: marked `check` without a specific defect description in the inspected issue text. Treat as unresolved / do not include prospectively unless independently cleared from public metadata.
- `RWC_J007`, `RWC_J009`, `RWC_J010`: not listed in the inspected problem table. They remain the strongest public guitar-only subset, but absence from a problem table is not affirmative proof that every onset is exact.

This narrowing is prospective and based only on published annotation-quality metadata. No correctness score, model output, MIDI payload, audio payload, or post-result tuning was used.

A separate issue (`#257`) includes beat-test failures touching some RWC guitar tracks. Those concern beat/downbeat annotations and must not be conflated with MIDI note-event alignment quality.

Current RWC evaluation-candidate status:

`J007/J009/J010 = STRONGEST_PUBLIC_SCRAPEABLE_GUITAR_ONLY_CANDIDATES / RIGHTS_AND_FILE_IDENTITY_CLEAR / HUMAN_TRANSCRIBED_PITCH_TRUTH / PER_NOTE_ONSET_AUTHORITY_STILL_REQUIRES_FINAL_GATE / FULL_HISTORY_LINEAGE_NOT_YET_PROVEN`

`J006 = PROSPECTIVELY_EXCLUDE_PUBLISHED_ONSET_MISMATCH`

`J008 = HOLD_UNRESOLVED_PUBLIC_QC_CHECK`

No RWC MIDI/audio payload was opened.

## Older manually created RWC guitar ground truth

Older Benetos/Dixon automatic music transcription work used RWC Jazz guitar pieces and reports creating manually aligned ground-truth MIDI for approximately the first 23 seconds in Sonic Visualiser because the older distributed alignment had omissions/timing/duration problems.

This is technically attractive because manual note timing in Sonic Visualiser is much closer to the frozen actual-performance-onset requirement than global DTW warping.

However, no stable public copy of those exact manual ground-truth MIDI files was located in this pass. Public example pages expose some audio/examples but not a qualifying immutable manual-GT package.

Status:

`TECHNICALLY_STRONG_SHORT_MANUAL_GT / PUBLIC_FILE_NOT_LOCATED / NOT_PRE_READY`

No media or annotation payload was opened.

## RWC Instrument Sound 2.0 — useful public source

RWC Instrument Sound was also re-released publicly in 2026:

- Zenodo DOI `10.5281/zenodo.17170844`, version `v1`, published 2026-02-12.
- License: CC BY-NC 4.0.
- Archive `RWC-I.zip`, approximately 14.2 GB, MD5 `fb5789335fe68abdc09929618e9f0403`.
- Includes Classic Guitar, Acoustic Guitar (Steel String), and Electric Guitar families.

Public RWC documentation describes individual instrument sounds generally recorded in ascending semitone order with silent gaps; for stringed instruments, the total range is recorded for each string. Public metadata exposes guitar maker/variation/style/dynamic/pitch-range fields.

This is potentially valuable for isolated-note diagnostics, but the repeated per-string structure means pitch cannot safely be reconstructed from a single naive global ascending-semitone sequence without a verified file/string event-order specification.

Status:

`AUXILIARY_HIGH_VALUE_PUBLIC_REAL_GUITAR_NOTES / STABLE_RIGHTS_AND_ARCHIVE_IDENTITY / EXACT_PER_EVENT_PITCH_ORDER_MAPPING_NOT_YET_PROVEN`

No RWC-I audio payload was opened.

## MINST — committed RWC onset markers

Public repository: `ejhumphrey/minst-dataset`, inspected at commit `5847ac421522a393df77ca2a43acdc326f7d64e8`.

Useful public properties:

- Project is designed around instrument recordings requiring accurate onset detections.
- README describes high-recall initial onset detection followed by visual human verification/correction.
- Annotation GUI permits adding, removing, and moving onset markers; documented temporal resolution is 10 ms.
- README reports **5,618 RWC guitar notes**, including unpitched sounds.
- `data/onsets/rwc/` contains committed per-source onset CSVs as immutable Git blobs.
- RWC instrument normalization maps `flamenco guitar`, `nylon-string guitar`, and `steel-string guitar` to `guitar-acoustic`.

Important limitation discovered from code:

- `scripts/split_audio_to_clips.py` passes the corrected onset time into an `Observation`, but for RWC it does **not** pass a `note_number`/pitch.
- `minst/model.py` therefore leaves the RWC observation pitch unset in this path.
- The generated `models/rwc/fold0/annotations.csv` referenced in the README is not committed at the advertised current repository path.

Therefore MINST does not by itself publish a ready-made authoritative onset+integer-MIDI event table for RWC guitar. It publishes high-value onset material and tooling, but deterministic pitch must come from a separately proven RWC source-event mapping.

Current status:

`AUXILIARY_HIGH_VALUE_PUBLIC_HUMAN_VERIFIABLE/CORRECTABLE_RWC_ONSETS / PITCH_NOT_CARRIED_IN_CURRENT_RWC_SPLIT_PIPELINE / NOT_EVALUATION_TRUTH_YET`

No onset CSV contents were opened.

## MedleyDB auxiliary classification

MedleyDB exposes public guitar stems and human-verified framewise/continuous pitch contours, but its instrument-activation/onset-style boundaries are not authoritative discrete performed-note births. It remains useful for diagnostics or future auxiliary research but not for the frozen correctness truth.

Status:

`AUXILIARY_USEFUL_PUBLIC_GUITAR_F0_STEMS / NOT_EVAL_TRUTH_DUE_NO_DISCRETE_NOTE_BIRTH_INTEGER_MIDI`

No payload was opened.

## Current practical ranking by gate status

Evaluation-grade / near-evaluation leads:

1. **RWC J007/J009/J010** — strongest *public scrapeable* lead; stable licensed audio and aligned human-transcribed MIDI, but exact per-note onset authority and full-history clean provenance still unresolved.
2. **Arty** — strongest documented hand-annotated onset+integer-MIDI semantics; public immutable package/license unresolved.
3. **Older Benetos/Dixon RWC manual ~23 s GT** — technically strong manual timing; qualifying public files not located.
4. **GM Dataset** — potentially acceptable aligned symbolic truth; stable public package/license unresolved.

Auxiliary scrapeable data:

- RWC Instrument Sound guitar recordings + public metadata.
- MINST committed human-verifiable/correctable onset CSVs for RWC instrument recordings.
- MedleyDB guitar f0/stems.
- TapToTab isolated pitch-labelled guitar notes (pitch useful, onset authority insufficient for evaluation).

This ordering is a research-priority classification, not a correctness score or model ranking.

## State after this pass

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Next work

1. Keep searching for another public guitar corpus with human/direct/symbolic note-on/off truth and stable rights so RWC is not accepted merely for lack of alternatives.
2. Search RWC public QC/alignment metadata for affirmative evidence about J007/J009/J010 without opening MIDI payloads.
3. Investigate whether RWC Instrument Sound has an authoritative per-file/per-string note sequence manifest that can pair MINST corrected onsets with integer MIDI without audio pitch estimation.
4. Complete a true full-history provenance audit before any RWC payload access; current/default-branch/commit-message searches are not enough.
5. If a candidate clears all source/rights/reference/provenance gates, freeze a new exact PRE for unchanged `S AND E AND O AND K`, update the canonical checkpoint to that PRE commit, then STOP for fresh post-freeze user authorization.
