# Songsterr Fresh V6 — AG-PT-set pre-media clearance

Date: 2026-09-15 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata / license / annotation-provenance screening only

## Frozen ingress rule

A V6 replacement holdout may advance beyond metadata-only screening only when public evidence establishes, before candidate media is opened:

1. real guitar performance;
2. usable public licensing for this project;
3. pre-existing synchronized note events aligned to the exact performance;
4. reference provenance sufficiently independent for frozen V6 scoring — do not manufacture, infer, transcribe, or derive the scoring reference using the system under test or a materially circular procedure.

This audit does **not** itself authorize Basic Pitch, V6 correctness execution, EGFxSet reruns, threshold changes, or any other real-media/model run.

## Candidate

AG-PT-set — Acoustic Guitar Playing Technique dataset

Primary dataset record:
- https://zenodo.org/records/10159492
- DOI: `10.5281/zenodo.10159492`

Primary methodology paper:
- Domenico Stefani, Gregorio Andrea Giudici, Luca Turchet (2024), *On the Importance of Temporally Precise Onset Annotations for Real-Time Music Information Retrieval: Findings from the AG-PT-set Dataset*
- https://doi.org/10.1145/3678299.3678325

Accompanying repository:
- https://github.com/CIMIL/AG-PT-set_AM24_accompanying-material

## Gate 1 — real guitar performance

**PASS.**

Public metadata establishes real acoustic/electro-acoustic steel-string guitar recordings performed by multiple human guitarists on multiple physical guitars. The labeled portion contains individual monophonic guitar notes recorded through the guitars' internal transducers.

Published dataset summary:
- 15 h 55 min total recordings;
- 10 h 04 min labeled portion;
- 32,592 labeled individual notes;
- 12 playing techniques total, 8 onset-labeled;
- multiple players and multiple acoustic steel-string guitars;
- 48 kHz / 24-bit WAV in the published methodology.

## Gate 2 — usable public licensing

**PASS.**

The Zenodo dataset record was inspected directly on 2026-09-15. It reports:
- access: **Open Access**;
- dataset license: **Creative Commons Attribution 4.0 International (CC BY 4.0 / CC-BY-4.0)**.

The archive itself was **not** clicked or downloaded during this audit.

CC BY 4.0 is a usable public license for reuse subject to attribution and the license terms. This gate relies on the dataset record's rights metadata, not on the publication's separate copyright/license terms.

## Gate 3 — synchronized note-event reference aligned to exact performance

**PASS.**

The published methodology establishes that:
- audio and annotations are released together;
- each note reference is tied to an `audio_file_path`;
- `note_labels.csv` includes `onset_label_seconds` and `onset_label_samples`;
- the same note row includes `pitch_midi` identified as ground-truth pitch;
- the same note row includes `string_number`;
- per-audio-file onset and pitch label files are also provided;
- onsets were aligned at millisecond resolution to the recorded signal.

This is materially stronger than a corpus that has only clip-level pitch classes or only unsynchronized score/MIDI metadata.

## Gate 4 — independent reference provenance

**PASS for pre-media admission.**

The pitch identity is not created by the Songsterr system under test. The recording protocol prospectively prescribed the note content: pitched techniques were recorded as individual notes across specified strings/frets, with repeated performances. The paper states that the number, pitch, and sequence of notes in each file were already known and were used to detect annotation mistakes.

Onset timing was produced independently of the Songsterr pipeline by five musician annotators. Candidate onsets from `aubioonset` were used only to seed the annotation projects; annotators were instructed to add missed onsets, remove false positives, and manually align each retained label to the real onset using high-resolution waveform/spectrogram views. Known note number/pitch/sequence, with a pitch detector only as an aid for finding mistakes, was then used to correct annotation errors.

Therefore the final reference is pre-existing human-validated ground truth aligned to the exact recorded performances, not Basic Pitch/V6 output and not a reference manufactured from the candidate by the system being scored.

Important limitation: this clearance does **not** claim that every onset is infallible; it establishes that provenance is sufficiently independent for the frozen ingress gate.

## Pre-media decision

**PASS_PREMEDIA — AG-PT-set clears all four frozen metadata/license/alignment/provenance gates.**

This makes AG-PT-set the first candidate in the current replacement-holdout search to advance beyond pre-media rejection.

However, this checkpoint is only a clearance to consider a prospective, explicitly authorized media audit. It is **not** authorization to download/open candidate audio or annotation payloads, run Basic Pitch, run V6 correctness, alter thresholds, or score the candidate.

## Safety / authorization record

- AG-PT-set dataset archive clicked: **0**
- AG-PT-set media downloaded/opened: **0**
- AG-PT-set annotation payload downloaded/opened: **0**
- Basic Pitch runs: **0**
- V6 correctness runs: **0**
- EGFxSet runs: **0**
- frozen method/scoring changes: **0**
- V143/Gomyway activity: **0**

## Next safe step

Before any AG-PT-set media access, create a prospective one-shot candidate-selection/execution PRE that freezes:

- exactly which untouched labeled pitched-technique file/note will be selected and by what metadata-only rule;
- exact reference fields to be consumed (`audio_file_path`, onset, `pitch_midi`, `string_number` and any derived physical position rule if required);
- expected sample-rate handling without learning from the candidate result;
- immutable V6 scoring and promotion logic;
- no tuning, rerun, threshold variation, candidate substitution, or reference regeneration after media access;
- explicit user authorization for the real-media/model action if such action is requested.

Until that PRE and authorization exist, keep AG-PT-set media untouched.
