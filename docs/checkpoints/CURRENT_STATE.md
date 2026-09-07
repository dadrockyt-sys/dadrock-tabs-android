# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`
Previous full-detail checkpoint blob before this continuation: `45001b66c310d860cae560c8c09e396d51eeb033` (retained in Git history)
First continuation checkpoint commit: `0410c6c825d15751163a311f5389a444124a4d1f`

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

## MODEL-FREE POST-MODEL TRACE

### Timing provider

`analyzer/v143_reference_free_timing.py`
- estimates beat grid/bar phase;
- exposes `ReferenceFreeTimingEstimate.candidate_adapter_kwargs()`;
- does **not** construct final note/chord events.

### Carrier consumer

`analyzer/v143_contextual_prune_reference_free_carrier.py`
- calls `build_subdivision_grid(**timing.candidate_adapter_kwargs())`;
- runs the four historical wide-recall Basic Pitch sweeps on both deterministic guitar views;
- clusters duplicate detections per `(measure, midi)` and groups physical candidates by onset;
- each onset row carries all observed `candidateMidis` plus physical two-view CQT evidence.

This confirms polyphonic evidence exists before post-model precision pruning.

### Confirmed confidence-before-feasibility narrowing

`analyzer/v143_contextual_prune_precision_shadow.py::_precision_pitch_set(...)`
- chooses one explicit primary;
- retains secondaries only above hard relative evidence gates:
  - `SECONDARY_RAW_RATIO = 0.80`
  - `HARMONIC_SECONDARY_RAW_RATIO = 0.92`
- those gates run before legal guitar voicing is considered.

The existing audio-only polyphonic audit reinforces the issue:
- 238 multi-hypothesis attacks existed in the audited candidate;
- rendered secondaries begin almost exactly at the 0.80 confidence floor;
- serialized support was indistinguishable per pitch for all 238 multi-hypothesis attacks.

### Existing final voicing is already polyphony-capable

`analyzer/v143_rhythm_guitar_note_mapper.py::resolve_joint_chord_voicing(...)`
- deterministic standard-tuning guitar mapper;
- max fret 24;
- max six notes;
- unique strings required;
- non-crossing voicing required;
- max chord span 28 semitones;
- never adds pitches.

`analyzer/v143_contextual_prune_precision_candidate_events.py` already expanded surviving pitch sets through this resolver. The problem was that weaker observed tones could be discarded before the resolver ever saw them.

### Existing promoted-harmonic contradiction guard

`analyzer/v143_precision_promoted_harmonic_guard.py`
- when a lower physical fundamental is promoted below the strongest raw upper pitch, and that strongest upper is a recognized harmonic-family interval, the strongest upper is deliberately removed as an independent chord tone;
- attack identity and primary are unchanged;
- no unobserved pitch is added.

Any polyphony recovery must preserve this invariant and must not re-add that exact strongest promoted harmonic.

## IMPLEMENTED DETERMINISTIC POLYPHONY BOUNDARY

### New pure helper

File:
- `analyzer/v143_precision_polyphony_boundary.py`
- commit `039ddbf7bf4d859c7fa27294be13b58b3757ec3a`
- blob `720a068d71ad72719053cdc89bdab81db541c884`

`resolve_precision_polyphony(...)` now separates confidence from physical feasibility:
1. the explicit precision primary is immutable and mandatory;
2. precision-retained secondaries get priority;
3. a previously confidence-pruned secondary may be considered only when:
   - its MIDI was already in `precision.original_pitch_sets` for the same attack;
   - its two-view physical attack evidence is above the existing positive attack floor;
   - its two-view physical body evidence is above the existing positive body floor;
4. the candidate is admitted only if `resolve_joint_chord_voicing(...)` can still place the entire selected set legally;
5. max six strings, duplicate-string collisions, pitch-span, fret and non-crossing constraints remain enforced by the existing mapper;
6. the exact strongest promoted upper harmonic contradiction is excluded from recovery;
7. no pitch outside the observed set can be emitted.

No scorer/reference data, chord names, key, song labels, model output reranking, new attack creation, or attack relocation is accepted by the helper.

### Model-free regression tests

File:
- `analyzer/test_v143_precision_polyphony_boundary.py`
- commit `76ba535a3832204812832cebeac1ee92d028abdd`
- blob `97fbcf4bd8ce791a3323cb45bcc08c8f17ac438a`

Covered cases:
- weaker positive observed pitch survives when a legal joint voicing exists;
- weaker observed pitch is rejected when two notes require the same only-available string (`87 + 88` within the 0–24 fret rule);
- strongest promoted upper harmonic is not reintroduced (`40 + 52` synthetic guard case);
- non-positive observed pitch is not recovered;
- no unobserved pitch is created;
- primary remains present;
- simultaneous rendered strings are unique.

Local deterministic execution of the pure helper regression cases passed. No Basic Pitch, Modal, separator, Rhythm/Lead/Bass model, scorer, professional reference, optimizer, or GPU path was initialized.

### Precision assembly wiring

File:
- `analyzer/v143_contextual_prune_precision_candidate_events.py`
- commit `bb3a8ddcd86e2fb9df167ff6c5fa60b75820d2e0`
- blob `68732a07701a30a455ba9bcbf7c2adddd3930622`

Changes:
- consumes both `precision.pitch_sets` and `precision.original_pitch_sets`;
- obtains CQT physical evidence for all originally observed pitches;
- calls the new pure feasibility boundary;
- keeps `dominantMidi` equal to the immutable precision primary;
- serializes all observed `pitchHypotheses` with explicit diagnostics:
  - `precisionRetained`
  - `feasibilityRecoveryEligible`
  - `feasibilityRecovered`
  - `rendered`
- emits recovered notes only when they were observed and legally voiceable;
- every recovered note is marked `noteMapping.feasibilityRecoveredSecondary = true`;
- event-level invariants now validate emitted MIDI against `precision.original_pitch_sets`, not an invented external set;
- a non-precision pitch without the explicit recovery marker is rejected;
- attack identity remains exactly `precision.retained_events`.

A local stubbed integration exercise of the committed assembly design also passed for a weaker observed `40 + 47` dyad: both notes rendered, primary stayed 40, and recovery was explicitly marked. This was source-level/model-free validation only; it was **not** a model-bearing pipeline run.

## NEXT SAFE SLICE

1. Add/perform branch-safe static validation of the three committed files without importing or initializing any model-bearing runtime.
2. Inspect downstream semantic/sustain/export stages for assumptions that one attack has one event, especially:
   - bend/legato enrichment;
   - semantic primary-note guard;
   - sustain shadow/promotion;
   - final `render_rhythm_tab(...)` / render-event serializer;
   - any `(measure, step)` dictionary that overwrites same-onset chord notes.
3. If a downstream same-onset overwrite is found, patch only that deterministic post-model boundary and add model-free regression coverage.
4. Add a deterministic pre-export validator for:
   - unique simultaneous strings;
   - legal string/fret/MIDI mapping;
   - primary preservation;
   - no unobserved recovered MIDI;
   - no duplicate identical note identity;
   - stable event ordering with multiple notes at one attack.
5. Checkpoint again immediately after downstream trace/validator work.
6. Only after the score-structure path is safely closed, locate the actual async control/result ownership TTL and patch that lifetime separately.

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
No model/scheduler/threshold parameter was changed.

**Current handoff:** the confidence-before-feasibility polyphony boundary is now repaired and covered by pure deterministic tests. Continue by tracing the already-generated multi-note attack events through semantic, sustain, and export/render stages for any same-onset overwrite or single-note assumption, then add the deterministic pre-export validator. Keep all work model-free and checkpoint often.
