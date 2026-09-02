# Open-Corpus V4 GuitarSet Player-05 Confirmation — Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose and timing

This confirmation contract is frozen **after** `H72-D035` was selected by the preregistered exact discovery-family rule on players `02/04`, and **before any player `05` V4 reference is read**.

This is a one-shot internal confirmation, not a new discovery phase and not a threshold search. It tests exactly one previously selected reference-blind rule on one independent development player.

## Frozen selected rule

Only **`H72-D035`** is eligible for confirmation.

An event changes pitch only when all are true:
1. frozen trigger observation has `triggerEligible == true`;
2. frozen ordinary V2 proposal differs from baseline;
3. frozen ordinary V2 winner equals `baselinePitch - 12` exactly;
4. baseline MIDI pitch is **>=72**;
5. frozen Basic Pitch event duration `end-start` is **<=0.35 seconds**.

For selected events, pitch becomes the already-frozen `ordinaryV2Winner`. Onset, end, amplitude and event identity remain unchanged. All other events retain baseline pitch. Event count must remain identical.

No alternative thresholds, directions, pitch floors, duration cutoffs, amplitude gates, style gates, per-track gates, or learned models may be introduced after player-05 reference use begins.

## Frozen confirmation partition

Player `05` is the only confirmation player.

Expected admissible confirmation tracks: **60**.

The confirmation workspace must contain:
- the immutable V3 candidate artifact, reverified before references;
- exactly the 60 player-`05` GuitarSet JAMS references;
- no player `02` or `04` JAMS;
- no prospective player `00`, `01`, or `03` JAMS;
- no WAV/audio files.

The scorer may verify all 177 frozen candidate JSON hashes before references, but it must score only the 60 player-05 candidate payloads.

## Frozen reference semantics

Use the unchanged V3/V4 exact-pitch scorer semantics:
- `note_midi` JAMS namespace with `pitch_midi` fallback only if needed;
- exactly six string annotations;
- pitch = `int(round(note.value))`;
- onset = `float(note.time)`;
- all six strings aggregated without deduplication;
- primary one-to-one onset tolerance = **100 ms**;
- strict secondary tolerance = **50 ms**.

No timing offsets, onset edits, duration edits, candidate regeneration, or audio inference are permitted.

## Frozen one-shot confirmation outputs

Score baseline and `H72-D035` over the same 60 tracks and report:
- baseline and H72-D035 primary macro F1;
- baseline and H72-D035 primary combined micro F1;
- baseline and H72-D035 strict50 combined micro F1;
- exact changed-pitch count;
- per-track primary TP delta;
- number of positive, neutral and negative-primary-TP tracks;
- event-count identity.

This run makes exactly one player-05 confirmation score call.

## Frozen confirmation qualification gate

`H72-D035` passes confirmation only if **all** conditions are true:
1. event-count identity holds for every confirmation track;
2. at least one pitch is changed by the frozen rule;
3. primary macro F1 gain vs baseline is **strictly > 0.00 pp**;
4. primary combined micro F1 gain vs baseline is **strictly > 0.00 pp**;
5. strict50 combined micro F1 delta vs baseline is **>= 0.00 pp**;
6. **no player-05 track has primary TP delta < 0**.

The no-track-loss condition is intentionally carried forward from the zero-harm discovery-family hypothesis. It must not be relaxed after the confirmation result is observed.

Status is:
- `V4_PLAYER05_CONFIRMATION_PASS` only if all conditions pass;
- otherwise `V4_PLAYER05_CONFIRMATION_FAIL`.

There is no fallback config, no threshold adjustment, and no second confirmation attempt after a scientific result is produced.

## Frozen consequence

If confirmation **fails**:
- V4 closes for this hypothesis;
- do not weaken or retune `H72-D035` using player-05 outcomes;
- do not open prospective players `00/01/03` for this V4 design.

If confirmation **passes**:
- immediately checkpoint the result;
- do not yet read `00/01/03`;
- first freeze a separate prospective-evaluation contract, candidate-generation/application identity, one-shot scoring gate and promotion/non-regression rule before prospective references are touched.

## Pre-reference guards required

Before extracting player-05 references, the real confirmation workflow must verify:
- immutable candidate artifact ID/name/digest/original run/head;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- all 177 candidate JSON hashes;
- frozen selected-rule/scorer code identities;
- candidateRegenerated=false;
- Basic Pitch not importable in the scorer runtime;
- no audio files.

Static/synthetic guards must pass before the real one-shot confirmation workflow is armed.

## Counters at preregistration

- selected V4 config: **`H72-D035`**;
- exact V4 discovery-family score calls: **1**;
- player `05` V4 reference read: **false**;
- player `05` confirmation score calls: **0**;
- GuitarSet prospective evaluation processed: **false**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
