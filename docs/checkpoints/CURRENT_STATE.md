# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`
Prior checkpoint lineage retained in Git history:
- pre-continuation full-detail blob `45001b66c310d860cae560c8c09e396d51eeb033`
- hook trace checkpoint `0410c6c825d15751163a311f5389a444124a4d1f`
- polyphony repair checkpoint `4cb4c57e52cf21e95877d984f6002236abca1727`
- integrated repair checkpoint `b09fddb5da4486e8bccab34636cdd844183c1d85`

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

The one authorized replacement V143 Rhythm model-bearing start has been consumed.
The one authorized professional full-1–113 score has been consumed.

Current counters:
- replacement live model start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis and **DO NOT** run the professional scorer again without new explicit user authorization.
Also do not deploy/promote production, weaken Deployment Protection, run optimizer/training/threshold sweeps, or mutate model/scheduler parameters as part of evaluation.

Safe work now is deterministic/model-free source analysis, repair, static validation, and read-only inspection of already-consumed evidence.

## IMMUTABLE RECOVERED RUN / FROZEN RESULT

Exact authorized Rhythm run:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- run `34046854397`
- job `101523324268`
- one start accepted around `2026-09-06T16:54:33Z`
- worker completed successfully at `elapsed=936.836`

Same-run recovery:
- recovery run `34048291636`
- job `101527199470`
- job ID `K7aeTJDV7fp7l5R5UwsOvJkrC_mCDQt0`
- recovered worker-result SHA-256 `185a19dcd58df7bece23a75b300bb3f9fbf6d6322bf61b52b1e667b5ba684293`

Frozen product facts:
- E Standard, ~129.199 BPM, 4/4
- candidateCount **1818**
- selected attack count **364**
- final rendered note count **925**
- raw/canonical/frozen events **925 / 925 / 925**
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

## IMPLEMENTED MODEL-FREE PRECISION-PATH REPAIR

### Pure confidence/feasibility boundary

`analyzer/v143_precision_polyphony_boundary.py`
- commit `039ddbf7bf4d859c7fa27294be13b58b3757ec3a`
- blob `720a068d71ad72719053cdc89bdab81db541c884`

Behavior:
- immutable precision primary;
- already-retained secondaries have priority;
- only same-attack MIDI values from `precision.original_pitch_sets` may be reconsidered;
- requires positive two-view physical attack/body evidence using existing floors;
- recovered pitch is admitted only when `resolve_joint_chord_voicing(...)` accepts the complete set;
- existing six-string/fret/span/non-crossing constraints stay intact;
- exact strongest promoted upper harmonic contradiction remains blocked;
- cannot create/relocate attacks or invent pitch/chord/key/song/reference facts.

Pure tests:
`analyzer/test_v143_precision_polyphony_boundary.py`
- commit `76ba535a3832204812832cebeac1ee92d028abdd`
- blob `97fbcf4bd8ce791a3323cb45bcc08c8f17ac438a`

Local deterministic checks passed; no model-bearing runtime initialized.

### Precision candidate assembly

`analyzer/v143_contextual_prune_precision_candidate_events.py`
- commit `bb3a8ddcd86e2fb9df167ff6c5fa60b75820d2e0`
- blob `68732a07701a30a455ba9bcbf7c2adddd3930622`

Now consumes both `precision.pitch_sets` and `precision.original_pitch_sets`, preserves immutable primary, serializes observed/recovery provenance, allows only observed legally voiceable recovery, and rejects any non-retained note lacking explicit `feasibilityRecoveredSecondary` provenance.

### Fail-closed pre-export validator

`analyzer/v143_rhythm_preexport_validator.py`
- commit `4c807cb47e8cd4c9ded51591e279d6149004a9cb`
- verified blob `b654c306cdbfec4a998a9f8fb3f33690ff4a97e3`

Checks:
- legal standard-tuning string/fret/MIDI;
- unique simultaneous strings;
- no duplicate note identity;
- stable ordering/eventIndex;
- immutable primary/sourceAttackMidi;
- complete chordNoteCount/chordNoteIndex metadata;
- common observed hypothesis set per attack;
- recovered pitch must be observed and explicitly recovery-marked.

Tests:
`analyzer/test_v143_rhythm_preexport_validator.py`
- commit `924f2b9d3695c229ebeca9f173ff559d231eca70`

`analyzer/v143_precision_sustain_promotion.py`
- commit `3d6d80b1aba0154aa423d883bce0fe4d4d5b2f20`
- blob `30d79f5392324691b95cb91f28cc1f26a0765cef`

The final promoted precision event list now fails closed through the validator before render/export.

### Isolated precision-candidate product integration

`analyzer/v143_repaired_timing_precision_candidate_product_modal.py`
- commit `affe42af558ee597290e8bacf28ce76ce5f0283d`
- verified blob `63a58b1360786abf7ddc89e4aa67e6daeba0496b`

Fixed two deterministic seams:
- Modal source bundle now includes `v143_precision_polyphony_boundary` and `v143_rhythm_preexport_validator`;
- stale final assertion `midi in precision.pitch_sets` was replaced by:
  - MIDI must be in `precision.original_pitch_sets`;
  - if absent from pruned `precision.pitch_sets`, explicit `feasibilityRecoveredSecondary = true` is mandatory.

Output now records `preExportValidation` and that confidence gating is not the final feasibility gate.

**Important:** no Modal function was invoked. This is source-only integration and is **not** the exact live path that produced the frozen 925-event result.

## DOWNSTREAM PRECISION-PATH TRACE — NO SAME-ONSET OVERWRITE FOUND

Inspected:
- bend consensus/evidence;
- legato evidence;
- semantic primary-note guard;
- sustain shadow/promotion;
- Python rhythm output adapter;
- `lib/v143RenderContract.js`.

These stages preserve multi-note attacks. The Python renderer stores a list per step and rejects duplicate strings. JS projects each event independently and reports maximum chord size / multi-note onset count.

## EXACT FROZEN/LIVE PATH TRACE — NEW CRITICAL FINDING

The exact one-shot workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml` pins and reuses the existing preview and verifies these live files, including:
- `analyzer/v143_modal_http_endpoint.py`
- `analyzer/v143_async_job_protocol.py`
- `analyzer/v143_modal_live_endpoint.py`
- `analyzer/v143_seeded_separator.py`

Pinned live worker blob:
`analyzer/v143_modal_live_endpoint.py` = `111bf14a8f91045d3478901f8e36b88a2e7f181a`

The live Rhythm route is:
`v143_modal_live_endpoint.rhythm_v143_request`
→ `v143_modal_rhythm_router.route_normalized_audio`
→ `v143_reference_free_rhythm_pipeline.analyze_reference_free_rhythm`
→ `v143_rhythm_event_assembly.assemble_rhythm_events`
→ `v143_rhythm_guitar_note_mapper.map_selected_v143_rows`
→ sustain/technique enrichment
→ `v143_rhythm_output_adapter.build_rhythm_output`.

Therefore the exact frozen/live path does **not** call `build_precision_candidate_assembly(...)` or the isolated repaired precision-candidate product.

### Live mapper already has substantial polyphonic expansion

`v143_rhythm_guitar_note_mapper.py::credible_polyphonic_hypotheses(...)` filters Basic Pitch hypotheses before `resolve_joint_chord_voicing(...)` using existing reliability/confidence gates:
- max source-count winner requirement;
- absolute amplitude ≥ 0.11;
- relative amplitude ≥ 40% of strongest;
- event count ≥ 2;
- grid error ≤ 0.06 s;
- duration ≥ 0.05 s;
- then near-unison suppression and legal joint voicing.

This is structurally confidence-before-feasibility, but **do not loosen it blindly**.

### Read-only replay of already-consumed frozen worker result

Artifact inspected read-only:
- recovery run `34048291636`
- artifact `v143-recovered-orchestrator-result`
- artifact ID `9993769594`
- `recovered-worker-result.json`

Facts from the frozen serialized result:
- candidateCount **1818**
- selected attacks **364**
- rendered notes **925**
- multi-note rendered attacks **259 / 364**
- all 364 selected attacks have >1 observed pitch hypothesis
- total observed playable pitch hypotheses across selected attacks: **7624**
- rendered: **925**
- observed but not rendered: **6699**

A deterministic read-only replay of the current mapper rules found:
- 6300 suppressed hypotheses fail the relative-amplitude gate (non-exclusive reason count);
- 3929 fail the absolute 0.11 amplitude floor;
- 3244 fail max-source winner equality;
- 2970 fail eventCount≥2;
- 1086 fail duration≥0.05;
- only 16 fail grid error≤0.06.

Critically, if only the 40% relative-amplitude winner gate were bypassed while retaining max-source + all existing absolute reliability gates, **1511** currently suppressed pitches would become eligible and **1338** are individually legally voiceable with the frozen rendered set across **285 attacks**. A greedy legal-voicing replay preserving the existing near-unison rule would add **812 notes across 283 attacks**, frequently filling attacks to six notes.

Given the professional frozen score already reports **779 unmatched generated notes**, that direction is unsafe and likely worsens over-generation.

**Conclusion:** the frozen/live failure is not a one-note-per-attack collapse. The exact live path is already highly polyphonic. Do **not** relax live mapper thresholds or source-count/relative-amplitude gates based solely on feasibility.

## CURRENT DIAGNOSIS

There are two distinct paths:

1. **Exact frozen/live path** — broad Basic Pitch hypothesis cloud → conservative live mapper → 364 attacks / 925 notes. It is already polyphonic and has poor pitch/chord correctness. Blindly recovering more notes is contraindicated by the frozen evidence.

2. **Isolated repaired precision path** — contextual-prune precision v2 + promoted-harmonic guard → deterministic legal polyphony boundary + provenance validator. This path is designed to reduce/structure the hypothesis cloud before final voicing, but it has not been proven as the deployed/frozen live route and must not be treated as such.

The next work should determine the intended safe integration boundary between these paths without running a model or scorer.

## NEXT SAFE SLICE

1. Read-only trace branch history/source around the precision-candidate product to determine whether it was explicitly intended as a replacement product path, shadow candidate, or evaluation-only path.
2. Inspect any adapter/orchestrator already present that can consume **precomputed/frozen** precision evidence without initializing a new model. Prefer replayable deterministic evidence over a new live run.
3. Do **not** loosen live Basic Pitch polyphony thresholds. Do **not** change model/scheduler thresholds.
4. If a deterministic source integration can route already-produced precision output through the same final render contract without model execution, implement only that adapter/validation seam and add pure tests.
5. Checkpoint immediately after that trace/integration decision.
6. Once score construction/export is genuinely closed, separately locate the real async control/result lifetime (~900 s) and patch only that ownership boundary to exceed the 1200-second worker budget.

## CONTINUATION STATUS

No model-bearing run was started in this continuation.
No professional scorer was run.
No evaluation budget was consumed.
No production deployment/promotion was performed.
No model/scheduler/threshold parameter was changed.
No Modal remote function was invoked.
The frozen worker artifact was only downloaded and inspected read-only.

**Current handoff:** the isolated precision path is repaired model-free, while the exact frozen/live path is confirmed to be a separate already-highly-polyphonic 364→925 pipeline. Do not relax the live mapper. Next determine the intended precision-path integration/replay boundary using source/history and already-produced evidence only. Keep saving this checkpoint often.
