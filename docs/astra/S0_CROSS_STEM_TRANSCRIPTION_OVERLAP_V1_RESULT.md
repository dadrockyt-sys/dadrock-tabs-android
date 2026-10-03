# Cross-Stem Transcription Overlap / Role Ambiguity Diagnostic V1 — Result

Date: 2026-10-02  
Branch: `astra-work`

## Purpose

Test whether two untouched raw separator outputs that represent the same underlying musical source can be identified from overlap between their independently transcribed note-event streams.

The same frozen Basic Pitch 0.4.0 TFLite front end was used on the raw guitar and bass BS-Roformer outputs.

Measured:
- exact-MIDI onset overlap at 50 ms;
- pitch-class onset overlap at 50 ms;
- octave-related onset overlap at 50 ms;
- any-pitch onset coincidence at 50 ms;
- guitar/bass event-density balance.

No overlap cutoff was selected and no audio was changed.

## Runtime correction

Initial run `37091545955` failed because co-installing TensorFlow for YAMNet caused Basic Pitch to switch its default backend from the previously frozen TFLite file to a TensorFlow SavedModel directory.

That backend change was rejected.

The final workflow isolates Basic Pitch on the exact frozen TFLite model and reads prior frozen duplicate-class context from:
`docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json`.

Intermediate run `37091775151` still used the older TensorFlow-containing workflow and failed for the same identity reason. It is not scientific evidence.

## Successful GitHub Actions evidence

Run: `37091792312` — **success**  
Head commit: `75b4bfb8b36f56e726aca7b32d05ce047c93f1d1`

Artifact:
- id: `11263730676`
- digest: `sha256:7cc5b69125dbc042c219a63fa73c4627a359bca7ed9b20591c0f6ecb0a795ed5`

Prior frozen pair context:
- duplicate candidate count: **1**
- key fixture: **S0M10**
- reported state: `duplicate_bass_candidate`

## S0M10 versus ordinary both-present guitar+bass mixtures

### Exact-MIDI onset overlap

S0M10 symmetric F1: **0.0303**

Ordinary:
- mean: 0.0202
- median: 0.0000
- max: 0.0851

S0M10 rank: **4th of 9**  
z versus ordinary: **+0.34**

Conclusion: exact-MIDI overlap does **not** isolate S0M10.

### Pitch-class onset overlap

S0M10 symmetric F1: **0.0909**

Ordinary:
- mean: 0.0520
- median: 0.0459
- max: 0.1176

S0M10 rank: **2nd of 9**  
z versus ordinary: **+1.12**

S0M01 was higher at 0.1176.

Conclusion: pitch-class overlap is elevated but not unique.

### Octave-related onset overlap

S0M10 symmetric F1: **0.0606**

Ordinary:
- mean: 0.0358
- median: 0.0305
- max: 0.1176

S0M10 rank: **2nd of 9**  
z versus ordinary: **+0.66**

S0M01 was again higher.

Conclusion: octave overlap does not uniquely identify the duplicate-role case.

### Any-pitch onset coincidence

S0M10 symmetric F1: **0.0909**

Ordinary:
- mean: 0.1836
- median: 0.1878
- max: 0.3529

S0M10 rank: **7th of 9**  
z versus ordinary: **-0.86**

The duplicate-role fixture actually had *less* generic onset coincidence than many ordinary mixtures.

### Event-density balance

S0M10:
- guitar events: **33**
- bass events: **33**
- event density: **4.48/s** for each
- min/max density ratio: **1.000**
- absolute density difference: **0**

Ordinary both-present mixtures:
- mean density-balance ratio: **0.296**
- median: **0.242**
- max: **0.654**

S0M10 rank: **1st of 9**  
z versus ordinary: **+3.14**

This is the only strongly isolated cross-stem transcription feature in V1.

## Interpretation

The original hypothesis that a duplicate-role pair would show unusually high *same-note* overlap is not supported by this S0 result.

S0M10 does show unusually symmetric transcription **quantity**, but its independently decoded note identities do not strongly match. This is compatible with the separator distributing related source information differently enough that Basic Pitch decodes different harmonics/octaves/events in the two outputs.

Event-count symmetry alone is not specific enough to freeze as an automatic role-ambiguity threshold from one positive fixture.

## Decision

**Do not preregister an automatic cross-stem overlap gate from V1.**

Keep:
- pair classifier frozen;
- duplicate-class evidence diagnostic only;
- transcription reliability diagnostic only;
- raw separator outputs unchanged.

Do not:
- choose an event-density threshold from S0;
- merge/mute/reassign/suppress stems;
- tune Basic Pitch;
- deploy a role decision to production.

The next project direction should be **explicit uncertainty presentation**: preserve the transcription evidence but mark cases with known diagnostic concerns rather than silently correcting them.

A future uncertainty contract should expose reason codes and provenance, distinguish normal evidence from role ambiguity / missing-stem / unresolved transcription conditions, and fail closed for automatic tab confidence. It must not imply that uncertain notes are wrong, nor select a hidden correction.
