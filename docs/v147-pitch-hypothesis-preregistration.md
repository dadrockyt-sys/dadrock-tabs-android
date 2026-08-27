# V147 — Pitch Hypothesis Before Fingering — Preregistration

Status: **FROZEN BEFORE IMPLEMENTATION — aggregation clarification also frozen before code**

Branch: `v143-contextual-prune-lobo`

## Why V147 exists

V146 is closed. Its bounded timing/fingering calibration changed many guitar positions but produced `pitchChanges = 0`; the V145 rhythm decoder preserves each incoming event MIDI and only searches timing/playable string-fret states for that fixed pitch. A further fingering-only sweep therefore cannot test or repair wrong-note inference.

V147 tests one qualitatively different, reference-free hypothesis:

> Before string/fret decoding, can Jimmy conservatively challenge a Basic Pitch event MIDI using harmonic evidence already derived from the source audio?

This is **not** a new transcription model and is **not** a reference-driven correction table. It is a bounded pre-decoder hypothesis layer.

## Isolation / anti-leakage rules

1. V145/V146 calibration references, gold tabs, position-accuracy scores, or reference-derived labels MUST NOT be read or used while constructing or tuning V147.
2. V146 thresholds/results MUST NOT be used to choose V147 pitch decisions, other than the structural observation that V145 emitted zero pitch changes.
3. No Modal, L4/GPU, or live-audio execution is authorized by this preregistration.
4. Phase A is CPU/generated-evidence only. A later live/reference check requires a separate explicit authorization and a checkpointed go/stop decision.
5. No automatic promotion into production decoding.

## Existing signals reused

V147 deliberately reuses two already-existing project boundaries instead of introducing an unrelated detector:

- `analyzer/modal_analyzer.py`: Basic Pitch supplies point note events (`midi`, confidence, start/end) while richer model output is not used to create alternate pitch hypotheses.
- `analyzer/modal_bend_harmonic_evidence_benchmark.py`: the project already computes harmonic/percussive separation and high-resolution CQT harmonic energy (48 bins/octave), including energy in narrow pitch bands.

The V145 decoder remains downstream and unchanged for Phase A.

## Frozen candidate family

For a valid incoming event MIDI `m`, V147 may consider only:

- `m - 1`
- `m`
- `m + 1`

Candidates outside the playable guitar MIDI range `[40, 88]` are discarded.

No octave jump, interval lookup, chord-template correction, key-signature correction, or sequence-derived pitch shift is permitted in Phase A.

## Frozen audio evidence representation

For production-side integration, evidence is defined on the harmonic component of mono 22,050 Hz audio:

- harmonic/percussive separation: `librosa.effects.hpss`
- CQT resolution: **48 bins/octave**
- narrow candidate band: **±0.30 semitone** around candidate MIDI
- octave-support band: the same width around candidate MIDI + 12 when available
- local baseline window: **±2.0 semitones**, excluding the central **±0.75 semitone** region
- magnitudes are converted to dB with a numerical floor before subtraction

For each candidate and event window:

- `fundamentalDeltaDb` = candidate-band dB − local-baseline dB
- `octaveDeltaDb` = octave-band dB − octave-local-baseline dB when available; otherwise `0`
- `scoreDb` = `fundamentalDeltaDb + 0.25 * max(0, octaveDeltaDb)`

The octave term is support only; it cannot overcome absent fundamental evidence.

### Frozen CQT aggregation clarification

This clarification is part of the preregistration and was committed before any V147 implementation.

Phase A's CQT evidence adapter does **not** choose audio normalization, CQT hop/fmin, or event-window timing. Those stay upstream in the existing analyzer/audio pipeline. The adapter accepts an already-computed **magnitude CQT**, the corresponding MIDI value for each CQT bin, and the explicit frame indices belonging to one event window.

For a requested centre MIDI `p`:

1. On each selected frame, `bandMagnitude(p)` is the **sum of CQT magnitudes** whose MIDI-bin centres lie in `[p-0.30, p+0.30]`.
2. On the same frame, baseline bins are those in `[p-2.0, p+2.0]` but outside `[p-0.75, p+0.75]`; `baselineMagnitude(p)` is the **median magnitude per selected baseline bin multiplied by the number of candidate-band bins**. This normalizes the baseline to the candidate band's width instead of rewarding a wider baseline region.
3. Both magnitudes are converted to dB as `20 * log10(max(value, 1e-8))`.
4. Frame delta is candidate-band dB minus normalized-baseline dB.
5. `fundamentalDeltaDb` is the **median frame delta** across the explicit event-window frames.
6. `octaveDeltaDb` is computed identically at `p+12` only when the supplied CQT bin range contains both its candidate band and baseline window; otherwise it is `0`.
7. If there are no selected frames, no candidate-band bins, no baseline bins, a shape mismatch, or any non-finite input needed for scoring, evidence extraction fails closed and the pitch decision must preserve the original MIDI.

This adapter boundary lets Phase A prove deterministic scoring without inventing a second audio front end. Later integration must feed it the existing harmonic 48-bin/octave CQT representation; any change to upstream CQT construction requires a new frozen phase/revision.

## Frozen decision rule

The original MIDI is the fail-closed default.

An alternate ±1 candidate may replace it only when **all** conditions hold:

1. alternate `fundamentalDeltaDb >= 3.0 dB`
2. alternate `scoreDb >= original scoreDb + 3.0 dB`
3. alternate fundamental evidence exceeds original fundamental evidence by at least `2.0 dB`
4. alternate is the unique best candidate after scores are rounded to `1e-6`
5. candidate is within `[40, 88]`

Otherwise V147 returns the original MIDI unchanged.

Ties, missing evidence, non-finite evidence, or malformed inputs MUST fail closed to the original MIDI.

## Phase-A implementation boundary

Phase A MUST be split so the pitch decision can be tested without Modal or live audio:

1. a pure deterministic pitch-hypothesis decision function accepting an incoming event MIDI plus candidate evidence values;
2. a reference-free CQT evidence adapter matching the frozen representation above;
3. only after the pure/generated proof passes may that corrected MIDI be handed to the existing V145 fingering/sequence decoder in a later phase.

V145 files are not to be modified in place during the first V147 proof.

## CPU/generated proof corpus

The generated proof must contain at least these classes and must not use any V145/V146 reference file:

1. **Correct-control** — original MIDI has clearly strongest evidence; expected action: keep original.
2. **Down-one recovery** — evidence is deliberately strongest at `m - 1`; expected action: change by −1.
3. **Up-one recovery** — evidence is deliberately strongest at `m + 1`; expected action: change by +1.
4. **Ambiguous neighbor** — alternate advantage is below the frozen margin; expected action: keep original.
5. **Weak evidence** — no candidate reaches the frozen absolute evidence floor; expected action: keep original.
6. **Tie** — two candidates tie after frozen rounding; expected action: keep original.
7. **Low guitar boundary** — no candidate below MIDI 40 may be emitted.
8. **High guitar boundary** — no candidate above MIDI 88 may be emitted.
9. **Non-finite/malformed evidence** — expected action: keep original.
10. **Determinism** — repeated identical inputs must produce byte-identical JSON output/hash.

The proof should include direct synthetic evidence cases first. A generated CQT-matrix adapter smoke test may also be included without changing the frozen decision thresholds. If a later proof constructs actual waveforms, it must use the already-frozen upstream analyzer representation and remain reference-free/CPU-only.

## Frozen Phase-A metrics

Report at minimum:

- `casesTotal`
- `casesPassed`
- `correctControls`
- `correctControlsFlipped`
- `deliberateMislabels`
- `deliberateMislabelsRecovered`
- `ambiguousCases`
- `ambiguousCasesKept`
- `rangeViolations`
- `malformedFailClosed`
- `deterministic`
- output SHA-256

## Frozen go / stop gate

Phase A passes only if all are true:

- every direct generated case passes its expected result;
- `correctControlsFlipped == 0`;
- every deliberately mislabelled strong-evidence ±1 case is recovered;
- every ambiguous/weak/tie case keeps the original;
- `rangeViolations == 0`;
- every malformed/non-finite case fails closed;
- determinism check passes.

Any failure is a **STOP**. Do not adjust thresholds after seeing a failed proof and rerun it as though the preregistration were unchanged. A threshold/family change requires a new checkpointed phase/revision.

## What Phase A does not prove

Passing generated evidence proves only that the bounded V147 mechanism behaves according to this frozen contract. It does **not** prove better real-song tab accuracy, and it does not authorize reading the consumed calibration reference, running live audio, or promoting V147 into Jimmy's production path.

## Next action after freeze

Implement the pure deterministic V147 hypothesis function and CPU-generated proof exactly against this contract; save the checkpoint; run only authorized CPU/reference-free evidence; then record a go/stop decision before any integration step.
