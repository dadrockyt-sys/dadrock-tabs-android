# V147 Phase B — Generated Pitch-to-Decoder Integration Preregistration

Status: **FROZEN BEFORE PHASE-B IMPLEMENTATION**

Branch: `v143-contextual-prune-lobo`

## Purpose

V147 Phase A is complete, GO, and sealed for the generated/reference-free pitch-hypothesis contract. Phase B tests the next architectural boundary only:

> Can the frozen V147 pitch decision be applied to generated Rhythm events and then passed into the frozen V145 CPU decoder so the downstream fingering is computed for the selected MIDI, while ambiguous/malformed evidence still fails closed?

This phase is not a real-song accuracy evaluation. It does not authorize calibration/gold access, live audio, Modal/L4/GPU execution, or Production integration.

## Frozen upstream identities

The following files are inputs and MUST remain unchanged during Phase B:

- V145 decoder `modal/v145_rhythm_decoder.py`: blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`
- V147 pitch hypothesis `modal/v147_pitch_hypothesis.py`: blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`
- V147 Phase-A tests: blob `f71d1da6c52a6a737faca7ab4f8989fb702be96d`
- V147 Phase-A proof harness: blob `e9d28739cd19f095cb83807fd0b23c2b14b7c966`
- V147 original preregistration: blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`

Accepted Rhythm family #10 and all V145/V146 scoring/evaluation identities remain untouched.

## Phase-B implementation boundary

Create a new CPU-only adapter module. It MUST NOT edit V145 or Phase-A V147 files in place.

The adapter may:

1. accept a sequence of generated Rhythm event mappings;
2. normalize those events only through the existing frozen V145 `normalize_rhythm_events` behavior;
3. accept generated V147 candidate-evidence mappings keyed by original V145 `source_index`;
4. apply the frozen `choose_pitch_hypothesis` decision independently to each normalized event;
5. clone caller-owned event mappings and, only when V147 selects a different MIDI, place that selected MIDI into a canonical `midi` field on the clone so the untouched V145 normalizer consumes the corrected pitch;
6. pass the cloned event sequence into the untouched V145 `decode_nearest_timing_path`;
7. return deterministic integration evidence containing pitch decisions, cloned events, and the V145 decode result.

The adapter MUST NOT mutate caller-owned event mappings.

## Frozen evidence behavior

- Evidence is generated/direct numeric evidence only; no audio is read in Phase B.
- Evidence keys are original event `source_index` integers.
- Missing, malformed, non-finite, tied, weak, or ambiguous evidence inherits the Phase-A fail-closed rule and preserves the original MIDI.
- Phase B MUST NOT add sequence/key/chord/reference heuristics or change any V147 threshold.
- Corrected MIDI remains bounded by the already-frozen V147 `[40, 88]` rule.

## Frozen generated integration cases

The Phase-B proof must include at least:

1. **Control passthrough** — strong original evidence; V147 keeps original; V145 decodes the same MIDI.
2. **Down-one end-to-end** — strong `m-1`; V147 changes by -1; V145 output MIDI equals the corrected pitch and selected string/fret reconstructs that MIDI in standard tuning.
3. **Up-one end-to-end** — strong `m+1`; same downstream identity requirement.
4. **Ambiguous fail-closed** — insufficient alternate margin; original MIDI reaches V145 unchanged.
5. **Malformed/missing fail-closed** — original MIDI reaches V145 unchanged.
6. **Caller immutability** — input event mappings are byte-equivalent before/after adapter execution.
7. **Source cardinality** — for valid generated events, normalization/decision/downstream evidence counts remain identical.
8. **Determinism** — repeated identical generated inputs produce byte-identical canonical integration output/hash.
9. **Frozen-source identity** — runtime proof records V145/V147 upstream Git blob identities and fails if they differ from the frozen values above.

## Frozen downstream identity checks

For every decoded note in the generated proof:

- `decoded_note.midi` must equal the MIDI that V145 consumed after V147 selection;
- standard tuning reconstruction must hold: selected open-string MIDI + fret = decoded MIDI;
- string must be in `[1, 6]` and fret must be in `[0, 24]`;
- no pitch outside `[40, 88]` may be introduced by V147.

Phase B does not change V145's timing or fingering costs, state enumeration, or continuity policy.

## Frozen metrics

Report at minimum:

- `casesTotal`
- `casesPassed`
- `inputEvents`
- `normalizedEvidence`
- `decisions`
- `pitchChanges`
- `controlFlips`
- `strongAlternatesRecovered`
- `ambiguousKept`
- `malformedKept`
- `sourceCardinalityViolations`
- `positionIdentityViolations`
- `inputMutationViolations`
- `deterministic`
- canonical proof payload SHA-256

## Frozen GO / STOP gate

Phase B is GO only if all are true:

- every generated integration case passes;
- control events are not flipped;
- both strong ±1 cases are recovered end-to-end;
- ambiguous and malformed/missing evidence keep original MIDI;
- source cardinality violations = 0;
- position identity violations = 0;
- input mutation violations = 0;
- deterministic = true;
- V145 and V147 frozen source blobs match exactly.

Any reached-case failure is **STOP**. Do not tune thresholds, alter generated expectations, or edit frozen upstream modules after observing a failure.

## Explicitly unauthorized in Phase B

- calibration/gold/reference reads or scoring;
- real audio or waveform analysis;
- analyzer integration;
- Modal cloud, L4, GPU, or any remote inference;
- edits to `modal/v145_rhythm_decoder.py` or `modal/v147_pitch_hypothesis.py`;
- `/ai-tab` frontend changes;
- Bass/Lead changes;
- `freezeReady` changes;
- main/Production changes;
- automatic promotion.

## Next action

Implement only the new generated integration adapter, its contract tests, and a standalone CPU/generated proof. Checkpoint implementation identities before execution. Then execute one repository-native CPU/reference-free proof, persist exact evidence, seal its one-use workflow, and stop at GO/STOP.
