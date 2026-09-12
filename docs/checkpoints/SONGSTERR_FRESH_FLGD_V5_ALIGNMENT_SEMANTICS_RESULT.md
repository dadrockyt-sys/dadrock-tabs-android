# Songsterr Fresh — FLGD V5 Alignment Semantics Result

Status: **FROZEN NON-SCORING ALIGNMENT DECISION / BEFORE ANY FLGD CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Audit

Preregistration:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_AUDIT.md`

One-shot audit workflow:
`.github/workflows/songsterr-fresh-flgd-v5-alignment-semantics-audit.yml`
source commit `b2343702e60049a0d17c4d132eda1f1dedc6d8cc`
run `34719868249`, job `103623610804`.

The audit inspected only the exact release's text/support files, sample syncpoint structure and canonical MIDI metrical metadata. It did not run Basic Pitch, V5, audio pitch analysis, estimate/reference matching or correctness metrics.

## Evidence

The selected release README describes the corpus as “Audio and aligned MIDI transcriptions for 79 solo guitar performances.”

The exact release's `test_set/dataset-eval.py` is the publisher-provided evaluation support script. It:
- loads ground-truth MIDI with `pretty_midi.PrettyMIDI(ref_path)`;
- constructs reference intervals directly from each MIDI note's `n.start` and `n.end`;
- evaluates those direct MIDI times against estimated MIDI with `mir_eval.transcription.evaluate(..., onset_tolerance=0.05)`;
- contains older/optional syncpoint/downbeat loading code only as commented-out lines;
- does not warp ground-truth note times through syncpoints before evaluation.

The audit also confirmed a canonical example MIDI (`midi/8DC4c.mid`) is format 1, two tracks, PPQ 220, tempo 500,000 us/quarter and 4/4 time signature at tick 0. Stage B established those same structural domains across all 79 canonical MIDIs.

Syncpoint examples contain explicit audio-second plus score-position coordinates. They remain useful alignment/score-position metadata, but the release's own note-transcription evaluation does not use them to transform canonical MIDI note times.

## Frozen alignment decision

**Canonical metadata-named MIDI note times, converted by standard SMF/PrettyMIDI tempo semantics, are the authoritative audio-aligned note-reference times for V5 external validation. No syncpoint time warp is applied to reference note onsets or offsets.**

Syncpoints may remain identity-bound diagnostics only. They must not modify V5, note inclusion, matching tolerances or correctness outcomes.

The final scoring harness must use the exact Stage B canonical reference-event population and standard MIDI time conversion already frozen in the Stage B result.

## Boundary

No FLGD correctness result exists yet. Authority remains:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- protected song unused.
