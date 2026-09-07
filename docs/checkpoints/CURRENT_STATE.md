# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`
Previous full-detail checkpoint blob before this continuation: `45001b66c310d860cae560c8c09e396d51eeb033` (retained in Git history)

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

The one authorized replacement V143 Rhythm model-bearing start has been consumed.
The one authorized professional full-1–113 score has been consumed.

Current counters:
- replacement live model start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis and **DO NOT** run the professional scorer again without new explicit user authorization.
Also do not deploy/promote production, weaken Deployment Protection, run optimizer/training/threshold sweeps, or mutate model/scheduler parameters as part of evaluation.

Safe work now is deterministic/model-free source analysis, repair, static validation, and read-only evidence inspection.

## IMMUTABLE RECOVERED RUN / FROZEN RESULT

Exact authorized Rhythm run:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- run `34046854397`
- job `101523324268`
- one start accepted around `2026-09-06T16:54:33Z`
- worker completed successfully at `elapsed=936.836`

Same-run recovery succeeded read-only:
- recovery run `34048291636`
- job `101527199470`
- job ID `K7aeTJDV7fp7l5R5UwsOvJkrC_mCDQt0`
- recovered worker-result SHA-256 `185a19dcd58df7bece23a75b300bb3f9fbf6d6322bf61b52b1e667b5ba684293`

Frozen product facts:
- E Standard, ~129.199 BPM, 4/4
- raw/canonical/frozen events: **925 / 925 / 925**
- frozen canonical event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- playable string/fret 925/925
- pitch validity 925/925
- render survival 100%
- PDF event fidelity **1.0**

## PROFESSIONAL HOLDOUT — CONSUMED, DO NOT RERUN

Scoring run:
- workflow `.github/workflows/v143-score-recovered-frozen-result.yml`
- run `34048719525`
- job `101528345557`
- authoritative result `rhythm-professional-holdout-score.json`

Result:
- `near100ProfessionalGatePassed = false`
- `rhythmComplete = false`
- `criticalMismatchCount = 1581`
- measure coverage recall `0.9823008849557522`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- string/fret timing tolerant F1 `0.02672367717797969`
- chord pitch-set tolerant F1 `0.004136504653567736`
- exact voicing tolerant F1 `0.004136504653567736`
- PDF event fidelity `1.0`
- missing measures `88, 99`
- extra generated measures `114, 115`
- unmatched generated notes `779`
- unmatched reference notes `800`

Interpretation: infrastructure/render fidelity succeeded; musical score construction did not. Do not use the professional reference at runtime and do not tune against its thresholds.

## CONFIRMED ASYNC DEFECT — DEFERRED UNTIL SCORE-STRUCTURE SLICE IS SAFE

The parent control/result tracking lifetime is ~900 seconds while worker/orchestrator runtime budget is 1200 seconds. The successful worker completed at 936.836 s, after the client-side tracking record expired.

Do **not** patch a guessed `ASYNC_RESULT_TTL_SECONDS` symbol. Locate the actual ownership/control-state implementation before changing only that lifetime to safely exceed 1200 seconds.

## MODEL-FREE TIMING / POST-MODEL TRACE

### Timing provider

`analyzer/v143_reference_free_timing.py`
- estimates beat grid/bar phase;
- exposes `ReferenceFreeTimingEstimate.candidate_adapter_kwargs()`;
- does **not** construct final note/chord events.

### Carrier consumer — exact branch-local downstream path found

`analyzer/v143_contextual_prune_reference_free_carrier.py`
- imports `v143_candidate_timing_adapter` and `v143_reference_free_timing`;
- calls `build_subdivision_grid(**timing.candidate_adapter_kwargs())`;
- runs the four historical wide-recall Basic Pitch sweeps on both deterministic guitar views;
- clusters duplicate detections per `(measure, midi)` and then groups physical candidates by onset;
- each onset row carries **all** observed `candidateMidis` plus physical two-view evidence.

This confirms the reference-free timing estimator is only upstream context. The carrier still has polyphonic pitch evidence before precision pruning.

### First confirmed polyphony-loss risk — narrow repair hook

`analyzer/v143_contextual_prune_precision_shadow.py`

The function `_precision_pitch_set(...)` chooses one explicit primary and then admits secondary pitches only if they pass hard relative physical-evidence gates:
- `SECONDARY_RAW_RATIO = 0.80`
- `HARMONIC_SECONDARY_RAW_RATIO = 0.92`

Those gates run **before** guitar-voicing feasibility is considered. A musically/physically compatible lower-confidence chord tone can therefore be removed even when it would complete a legal voicing.

This is the first confirmed winner-by-strength style narrowing in the post-model score-construction path.

### Downstream voicing stage is already polyphony-capable

`analyzer/v143_contextual_prune_precision_candidate_events.py`
- receives `precision.pitch_sets`;
- `_voicing_with_explicit_primary(...)` keeps the precision primary immutable;
- iterates the remaining supported MIDI values and retains each one when `resolve_joint_chord_voicing(...)` says the entire set remains playable;
- expands one retained attack into multiple final note events when the surviving pitch set supports a legal chord;
- preserves `pitchHypotheses`, `dominantMidi`, and explicit per-note string/fret assignments.

Therefore **do not** rewrite the final assembly into a new chord engine. The smallest justified repair is one stage earlier: stop confidence-only pruning from deleting otherwise physically supported, legally voiceable secondary tones.

### Render contract observation

The final JS render contract can fall back to `event.dominantMidi` when `event.midi` is absent, but the precision candidate assembly explicitly emits one event per selected MIDI with `event.midi` populated. The currently confirmed loss occurs before that point in `precision.pitch_sets`, not in render serialization.

## NEXT IMPLEMENTATION SLICE — IN PROGRESS

1. Inspect model-free tests around `v143_contextual_prune_precision_shadow.py`, `v143_contextual_prune_precision_candidate_events.py`, and `v143_rhythm_guitar_note_mapper.py`.
2. Implement the **smallest deterministic post-model repair** at the precision-pitch-set/voicing boundary:
   - keep the explicit precision primary;
   - keep genuinely contradictory/unsupported pitches prunable;
   - allow lower-confidence observed secondary tones when they have positive two-view physical evidence **and** complete a legal joint guitar voicing;
   - never invent a pitch, attack, string/fret, chord label, key, or reference-derived fact;
   - cap by six strings and preserve duplicate-string collision protection through joint voicing resolution.
3. Add pure/model-free tests proving:
   - a weaker but physically supported legal chord tone survives;
   - a conflicting/unplayable secondary is still rejected;
   - no unobserved pitch can be created;
   - the primary remains immutable;
   - final emitted notes have unique simultaneous strings and legal string/fret mappings.
4. Run only pure/static/unit tests that cannot initialize Basic Pitch, Modal, separator inference, Rhythm/Lead/Bass models, or the professional scorer.
5. Checkpoint this file again immediately after source/test changes and validation.

## PRODUCT TARGET / SAFETY RULES

- Preserve valid polyphony; prune contradictions, not complexity.
- Separate confidence from feasibility.
- Prefer diagnostics over silent deletion when deterministic correction is ambiguous.
- Preserve timing, meter, pickup, tuning, attack grouping, sustain/voice relationships, and event identity.
- No reference/scorer leakage into runtime.
- No new model-bearing run or professional scorer without fresh explicit user authorization.

## CONTINUATION STATUS

No model-bearing run was started in this continuation.
No professional scorer was run.
No evaluation budget was consumed.
No production deployment/promotion was performed.

**Current exact hook:** `analyzer/v143_contextual_prune_precision_shadow.py::_precision_pitch_set(...)` removes secondary tones by strength before `analyzer/v143_contextual_prune_precision_candidate_events.py::_voicing_with_explicit_primary(...)` gets a chance to test whether those tones form a legal polyphonic guitar voicing. Continue there with a deterministic, model-free, reference-blind repair and tests.
