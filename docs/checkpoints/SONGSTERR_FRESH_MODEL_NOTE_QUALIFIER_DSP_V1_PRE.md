# Songsterr Fresh — Independent Model-Note DSP Qualifier V1 Pre-Execution Freeze

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `IMPLEMENTATION_FROZEN_NO_REAL_MEDIA_EXECUTION`

## Purpose

Implement the independent qualification producer required by `SONGSTERR_FRESH_MODEL_NOTE_QUALIFICATION_V1_PRE.md` without choosing thresholds from the observed EGFxSet Basic Pitch output.

This checkpoint freezes implementation semantics before any real-audio use. It does not authorize another EGFxSet/Basic Pitch run and does not change the historical repaired-smoke result.

## Algorithm lineage — exact existing synthetic V6 constants

The qualifier reuses the already-existing pure DSP classification function in:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`

No V6 DSP threshold is retuned from the EGFxSet result. The inherited constants remain exactly:

- analysis sample rate: `44100 Hz`
- frame samples: `2048`
- hop samples: `256`
- FFT size: `8192`
- frame end offsets: `-1536,-1280,-1024,-768,-512,-256,0,256,512,768,1024,1280,1536` samples
- post-onset comparison maximum: `1024` samples
- playable MIDI range: `40..88`
- maximum harmonic count: `6`
- minimum analysis RMS: `1e-5`
- minimum innovation energy: `1e-6`
- fundamental-to-maximum-harmonic onset-innovation ratio minimum: `0.20`
- selected-template necessity fraction minimum: `0.01`

The inherited classifier uses onset-synchronous complex spectral prediction deviation, pre/post innovation, harmonic templates, non-negative least squares, and a leave-selected-candidate-out residual test. A candidate is corroborated only when its selected coefficient is positive and its necessity fraction is at least `0.01`.

## Frozen real-pipeline wrapper behavior

1. Input is an audio WAV plus the immutable Basic Pitch primary JSON.
2. The wrapper never calls Basic Pitch or any other model.
3. The wrapper never reads Basic Pitch candidate confidence for its decision.
4. Audio channels are deterministically averaged to mono.
5. Integer PCM is deterministically normalized by dtype range; finite floating PCM is accepted directly.
6. If source sample rate differs from `44100`, deterministic `scipy.signal.resample_poly` conversion is used and recorded.
7. For an event whose required V6 pre-context would begin before sample zero, the wrapper prepends only the exact number of zero samples needed to supply the frozen pre-context and shifts that event's analysis index by the same amount. This is a general clip-boundary rule, not a MIDI-specific rule.
8. No right-edge zero padding is permitted. If required post-context lies beyond available audio, classification remains insufficient.
9. Per-proposal mapping is:
   - V6 `onset-birth-corroborated-candidate` -> qualification `corroborated`;
   - V6 `not-onset-birth-corroborated` -> qualification `rejected`;
   - V6 `insufficient-evidence` normally -> qualification `insufficient`;
   - **specific no-birth exception:** V6 reason `INSUFFICIENT_LOW_ONSET_INNOVATION` -> qualification `rejected`, because reaching that reason already proves the required pre/post context exists and `analysisRms >= 1e-5`, while onset innovation is below the already-frozen `1e-6` floor. For a proposal explicitly claiming a new note birth, adequate audio plus essentially no onset innovation is negative birth evidence rather than an unknown state.
10. The no-birth exception changes no numeric threshold and applies identically to every MIDI/event. Missing context, low audio support, missing feature bins, NNLS failure, non-finite fit, or other genuinely incomplete evidence remains `insufficient`.
11. Every model proposal is preserved one-for-one by exact `noteId`, MIDI and start time.
12. Output declares `candidateConfidenceUsedForDecision:false` and `independentOfBasicPitchCandidateConfidence:true`.
13. Reference tabs, Songsterr truth, desired MIDI values and physical string/fret labels are not inputs.
14. Qualification confidence is diagnostic only and does not own the status decision. The inherited V6 classifier result plus the frozen no-birth mapping owns the status.
15. The first validation of this wrapper is synthetic/code-only. No real EGFxSet audio is processed under this checkpoint.

## Why `LOW_ONSET_INNOVATION` is resolved negative evidence

The qualifier's question is not "is there enough evidence to estimate a pitch from scratch?" It is narrower: "does this already-proposed MIDI correspond to a new note birth at this time?" The V6 DSP only emits `INSUFFICIENT_LOW_ONSET_INNOVATION` after successfully obtaining finite full pre/post frames and passing the minimum-audio-RMS gate. Under that narrower qualification question, an innovation norm below the frozen minimum is direct evidence that no new spectral birth was detected. Treating it as unresolved would allow sustained-harmonic model proposals to block an otherwise resolved transcription indefinitely.

This semantic mapping is frozen before any real-audio execution and is not conditioned on a MIDI value, model confidence, expected answer, reference tab, or string/fret label.

## Boundaries

- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free.
- DSP remains under `scripts/songsterr-fresh/`.
- No V143/Gomyway or other closed/reserved line is used.
- No customer eligibility, correctness, V6 validation, or delivery authority is created.
- Global authorization fields remain false/zero.

A later real-audio validation requires a separately frozen execution checkpoint and explicit user authorization. That validation must use the already-frozen qualifier unchanged; no threshold adjustment may occur after observing its result.
