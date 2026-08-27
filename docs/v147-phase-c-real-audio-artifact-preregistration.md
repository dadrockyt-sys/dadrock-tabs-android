# V147 Phase C — Real-Audio Artifact-First Candidate Construction Preregistration

Status: **FROZEN BEFORE REAL-AUDIO ACCESS OR EXECUTION**

Branch: `v143-contextual-prune-lobo`

## Purpose

V147 Phase A proved the frozen ±1-semitone pitch-hypothesis contract on generated evidence. V147 Phase B proved that the selected MIDI can reach the untouched V145 guitar decoder on generated/reference-free inputs.

Phase C is the first real-song construction phase. Its only purpose is to construct exactly **one** immutable V147 candidate from the exact accepted Rhythm family #10 event stream using the exact historical source audio. **Phase C MUST NOT read calibration gold/reference data and MUST NOT calculate any musical accuracy score.**

This preserves an artifact-first boundary:

1. **Phase C:** real-audio evidence -> one fixed candidate -> seal candidate and construction proof, with zero reference/gold access.
2. **A later separately frozen Phase D:** validate that immutable candidate before reference access, then open calibration gold and score the fixed candidate exactly once.

No Phase-D execution is authorized by this preregistration.

## Frozen accepted source identity

Phase C starts from accepted Rhythm family #10 only:

- Name: `singleton-onset-replace-be9e9aa7a734e3cd`
- Manifest: `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`
- Manifest Git blob: `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`
- Accepted canonical event count: `1144`
- Accepted canonical event SHA-256: `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`
- Generated measure count: `113`
- Accepted scores remain `35.4 / 6.7 / 5.5 / 5.8 / 100 / 100` until a later promotion protocol succeeds.

The 1209-event V5 render stream is **not** the Phase-C candidate source. It may be used only as an immutable reconstruction ancestor if needed to deterministically materialize family #10. Before any audio byte is read, the materialized accepted event stream MUST independently canonicalize to exactly 1144 events and SHA-256 `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`. Failure is STOP.

Accepted-event reconstruction must be reference-free. Calibration gold/reference files may not be opened to reconstruct, verify, choose, repair, or rank the source stream.

## Frozen source-audio identity

The historical V144 one-shot workflow recorded the source-audio identity used by the accepted calibration chain as:

- Raw source audio SHA-256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- Historical workflow blob carrying that identity: `a9bef022032f2d5195dc54ba2a5bd9d7629686da`

The raw audio bytes are not present on the current branch. Phase C MUST NOT substitute another song, another encode, a regenerated file, or another upload. Before decoding or analysis, supplied bytes MUST hash exactly to the value above. If the exact bytes are unavailable or the hash differs, Phase C is STOP with no candidate.

Merely discovering/checking file metadata or verifying a raw-byte SHA is not musical evidence. Actual decoding, waveform access, CQT computation, or real-audio analysis remains blocked until explicitly authorized after this preregistration is frozen.

## Frozen upstream code identities

These upstream files are read-only Phase-C inputs:

- V147 pitch hypothesis `modal/v147_pitch_hypothesis.py`: blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`
- V145 guitar decoder primitives `modal/v145_rhythm_decoder.py`: blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`
- V147 Phase-B generated adapter: blob `76ce80ef998ca54797b1df8b6fb7ab46440d9a04`
- Canonical event helper `validation/rhythm_holdout/canonical.py`: blob `088d44827fb23e20d9aeeb4944a672989af5846c`
- PDF fidelity checker `validation/rhythm_holdout/verify_pdf_event_fidelity.py`: blob `5e1564216873046237fb545078a04a6b18f72b27`
- Render contract `lib/v143RenderContract.js`: blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`

The existing harmonic-evidence benchmark is **not** the Phase-C implementation and MUST NOT be run as a substitute. Its current Git blob `bd79d6eecf1e4b5d4c9b11216e62b4168a38eb0b` is historical design evidence only.

## Frozen audio front end

A new Phase-C CPU-only implementation must be created before execution. It must implement this fixed front end without reading calibration labels:

1. Verify the raw audio SHA-256 before decoding.
2. Decode to mono at exactly `22050 Hz` using a pinned, recorded dependency/toolchain. Record decoder/tool versions and the normalized PCM SHA-256 in runtime evidence.
3. Apply harmonic/percussive separation and use the harmonic component only, with `librosa.effects.hpss(..., margin=(1.0, 6.0))`.
4. Compute magnitude CQT with:
   - sample rate `22050`
   - hop length `128`
   - `bins_per_octave=48`
   - `fmin=librosa.midi_to_hz(40)` (E2)
   - `n_bins=243`, covering the frozen MIDI 40–88 candidate range plus full +12-semitone octave-support bands through MIDI 100.
5. Derive CQT-bin MIDI values from the same `fmin`, `n_bins`, and `bins_per_octave`.

Dependency versions must be pinned in the single-use execution workflow before any audio analysis. Versions are execution-environment identity, not tunable musical parameters.

## Frozen event-time mapping

Accepted Rhythm timing is structurally immutable. Phase C MUST NOT requantize, move, insert, delete, or reorder events.

For audio evidence only, map accepted event `(measure, step)` to seconds using the historically frozen calibration grid:

- tempo: `129.19921875 BPM`
- time signature: `4/4`
- 4 grid steps per beat / 16 steps per measure
- zero-based absolute step: `(measure - 1) * 16 + step`
- onset seconds: `absolute_step * (60 / 129.19921875) / 4`

The mapping is read-only evidence alignment. Candidate output retains the accepted event's original measure, step, duration, ordering, and all protected non-pitch metadata.

## Frozen frame selection

For each accepted event, CQT evidence uses explicit frames whose center times satisfy all of:

- `time >= onset + 0.020 seconds`
- `time <= onset + min(0.180 seconds, max(0.060 seconds, durationSeconds * 0.75))`
- when a later accepted onset exists, `time <= next_onset - 0.020 seconds`

At least **3** usable frames are required. If fewer than 3 exist, evidence is insufficient and the original MIDI is preserved.

No frame window may be changed after seeing Phase-C results.

## Frozen V147 per-candidate evidence aggregation

For each event's original MIDI `m`, consider only `{m-1, m, m+1}` clipped to `[40, 88]`.

For each usable frame and each candidate MIDI:

- candidate fundamental band: CQT bins within `±0.30` semitone of the candidate; sum magnitude in the band;
- local baseline window: bins within `±2.0` semitones of the candidate, excluding bins within `±0.75` semitone;
- baseline magnitude: median of the remaining bins, width-normalized to the candidate-band bin count;
- per-frame fundamental delta: `20*log10((candidate_sum + eps)/(normalized_baseline + eps))`, with a fixed implementation epsilon recorded in source and tests;
- event fundamental delta: median of per-frame fundamental deltas.

Octave support repeats the same calculation at candidate `+12` only when its complete `±2.0`-semitone baseline window is represented by the frozen CQT. Otherwise octave support is zero.

Candidate score is exactly:

`fundamental_delta_db + 0.5 * max(0, octave_delta_db)`

Then call the frozen V147 decision logic unchanged. Alternate selection requires all already-frozen Phase-A conditions:

- alternate fundamental `>= 3.0 dB`
- alternate score `>= original score + 3.0 dB`
- alternate fundamental `>= original fundamental + 2.0 dB`
- unique best after `1e-6` rounding
- selected MIDI in `[40, 88]`

Missing, malformed, non-finite, tied, weak, or ambiguous evidence preserves the original MIDI.

## Frozen candidate construction

Exactly one candidate is constructed from accepted family #10.

For every accepted event:

- preserve event count, event order, `eventIndex`, measure, step, duration/timing fields, techniques, sustain metadata, and all other protected metadata;
- only pitch/MIDI and corresponding guitar position may change;
- if V147 keeps the original MIDI, preserve the accepted event unchanged;
- if V147 selects `m-1` or `m+1`, set the event MIDI to that selected value and recompute a physically valid standard-tuning guitar position using frozen V145 guitar-position/state primitives;
- no V145 timing-lattice or nearest-timing decode may be used in Phase C, because accepted timing must remain fixed;
- for simultaneous events at the same `(measure, step)`, select a deterministic valid unique-string guitar state for the full resulting pitch set; if no valid state exists, fail closed for the **entire onset group** and preserve every accepted event in that group unchanged;
- standard tuning remains MIDI `(40,45,50,55,59,64)` for strings 6→1;
- string must be in `[1,6]`, fret in `[0,24]`, and `open_string_midi + fret == selected_midi`;
- no pitch outside `[40,88]` may be introduced by V147.

No sequence, key, scale, chord, reference, genre, artist, or hand-authored song heuristic may influence pitch selection.

## Frozen candidate invariants

The candidate must prove before it can be sealed:

- source accepted canonical event count = `1144`;
- source accepted canonical event SHA = `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`;
- candidate event count = `1144`;
- event indices/order unchanged;
- generated measure set unchanged and count = `113`;
- measure/step/timing/duration fields unchanged for every event;
- no additions/deletions;
- only MIDI/string/fret fields may differ;
- all changed MIDI values differ by exactly ±1 from their accepted source event;
- every changed guitar position reconstructs the selected MIDI;
- PDF event fidelity = exactly `1.0` for the candidate's own frozen event stream;
- deterministic repeated construction from identical bytes/events produces the same canonical candidate SHA-256 and proof payload SHA-256.

The number of pitch changes is observational only. It is not a success criterion and MUST NOT be used to retune thresholds or select among variants.

## Frozen Phase-C evidence report

Persist at minimum:

- accepted manifest path/blob;
- accepted source event count/SHA;
- raw audio SHA and normalized PCM SHA;
- decoder/librosa/numpy/scipy/soundfile/tool versions actually used;
- V145/V147/canonical/PDF/render source blob identities;
- candidate event count/SHA;
- generated measure count;
- events considered;
- usable-evidence events;
- insufficient-frame events;
- pitch changes total / down-one / up-one;
- ambiguous/weak/malformed fail-closed counts;
- onset-group fingering fail-closed count;
- position identity violations;
- timing/metadata invariant violations;
- input mutation violations;
- PDF event fidelity;
- deterministic true/false;
- `referenceRead=false`;
- `goldRead=false`;
- `calibrationScoreRun=false`;
- `candidateSearchRun=false`;
- `alternateCandidateConstructed=false`;
- `modalGpuUsed=false`;
- `productionIntegrated=false`.

## Frozen GO / STOP gate

Phase C is **GO** only if all of the following are true:

- exact accepted source identity verified;
- exact raw source-audio SHA verified before decoding;
- all frozen upstream source blobs match;
- exactly one candidate was constructed;
- candidate cardinality/order/measure/timing/metadata invariants pass;
- position identity violations = 0;
- candidate PDF event fidelity = 1.0;
- deterministic = true;
- no gold/reference file was opened;
- no calibration score was run;
- no alternate candidate/search/retuning was performed;
- no Modal/GPU or Production path was used.

Any reached-condition failure is **STOP**. Do not change windows, CQT parameters, thresholds, candidate rules, or fingering policy after observing the result. Do not construct a second candidate.

A Phase-C GO means only: **one real-audio-derived candidate was safely and deterministically constructed without reference access.** It does not mean the candidate is musically better.

## Explicitly unauthorized in Phase C

- calibration/gold/reference reads or scoring;
- validation/canary labels;
- using the accepted score to make per-event decisions;
- candidate search, alternate candidate construction, threshold tuning, or replay after a reached musical result;
- Modal cloud, L4, GPU, or remote inference;
- edits to frozen V145/V147 upstream files;
- timing changes;
- event insertion/deletion;
- `/ai-tab` frontend changes;
- Bass/Lead changes;
- `freezeReady` changes;
- `main` or Production changes;
- automatic promotion.

## Phase D boundary — NOT YET AUTHORIZED

If and only if Phase C later seals a GO candidate, a new Phase-D preregistration may be created. Phase D must keep that candidate immutable and use the frozen evaluator order:

1. candidate-only validation;
2. pre-reference freeze and PDF gate;
3. candidate/freeze/PDF identity checks;
4. accepted-manifest identity check;
5. only then verify/open calibration gold SHA-256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`;
6. score the candidate exactly once;
7. compare observationally to accepted family #10;
8. no automatic promotion.

## Immediate next action

Checkpoint this preregistration identity. Then, without reading or decoding real audio, implement and CPU-test only the reference-free accepted-event materializer, fixed-time fingering adapter, audio-evidence aggregation functions using generated numeric/CQT fixtures, and source-identity guards. Checkpoint their identities before any real-audio execution.

**STOP before real-audio decoding/analysis. Real-audio execution requires fresh explicit authorization after the implementation and generated CPU contract are frozen.**
