# Songsterr Fresh V6 — Recent Repository Replacement Sweep

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: metadata-only screening; **no candidate media downloaded, no Basic Pitch/V6 execution, no correctness exposure**

## Scope

This is a continuation of the replacement untouched-holdout search under the already-frozen V6 method/scoring framework. Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research and protected-song execution remain closed.

A replacement still must establish before media access: explicit usable dataset-audio rights, real guitar, immutable independent performed note-level onset+pitch truth, plausible >=1,000 V6-positive evidence volume without duplicate inflation, and defensible untouched status.

## Sources checked

- Hugging Face guitar-tag dataset index: https://huggingface.co/datasets?other=guitar
- GuitarJam: https://huggingface.co/datasets/Julian-br/GuitarJam
- Isolated Guitar Chords: https://huggingface.co/datasets/severyn-k/isolated-guitar-chords
- duplicate Isolated Guitar Chords release: https://huggingface.co/datasets/rodriler/isolated-guitar-chords
- Guitar Single-Note Recordings / guitar-fretboard-notes: https://huggingface.co/datasets/collegefishiesd/guitar-fretboard-notes
- Semantic Timbre Dataset: https://huggingface.co/datasets/JoeCameron1/SemanticTimbreDataset
- guitar-chord-mix: https://huggingface.co/datasets/ryangowe/guitar-chord-mix

## GuitarJam — RIGHTS CLEAN / REFERENCE ABSENT

The dataset card reports approximately 2.5 hours of clean monophonic electric-guitar improvisations, 580 ~15-second clips, Fender Stratocaster -> Focusrite Scarlett Solo -> Audacity DI, WAV 44.1 kHz/16-bit, and CC0-1.0 metadata.

However, the public dataset schema/card exposes audio with null labels and documents no independent note-event annotations, MIDI stream, string/fret sequence, performed onset timestamps, or performed pitch truth.

**Disposition: reject before media access for V6 admission.** Clean DI and permissive rights are insufficient without immutable independent performed note-level onset+pitch truth. Do not create truth with Basic Pitch, pitch tracking, onset detection, transcription, manual listening, or score reconstruction.

## Isolated Guitar Chords — CHORD LABELS ONLY

The current dataset card reports manually recorded acoustic guitar, CC BY 4.0, 25 training + 6 test recordings per chord class, and class-directory labels such as `A`, `Am`, etc. The duplicate `rodriler` release explicitly identifies itself as a duplicate of the same source.

The authoritative public metadata is for audio classification/chord recognition and exposes chord-class labels, not immutable performed per-string/per-note onset+pitch events. Slow string-by-string and repeated-strum protocols make a single nominal chord label especially unsuitable as an onset reference.

**Disposition: reject before media access.** Do not infer note events from chord theory/fingering, strum protocol, energy thresholds, or the audio. The duplicate release is not independent evidence.

## Guitar Single-Note Recordings (`guitar-fretboard-notes`) — TOO SMALL + NO PERFORMED ONSET TRUTH

The 2026 dataset card reports 390 real single-note guitar recordings across six strings and frets 0-12 from two players, including acoustic and electric sources. Filename-derived metadata provides string, fret, note name, MIDI number and nominal frequency. License metadata is CC BY-SA 4.0.

Two frozen gates fail before media access:

1. **Evidence volume:** there are only 390 total recordings / nominal note events. Even the impossible best case of one V6-positive event per recording cannot reach the frozen >=1,000 V6-positive admission minimum.
2. **Reference timing:** metadata derives pitch/string/fret identity from filenames but provides no independent performed onset timestamp for the note inside each recording. Recording duration/start is not a contemporaneous performed-onset reference, and onset detection from the evaluated audio is forbidden as truth construction.

**Disposition: reject before media access for V6 admission.** It may be useful for unrelated pitch-classification research, but not for this frozen external admission experiment.

## Semantic Timbre Dataset — DERIVATIVE OF EGFxSet

The dataset card states that its original clean 690 Fender Stratocaster monophonic recordings come from EGFxSet, then expands them through Guitar Rig Pro 7 pedal/effect parameter settings to 275,310 files.

**Disposition: reject as a new untouched replacement holdout.** The underlying unique real performances are the already-screened EGFxSet source population; effect renders are not new independent performances and cannot inflate evidence volume. EGFxSet remains only the previously recorded narrow backup, with its existing reference limitations unchanged.

## `guitar-chord-mix` — DERIVED MIXTURE, NOT INDEPENDENT HOLDOUT

Its dataset card explicitly lists GuitarSet, Guitar-TECHS, EGFxSet, Isolated Guitar Chords, synthetic SFZ instruments and noise as source material, and generates/normalizes JAMS annotations across those sources.

**Disposition: reject as an external untouched replacement.** It repackages already revealed/closed or otherwise ineligible populations and adds synthetic/derived material. Derived JAMS cannot make an exposed source corpus untouched, and effect/synthetic variants cannot count as independent external evidence.

## Search-frontier result

The current recent public guitar-tag repository sweep has not produced an audit-ready replacement. The newly surfaced clean-rights datasets fail on reference semantics or evidence volume, while large derived datasets fail independence/untouched provenance.

This is not a claim that no qualifying corpus exists. Continue metadata-only discovery, especially primary research releases outside generic dataset indexes, and re-check authoritative rights/reference updates for scientifically strong blocked candidates such as AG-PT-set.

## Authority unchanged

No corpus is selected. No media was downloaded or inspected. No structural/alignment audit, Basic Pitch run, V6 run, correctness computation, optimizer/threshold sweep, frozen-rule change, or production promotion is authorized by this checkpoint.

Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
