# Unified Guitar/Bass Audio Recognition Set V1

Date: 2026-10-02
Branch: `astra-work`
Status: **CATALOG MERGED / EXECUTION DISABLED**

## Goal

Combine the preserved guitar, bass and non-guitar uploads into one instrument-recognition fixture set before transcription/tab generation.

This layer asks a narrower first question:

**What instrument class is present?**

Primary V1 labels:
- `guitar`
- `bass`
- `other`

Do not conflate this with note transcription, source separation, or tablature generation.

## Source catalogs

- Guitar + controls: `docs/astra/PIXABAY_GUITAR_AUDIO_CATALOG_V1.md`
- Bass: `docs/astra/PIXABAY_BASS_AUDIO_CATALOG_V1.md`

## Combined inventory summary

- 24 guitar-positive files
- 30 bass-candidate files
- 6 non-guitar controls
- **60 total files**
- Guitar duration: **244.110 s**
- Bass duration: **340.805 s**
- Other/control duration: **41.450 s**
- Combined duration: **626.365 s (10 min 26.4 s)**

Audio binaries remain outside Git. Exact SHA-256 hashes stay in the source catalogs.

## Label policy

### Guitar
Use `guitar` only for the 24 G-series files already cataloged as guitar.

Coverage includes:
- acoustic chord
- clean electric
- distorted/metal
- 8-string / low-register
- baritone
- strumming
- tapping
- slide
- bends
- riffs
- loops
- alternate tuning

### Bass
Use `bass` for the B-series pool only where the provenance/classification review supports physical or probable physical bass.

Keep uncertain bass assets out of scored recognition until manually verified.

Current uncertain holdouts:
- B03 — Simple Bass
- B30 — riff dom Cm / bass-heavy electronic candidate

### Other
Use `other` for:
- drums
- speech
- keyboard typing
- crowd cheer
- applause

These are negative controls. They must not be counted as guitar or bass failures unless the recognizer predicts a stringed-instrument class for them.

## Recognition task design

### Stage R1 — coarse instrument presence
Classes:
- guitar
- bass
- other

This is the recommended first recognition task.

### Stage R2 — guitar/bass subtype, only after R1 is credible
Potential guitar sublabels:
- acoustic
- clean electric
- distorted/heavy
- extended-range/baritone
- articulation-specific: tapping/slide/bend/strum

Potential bass sublabels:
- fingerstyle/ordinary
- picked
- slap
- distorted/heavy
- fretless
- sustained/single-note diagnostic

Do not require subtype classification for the first pass.

## Split policy

Because several files may come from the same contributor or closely related recording series, random file-level train/test splitting would leak style/performer/source identity.

For any learned classifier:
- group by contributor/source family;
- keep related series on one side of the split;
- hold at least one contributor/source family out of confirmation;
- never train and test on near-duplicate riffs or related note-series from the same contributor;
- B03/B30 stay excluded until class is verified.

For a non-trained recognition benchmark, report results per contributor/source family in addition to pooled counts.

## Metrics for a scored recognition experiment

Only after labels and provenance are frozen:
- per-class precision
- per-class recall
- per-class F1
- macro F1
- balanced accuracy
- confusion matrix
- false guitar rate on `other`
- false bass rate on `other`
- guitar↔bass confusion rate

Because class durations are unequal, report both file-balanced and duration-weighted summaries.

Do not use note-transcription F1 for this recognition layer.

## Recommended progression

1. **R1 recognition:** guitar vs bass vs other.
2. **R2 transcription gate:** route recognized guitar/bass into instrument-appropriate transcription.
3. **R3 note-event evaluation:** pitch/onset/offset metrics against verified annotations.
4. **R4 tablature mapping:** string/fret assignment.
5. **R5 mixed-song pipeline:** separation -> recognition -> transcription -> tablature.

This gives a failure location instead of one opaque end-to-end score.

## Missing classes for a fuller recognition set

The current `other` class is useful but narrow. Before calling this a broad audio recognizer, add rights-cleared examples of:
- vocals
- piano/keyboard music
- drums/percussion beyond one atmospheric sample
- synth
- strings/orchestral
- silence/room tone
- mixed full-band audio
- guitar + bass together
- bass + drums
- guitar + drums

Those should be collected separately and cataloged with hashes/provenance, not synthesized into fake ground truth.

## Current boundary

This merged set is a **recognition fixture pool**, not training data by default.

No classifier training, embedding generation, Basic Pitch inference, separator run, or empirical benchmark is authorized by this merge.

The next preparation step is to create a frozen V1 recognition manifest selecting verified guitar, verified bass and other controls, with contributor-group metadata and a proposed leakage-safe split.
