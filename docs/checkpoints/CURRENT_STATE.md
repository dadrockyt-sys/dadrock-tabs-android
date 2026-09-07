# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`
Prior checkpoint lineage retained in Git history:
- pre-continuation full-detail blob `45001b66c310d860cae560c8c09e396d51eeb033`
- hook trace checkpoint `0410c6c825d15751163a311f5389a444124a4d1f`
- polyphony repair checkpoint `4cb4c57e52cf21e95877d984f6002236abca1727`
- integrated repair checkpoint `b09fddb5da4486e8bccab34636cdd844183c1d85`
- live-vs-precision split checkpoint `13550deba569cf9c85a5fe7d48294434cbba24ae`

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

The one authorized replacement V143 Rhythm model-bearing start has been consumed.
The one authorized professional full-1–113 score has been consumed.

Current counters:
- replacement live model start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis and **DO NOT** run the professional scorer again without new explicit user authorization.
Also do not deploy/promote production, weaken Deployment Protection, run optimizer/training/threshold sweeps, or mutate model/scheduler parameters as part of evaluation.

Safe work now is deterministic/model-free source analysis, repair, static validation, and read-only inspection/replay of already-consumed evidence.

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

Output records `preExportValidation` and that confidence gating is not the final feasibility gate.

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

## EXACT FROZEN/LIVE PATH TRACE

The exact one-shot workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml` pins and reuses the existing preview and verifies live files including:
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

Do not loosen it blindly.

### Read-only replay of already-consumed frozen worker result

Artifact inspected read-only:
- recovery run `34048291636`
- artifact `v143-recovered-orchestrator-result`
- artifact ID `9993769594`
- `recovered-worker-result.json`

Facts:
- candidateCount **1818**
- selected attacks **364**
- rendered notes **925**
- multi-note rendered attacks **259 / 364**
- all 364 selected attacks have >1 observed pitch hypothesis
- total observed playable pitch hypotheses across selected attacks **7624**
- rendered **925**
- observed but not rendered **6699**

Deterministic read-only mapper replay found non-exclusive suppression reasons:
- 6300 fail relative amplitude;
- 3929 fail absolute 0.11 amplitude;
- 3244 fail max-source equality;
- 2970 fail eventCount≥2;
- 1086 fail duration≥0.05;
- 16 fail grid error≤0.06.

Bypassing only the 40% relative-amplitude gate while retaining the remaining rules would make 1511 suppressed pitches eligible, 1338 individually legally voiceable with the frozen rendered set, and a greedy legal replay could add about **812 notes across 283 attacks**.

Given the professional frozen score already has **779 unmatched generated notes**, that direction is unsafe.

**Conclusion:** the frozen/live failure is not a one-note-per-attack collapse. Do not relax live mapper thresholds or source-count/relative-amplitude gates solely because a pitch is guitar-feasible.

## HISTORY PROOF — PRECISION PRODUCT IS ISOLATED EVALUATION, NOT LIVE REPLACEMENT

Branch history now provides explicit intent:
- `0626287d410aac69d1a4a61c96301c5172041894` — `v143: add isolated repaired-timing candidate product`
- `27e52d525459554eed9930802199fcb87e79b884` — `v143: add repaired timing precision candidate product`
- `84feba722161b18e6ee31b587bd56bfc345d1c3b` — checkpoint authorizing a one-shot paid precision capture
- `aecdd04771850e7b43f13ced7751cdd11cf3be41` — `v143: add dormant one-shot paid capture workflow`
- `15d805facdd2c95b5a2f4f3c96be853777e592fe` — checkpoint recording successful paid precision capture
- `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` — `v143: validate precision candidate`

The candidate repeatedly serialized/declared:
- `protectedLivePipelineModified: false`
- `liveEndpointDeployedOrModified: false`
- `productionModified: false`

Therefore **do not wire this candidate into the live endpoint by assumption**. It was deliberately isolated for evaluation/replay.

## PERSISTED PAID PRECISION CAPTURE — CPU-ONLY REPLAY IS THE AUTHORIZED CONTINUATION PATH

The successful one-shot paid precision capture used approved fixture:
- `public/gomywayfullaitest.m4a`
- SHA-256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`

The capture is already consumed. Do not buy/rerun it without new explicit authorization.

Committed product/evidence from `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`:
- `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json`
  - blob `7e6002cd4d42f355685241e0576c78940056f093`
- `debug/v143-contextual-prune/repaired-timing-precision-replay-evidence.json`
  - blob `c1dec90e744624752ebe51676469aa5d99b11e23`
- `debug/v143-contextual-prune/replay-validation-a.json`
  - blob `d2633fdc353000bbe9f2954005948265358bb60a`
- `debug/v143-contextual-prune/replay-validation-b.json`
  - same blob `d2633fdc353000bbe9f2954005948265358bb60a`

Paid capture facts recorded by the successful-capture checkpoint:
- final tempo `129.19921875`
- beat-grid interval outliers `5 → 0`
- lookahead bridge beats `5`
- bar phase unchanged
- repaired attack moves `0`
- full audio-derived measure range `1–113`
- corrected retained attacks `858`
- precision-v2 retained attacks `725`
- precision-v2 selected pitches `970`
- final rendered pitches `967`
- after promoted-harmonic guard convenience count `965` (diagnostic layer)
- v2 attack additions/removals `0 / 0`
- v2 pitch additions/removals `22 / 4`
- promoted-harmonic strongest pitches dropped `2`
- semantic changed pitch/attack `false / false`
- onset-present-after guard `725`
- all 113 measures populated.

Persisted replay evidence stores, for each retained `(measure, step)` attack:
- original raw pitch hypotheses;
- final selected pitch set;
- explicit primary MIDI chosen live;
- attack strength.

Historical CPU-only replay validation reproduced the capture exactly:
- retained attacks `725`
- matched attacks `725`
- mismatch count `0`
- original pitch hypotheses `6525`
- live selected pitches `970`
- replay selected pitches `970`
- live/replay flat SHA-256 `b1e3fdf591420871ac1d9a1fa7d5a6fe4572b9febb73bf52b176ad3e90cb06a`
- deterministic replay `true`
- repeated replay A/B payloads identical `true`
- `addsUnobservedAttack=false`
- `addsUnobservedPitch=false`
- `referenceFree=true`
- `professionalReferenceUsed=false`
- `paidModelRequired=false`.

A later persisted precision event-layer replay also exists:
- workflow `.github/workflows/v143-replay-precision-candidate.yml`
- historical run `33803626150`
- head SHA `4c4c6cb2835708399e531c475b9725c70b405732`
- artifact `v143-replay-precision-candidate-33803626150`
- `replay-product-summary.json`
- `replay-product-events.json`
- result: 725 attacks / 965 rendered notes; all 113 measures populated; no unobserved attack/pitch; reference-free; paid-model-free.

The successful-capture checkpoint explicitly directs future deterministic policy work to use the persisted CPU-only replay bundle rather than purchasing another capture.

## CURRENT DIAGNOSIS

There are two distinct paths:

1. **Exact frozen/live path** — broad Basic Pitch hypothesis cloud → conservative live mapper → 364 attacks / 925 notes. It is already polyphonic and has poor pitch/chord correctness. Blindly recovering more notes is contraindicated by the frozen evidence.

2. **Isolated precision evaluation path** — contextual-prune precision v2 + promoted-harmonic guard → deterministic candidate assembly. Its one authorized paid capture is persisted and exactly reproducible CPU-only. This is the correct evidence source for testing deterministic post-capture policy changes, but it is **not** authorization to replace the live path.

A new risk must now be tested before retaining the recent feasibility-recovery change: the new boundary may recover too many of the 6525 original precision hypotheses that precision-v2 intentionally pruned. Guitar feasibility alone is not evidence of musical correctness. The persisted replay bundle lets us quantify that risk without a model or scorer.

## NEXT SAFE SLICE

1. Inspect the small committed `replay-validation-a.json` / `b.json` files and the CPU-only replay workflow/script to establish the exact replay schema/tooling.
2. Replay the **new feasibility-recovery boundary** against the persisted paid precision evidence only, without Basic Pitch, Modal, models, scorer, reference, optimizer, or GPU.
3. Quantify only reference-free structural effects:
   - retained attack identity;
   - original hypothesis count;
   - selected pitch count before recovery;
   - number of recovered pitches/attacks;
   - legal-voicing drops;
   - max chord size;
   - whether any unobserved pitch/attack is created;
   - whether the promoted-harmonic guard is violated.
4. If the recent helper materially explodes note count, **do not keep it merely because tests pass**. Revise or remove the recovery behavior using only deterministic source-evidence invariants; do not tune to the professional score.
5. Save checkpoint immediately after the CPU-only replay result and before any further source change.
6. Do not integrate the isolated precision candidate into live production unless a separate explicit product decision/authorization supports that.
7. After score-structure/replay work is closed, separately locate the real async control/result lifetime (~900 s) and patch only that ownership boundary to exceed the 1200-second worker budget.

## CONTINUATION STATUS

No model-bearing run was started in this continuation.
No professional scorer was run.
No evaluation budget was consumed.
No production deployment/promotion was performed.
No model/scheduler/threshold parameter was changed.
No Modal remote function was invoked.
Only committed history and already-consumed frozen/precision evidence were inspected read-only.

**Current handoff:** history proves the precision product is an intentionally isolated evaluation path, and its one paid capture plus exact CPU replay bundle are committed in Git. Next replay the recent feasibility-recovery boundary against that persisted evidence model-free; be prepared to revise/remove the recovery if it expands the precision result materially. Keep saving this checkpoint often.

## FRESH CHAT START HERE — 2026-09-06

Resume on branch `v143-contextual-prune-lobo`. Do not spend any new model/scorer/Modal budget.

Most important newly confirmed historical fact:
- successful authorized paid precision retry workflow run `32805316807` completed fully green;
- capture/replay commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` recorded the persisted schema-2 evidence;
- strict replay mismatch counts were exactly zero (`primaryRecomputeMismatchAttackCount=0`, `v2ReplayMismatchAttackCount=0`);
- successful-capture checkpoint explicitly says all next precision work must use persisted replay CPU-only and that no further Modal/L4 run is authorized.

Exact fresh-chat next steps:
1. Open commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` and inspect the committed replay files plus `.github/workflows/v143-replay-precision-candidate.yml` / its CPU-only script. Prefer the persisted Git evidence over expired Actions artifacts.
2. Note connector quirk observed in this chat: direct `fetch_file` of `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` on the branch returned an empty decoded `content` while still returning known blob SHA `7e6002cd4d42f355685241e0576c78940056f093`. Do **not** infer the evidence is absent; use the historical commit, blob SHA, replay-evidence file, or committed replay validators as the source of truth.
3. Run/reproduce only a **CPU-only deterministic replay** of the new `v143_precision_polyphony_boundary.py` feasibility-recovery behavior against the persisted paid precision evidence. No Basic Pitch inference, no Modal, no GPU, no professional reference/scorer, no optimizer, no threshold sweep.
4. Compare against the persisted precision baseline: 725 retained attacks, 970 selected pitches (967 rendered before later guard convenience layer; historical event-layer replay 965 rendered), all 113 measures populated, and zero unobserved attack/pitch creation.
5. Record structural deltas only: recovered pitches, affected attacks, total selected/rendered notes, max chord size, legal-voicing rejections, primary preservation, attack identity, unobserved pitch/attack count, and promoted-harmonic-guard violations.
6. Decision rule: if feasibility recovery materially inflates the precision product, revert/restrict the helper using deterministic source-evidence invariants. Guitar feasibility alone is insufficient. Do not tune against the consumed professional score.
7. Checkpoint `CURRENT_STATE.md` immediately after the replay result **before** changing the helper or candidate assembly further.
8. Keep the isolated precision candidate isolated. Do not wire it into the exact live endpoint or Production without a separate explicit integration/product authorization.
9. Only after this score-structure slice is closed, return to the separate async-result lifetime defect and locate the actual ~900-second ownership TTL before patching it to safely exceed the 1200-second worker budget.

Fresh-chat success condition for the next slice: obtain a deterministic, reference-free answer to **“Does the new feasibility-recovery boundary safely preserve the persisted precision candidate, or does it over-recover pruned hypotheses?”** with zero new paid/model/professional evaluation consumption.

## CONTINUATION CHECKPOINT — FEASIBILITY REPLAY PREP

Resumed on `v143-contextual-prune-lobo`; branch head at resume was `0d335c15237d8fa0d851edba5df680ab432c089d`.

Confirmed before any runtime-affecting change:
- the next operation remains a CPU-only deterministic structural replay of `analyzer/v143_precision_polyphony_boundary.py` against already-persisted precision evidence;
- no new Basic Pitch/model/Modal/GPU/professional scorer/reference/optimizer work is authorized or needed;
- `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` is present with known blob `7e6002cd4d42f355685241e0576c78940056f093`;
- GitHub's decoded large-file path is unreliable for that product, but the Git Data blob endpoint can read the committed evidence;
- the historical replay-evidence blob identifier recorded above did not resolve directly in the connector, so the immediate next action is to resolve the exact current path/blob for the persisted replay evidence and CPU-only replay plumbing before executing structural metrics.

Static inspection of `v143_precision_polyphony_boundary.py` also found two audit/robustness items to verify during replay rather than changing blindly: `familiesAfter` appears to be computed from the full timeline before filtering by string, and restored-string bookkeeping should be checked against the actual candidate string chosen. Neither observation has changed runtime behavior yet.

No source/runtime behavior was changed in this continuation before this checkpoint. No model call, scorer call, Modal function, production deployment, optimizer, or threshold sweep was performed.


## CONTINUATION CHECKPOINT — FEASIBILITY REPLAY RESULT

CPU-only deterministic boundary replay is complete. No model, Basic Pitch inference, Modal/GPU function, professional scorer/reference, optimizer, threshold sweep, production deployment, or new paid evaluation was used.

Replay tooling added:
- `analyzer/v143_precision_polyphony_boundary_replay.py` — commit `4b52f281d37753ad10dbd8ee7b1a1f4a7778158f`
- isolated workflow `.github/workflows/v143-precision-polyphony-boundary-cpu-replay.yml` — commit `c465a339231e0d0d8c71b30cd85824518d1adb08`
- successful CPU-only replay run `34074850353`, job `101598839853`
- persisted result `debug/v143-contextual-prune/precision-polyphony-boundary-replay.json`

Authoritative persisted precision identity used by this replay:
- retained attacks: **725**
- original retained-attack pitch hypotheses: **7535**
- stored precision-selected pitches: **970**
- deterministic selected-only rendered baseline: **967**
- all source evidence comes from the already-consumed schema-2 `precisionReplayEvidence` embedded in `repaired-timing-precision-candidate-product.json`.

Boundary replay result:
- boundary candidate pitches: **4653**
- recovery-eligible pitches: **3683**
- recovered pitches: **2518**
- recovered attacks: **703 / 725**
- rendered pitches after recovery: **3485**
- rendered delta vs 967 baseline: **+2518**
- rendered ratio vs baseline: **3.6039296794208893x**
- max baseline chord size: **5**
- max recovered chord size: **6**
- candidate pitches dropped by voicing/capacity: **1168**
- retained-precision voicing drops in baseline: **3**
- retained rendered pitch loss caused by recovery: **0**
- primary violations: **0**
- unobserved pitch creations: **0**
- unobserved attack creations: **0**
- promoted-harmonic guard violations: **0**
- protected promoted-harmonic attacks: **96**
- attack identity changed: **false**.

Decision: **the feasibility-recovery boundary materially over-recovers pruned hypotheses and is unsafe to keep as-is.** Physical positivity + legal guitar voicing are necessary feasibility checks but are not sufficient evidence of musical correctness. The helper passes its safety invariants while still inflating the deterministic precision product from 967 to 3485 rendered notes.

Important stale-guard finding: `analyzer/v143_precision_optional_candidate_accounting.py` still expects an older identity of 987 retained / 6548 suppressed pitches. The current persisted product records 970 retained / 6565 suppressed. Do not modify that historical accounting helper merely to make the new boundary replay green; the boundary replay has been isolated from it.

NEXT SAFE ACTION, only after this checkpoint: remove or sharply restrict the post-precision recovery behavior using deterministic source-evidence invariants. Do not tune against the consumed professional score and do not introduce a threshold sweep. Preserve the precision-selected pitch set as the musical authority unless a non-threshold source invariant proves a recovery is semantically mandatory. Keep the candidate isolated from the exact live endpoint/Production.
