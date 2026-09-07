# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`
Previous full-detail checkpoint blob before this continuation: `45001b66c310d860cae560c8c09e396d51eeb033` (retained in Git history)
Continuation checkpoints:
- hook trace: `0410c6c825d15751163a311f5389a444124a4d1f`
- polyphony repair: `4cb4c57e52cf21e95877d984f6002236abca1727`

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

## CONFIRMED ASYNC DEFECT — DEFERRED UNTIL SCORE-STRUCTURE SLICE IS CLOSED

The parent control/result tracking lifetime is ~900 seconds while worker/orchestrator runtime budget is 1200 seconds. The successful worker completed at 936.836 s, after the client-side tracking record expired.

Do **not** patch a guessed `ASYNC_RESULT_TTL_SECONDS` symbol. Locate the actual ownership/control-state implementation before changing only that lifetime to safely exceed 1200 seconds.

## ROOT MUSICAL-STRUCTURE FINDING

Reference-free timing itself is not the note-loss source.

`analyzer/v143_contextual_prune_reference_free_carrier.py` retains same-onset multi-pitch evidence in `candidateMidis` plus two-view CQT evidence. The narrowing occurs later in precision selection.

Current product uses `analyzer/v143_contextual_prune_precision_shadow_v2.py`:
- explicit primary is chosen and preserved;
- non-harmonic secondaries require two of score/attack/body at legacy 0.80;
- harmonic upper secondaries require all three at 0.92;
- this is still a confidence gate before guitar feasibility.

The downstream joint voicing resolver is already polyphony-capable:
`analyzer/v143_rhythm_guitar_note_mapper.py::resolve_joint_chord_voicing(...)`
- standard tuning;
- frets 0–24;
- max 6 notes;
- unique strings;
- non-crossing voicing;
- max 28-semitone chord span;
- never adds a pitch.

`analyzer/v143_precision_promoted_harmonic_guard.py` remains an important contradiction guard: when a lower fundamental is promoted below the strongest positive raw upper harmonic-family pitch, that exact strongest upper may be removed as an independent note. Recovery must not re-add it.

## IMPLEMENTED — DETERMINISTIC CONFIDENCE/FEASIBILITY SEPARATION

### Pure polyphony boundary

`analyzer/v143_precision_polyphony_boundary.py`
- commit `039ddbf7bf4d859c7fa27294be13b58b3757ec3a`
- blob `720a068d71ad72719053cdc89bdab81db541c884`

`resolve_precision_polyphony(...)` now:
- keeps the precision primary immutable;
- gives already precision-retained secondaries priority;
- may reconsider only MIDI values already present in `precision.original_pitch_sets` for that same attack;
- requires positive two-view attack/body evidence using the existing physical floors;
- admits a recovered pitch only if the existing joint-guitar-voicing resolver accepts the entire set;
- preserves six-string/string-collision/fret/span/non-crossing constraints;
- blocks reintroduction of the exact strongest promoted upper harmonic;
- cannot add/relocate attacks or invent pitch/chord/key/song/reference information.

### Pure boundary tests

`analyzer/test_v143_precision_polyphony_boundary.py`
- commit `76ba535a3832204812832cebeac1ee92d028abdd`
- blob `97fbcf4bd8ce791a3323cb45bcc08c8f17ac438a`

Covers:
- weaker observed legal chord tone recovered;
- impossible same-string combination rejected;
- promoted strongest harmonic not reintroduced;
- non-positive pitch not recovered;
- unobserved pitch cannot appear;
- primary remains immutable;
- simultaneous strings remain unique.

Local deterministic pure checks passed. No Basic Pitch, Modal, separator, model, scorer, reference, optimizer, or GPU path was initialized.

### Precision candidate assembly wiring

`analyzer/v143_contextual_prune_precision_candidate_events.py`
- commit `bb3a8ddcd86e2fb9df167ff6c5fa60b75820d2e0`
- blob `68732a07701a30a455ba9bcbf7c2adddd3930622`

Changes:
- consumes `precision.pitch_sets` **and** `precision.original_pitch_sets`;
- runs the pure feasibility boundary using already-present CQT evidence;
- keeps `dominantMidi` equal to immutable primary;
- serializes all observed pitch hypotheses with `precisionRetained`, `feasibilityRecoveryEligible`, `feasibilityRecovered`, and `rendered` markers;
- recovered final notes are explicitly marked `noteMapping.feasibilityRecoveredSecondary = true`;
- emitted MIDI must remain in `precision.original_pitch_sets`;
- a non-retained MIDI without explicit recovery provenance is rejected;
- attack identity remains exactly `precision.retained_events`.

A model-free stubbed integration exercise rendered the weaker observed `40 + 47` dyad, kept primary 40, and marked 47 as recovered.

## DOWNSTREAM MULTI-NOTE TRACE — NO SAME-ONSET COLLAPSE FOUND

Inspected deterministic downstream stages:
- `v143_rhythm_bend_consensus.py`
- `v143_rhythm_bend_evidence.py`
- `v143_rhythm_legato_evidence.py`
- `v143_rhythm_semantic_primary_note_guard.py`
- `v143_rhythm_sustain_consensus_shadow.py`
- `v143_precision_sustain_promotion.py`
- `v143_rhythm_output_adapter.py`
- `lib/v143RenderContract.js`

Findings:
- bend analysis works per emitted event;
- legato tracks the next event per mapped string, not one event per attack;
- semantic guard keeps every note and strips attack-level audio techniques from secondary chord notes instead of deleting them;
- sustain is per event / per string;
- Python tab output stores a list of events per step and fails on duplicate simultaneous strings rather than overwriting;
- JS render projection keeps every event independently and explicitly summarizes maximum chord size / multi-note onset count.

No downstream `(measure, step)` winner overwrite or one-note-per-attack collapse was found in these stages.

## IMPLEMENTED — FAIL-CLOSED PRE-EXPORT SCORE VALIDATION

### Validator

`analyzer/v143_rhythm_preexport_validator.py`
- commit `4c807cb47e8cd4c9ded51591e279d6149004a9cb`
- verified committed blob `b654c306cdbfec4a998a9f8fb3f33690ff4a97e3`

`validate_v143_preexport_events(...)` checks only already-constructed score events:
- legal measure / 16th-note step;
- valid standard-tuning string, fret, and exact string+fret→MIDI relationship;
- no duplicate identical note identity;
- stable event order and eventIndex;
- no duplicate simultaneous string;
- consistent attack primary / `sourceAttackMidi`;
- exactly one primary technique note when primary metadata exists;
- `chordNoteCount` equals rendered group size;
- `chordNoteIndex` is complete;
- all notes at one attack serialize the same observed pitch set;
- a feasibility-recovered secondary must be present in observed `pitchHypotheses` and explicitly marked recovered rather than precision-retained.

Diagnostics include event count, attack count, multi-note attack count, max chord size, recovered secondary count and pass flags.

### Validator tests

`analyzer/test_v143_rhythm_preexport_validator.py`
- commit `924f2b9d3695c229ebeca9f173ff559d231eca70`

Covers:
- legal recovered dyad accepted;
- duplicate simultaneous string rejected;
- illegal standard-tuning mapping rejected;
- recovered MIDI without observed provenance rejected;
- missing/changed primary rejected;
- unstable event order rejected.

Local pure validation passed; no model-bearing path was initialized.

### Final sustain/presentation boundary now invokes validator

`analyzer/v143_precision_sustain_promotion.py`
- commit `3d6d80b1aba0154aa423d883bce0fe4d4d5b2f20`
- blob `30d79f5392324691b95cb91f28cc1f26a0765cef`

After final event indices/start/end/duration/onset/offset are assigned, the complete promoted event list is validated fail-closed before it can be handed to render/export consumers.

## CANDIDATE PRODUCT INTEGRATION BLOCKER FOUND AND REPAIRED

File:
`analyzer/v143_repaired_timing_precision_candidate_product_modal.py`

Problem found:
1. its Modal source bundle did not include the new polyphony helper, so the repaired candidate assembly import would fail if the wrapper were later run;
2. its post-sustain invariant still required every rendered MIDI to be in pruned `precision.pitch_sets`, which would reject every legitimate feasibility-recovered note.

Repair commit:
- `affe42af558ee597290e8bacf28ce76ce5f0283d`
- verified committed blob `63a58b1360786abf7ddc89e4aa67e6daeba0496b`

Verified branch-read state:
- `CANDIDATE_MODULES` now includes `v143_precision_polyphony_boundary` and `v143_rhythm_preexport_validator`;
- the wrapper explicitly runs pre-export validation after sustain promotion;
- emitted MIDI is now checked against `precision.original_pitch_sets`;
- if emitted MIDI is absent from pruned `precision.pitch_sets`, it must carry `feasibilityRecoveredSecondary = true`;
- output records `preExportValidation` diagnostics;
- `precisionPolicy` explicitly records that confidence gating is not the final feasibility gate;
- file terminates normally; no accidental truncation detected.

No Modal function was invoked. This was source-only integration.

## NEXT SAFE SLICE

1. Inspect the exact one-shot/live workflow and production/runtime source path that produced the frozen 925-event run, read-only, to determine whether it uses this repaired candidate-product path or a different adapter. Do not assume the isolated candidate-product wrapper is the live path.
2. Search any other branch-local callers of `build_precision_candidate_assembly(...)` for:
   - missing source-bundle inclusion of the new helper/validator;
   - stale `midi in precision.pitch_sets` assertions;
   - any final-event normalization that could erase recovery provenance.
3. Perform only static/pure validation available without triggering Actions/Modal/model inference/scorer.
4. If the actual live source path has a deterministic integration seam, patch only that seam and add model-free coverage.
5. Checkpoint immediately after the exact live-path trace/integration.
6. Once score construction/export is genuinely closed, separately locate the actual async control/result state lifetime that expires around 900 seconds and patch only that ownership boundary to exceed the 1200-second worker budget.

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
No Modal remote function was invoked.

**Current handoff:** the post-precision confidence/feasibility boundary, downstream score invariants, pre-export validation, and isolated candidate-product integration are repaired model-free. Next trace the exact one-shot/live source path read-only before deciding whether another deterministic integration patch is needed. Keep saving this checkpoint often.
