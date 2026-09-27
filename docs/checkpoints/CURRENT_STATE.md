# Astra — current handoff

Updated: 2026-09-26 UTC  
Branch: `astra-work`  
Status: **DECODER V2 ZERO-OPTIMIZER P1 CHECK GREEN; TRAINING-ONLY ENGINEERING GATE MET 16/16 TP, 0 FP, 0 FN; RESULT FROZEN; NO GENERALIZATION SCREEN OR FULL TRAINING AUTHORIZED**  
Next-chat guide: `docs/astra/NEXT_CHAT.md`

## Direction

Do not restart full V1–V5-style training. V1–V5 remain FAIL; V4 is still the best historical legacy development macro F1 at 0.243523 and V5 remains 0.064131. The V5 onset-admission collapse was already diagnosed. P3 remains sealed.

The economical path is now concrete: preserve explicit source attacks, prove one tiny event-aware candidate can fit four of its own P1 training examples under a hard budget, and only then consider a separate same-budget cross-performer screen.

## Offline preparation completed

- `astra_backend/evaluation/prepared_event_adapter_v1.py` preserves source attack IDs and frozen lag identity; handles carry-in without false onsets; excludes boundary events from event/offset scoring; whole-event masks registered exclusions; and reports unsupported frets, overlaps, negative aligned time, sub-frame attacks and frame-grid collisions instead of silently repairing them.
- `astra_backend/tiny_fit_pilot_v1.py` freezes one candidate only: 192->128 ReLU shared encoder, six-string state head, explicit onset head, random seed 20260921, Adam lr 0.01.
- Onset supervision is explicit source-event supervision, not state changes. The decoder can emit same-string/same-fret reattacks and does not invent a fret-change attack without onset admission.
- Hard code caps: four P1 examples, one view each, 200 frames/example, 200 optimizer steps total, 2700 seconds training/evaluation, 3600 seconds whole job, one candidate, zero automatic retries.
- Exact frozen capture keys:
  1. `P1|chords|Drop3_7|directinput`
  2. `P1|scales|Ab|directinput`
  3. `P1|singlenotes|allsinglenotes|directinput`
  4. `P1|techniques|PalmMute|directinput`
- Future real source handling lists each pinned ZIP then extracts exactly one selected MIDI plus one direct-input audio member. Unrelated media is not extracted.
- `docs/astra/TINY_FIT_PILOT_DESIGN_V1.json` is the exact design blob verified by the synthetic gate. Do not edit it without re-running verification.

## Exact-runtime synthetic gate — PASS

GitHub Actions run **36275788105**, job **108498148554**, head `2975017d9632f75a9e24e4eb5d8e3b2ae0546468`: **SUCCESS**.

Verified runtime: Python 3.10.15, NumPy 1.21.6, Torch 1.11.0+cpu, CPU.

The gate passed:
- event-contract regression tests;
- fabricated prepared-event adapter tests;
- tiny-fit component/cap tests;
- stable source attack IDs;
- carry-in with no false onset;
- whole-event mask semantics;
- same-fret reattack decoding;
- explicit onset supervision;
- finite synthetic backward pass and decreasing synthetic loss;
- optimizer-cap and wall-cap extension rejection;
- selected-ZIP extraction isolation.

Execution boundary: **20 synthetic optimizer-step operations only; 0 real optimizer steps; no P1, P2 or P3 media accessed; no paid compute.**

Frozen receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V1.json`.  
GitHub artifact ID: `10917501716`.

## Dormant real pilot

`.github/workflows/astra-tiny-fit-pilot-real.yml` is prepared but intentionally has **no workflow_dispatch**. It can trigger only when a future `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V1.json` is committed.

Before media access it requires:
1. the frozen synthetic receipt;
2. a separately created real authorization document explicitly granting this exact P1-only 200-step scope;
3. a source-pinned launch document matching all frozen Git blobs.

It has a 60-minute GitHub CPU job timeout, no P2/P3 source path, no automatic retry, and no route to full training.

## Current authorization / launch boundary

The user explicitly continued with the exact frozen P1 scope in chat on 2026-09-26.

Created once:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V1.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V1.json`

Launch commit: `9aa5c9e89a41e08c2cc25681bf77fe481020a608`.  
Canonical capped P1 workflow run: **36276196059**, job **108499312084**.

This authorization applies only to that single bounded run: four specified P1 training examples, one view each, 200 frames/example, at most 200 optimizer steps total, one candidate, zero retries, zero paid compute. **Do not create a second launch artifact, rerun the workflow, extend optimizer steps, open P2/P3, retune thresholds, or restart full training without new explicit authorization.**

## Advancement rule if the real pilot is later authorized

Training-example explicit-event F1 >= 0.95; matched offsets within 50 ms >= 0.90; repeated-attack coverage must be present and recall >= 0.90; all metrics finite; zero unresolved selected-crop labels.

Passing is only an engineering learnability screen. It does not prove generalization and does not authorize full training, P2/P3, production use or customer delivery. Failure stops the candidate; no extra epochs, retries, threshold rescue or second architecture are automatic.

## Verification notes

The earlier workflow-definition failures at runs created before the UTF-8 workflow repair are configuration-only and are not pilot evidence. The repaired synthetic run above is the canonical verification.

Normal `Astra backend tests` also passed on the design-trigger commit. Historical V1–V5 results and Event-v2 evidence remain unchanged.

## Preserved history

The pre-pilot history remains at `docs/checkpoints/archive/CURRENT_STATE_2026_09_26_PRE_PILOT.md` (original Git blob `1ae91540ac02133a4a1c63989350ad615f065954`). Consult specific sections only when needed.

## Explicit next steps for the next chat

1. Inspect canonical run **36276196059** / job **108499312084**. Do not launch or rerun anything.
2. If it is still in progress, record the current step only; the existing run is the sole authorized real P1 execution.
3. When it completes, inspect the bounded result and artifact. Preserve run ID, job ID, head SHA, runtime versions, prepared-example/source hashes, optimizer-step count, elapsed time, metrics, unresolved-label counts, stop reason, and artifact identity in a frozen result receipt and this checkpoint.
4. If it fails or stops before/during optimizer work, preserve evidence and diagnose the existing run only. No automatic retry, no added steps/epochs, no threshold rescue, no second candidate, no P2/P3, and no V6/full-training restart.
5. If it passes every frozen training-only threshold, preserve evidence and stop. Passing permits only the future **design** of a separate same-budget cross-performer screen; it does not itself authorize that screen or any full training.

Frozen advancement conditions remain:
- minimum per-example explicit-event F1 >= 0.95;
- matched-offset-within-50-ms fraction >= 0.90;
- repeated same-string/same-fret attack coverage present;
- repeated-attack recall >= 0.90 when present;
- all metrics finite;
- unresolved selected-crop label count = 0.

Current state at this checkpoint: **one capped P1 pilot authorized and launched; canonical run 36276196059 in progress; no second launch/rerun authorized; P2/P3 closed; full training not restarted.**

## Capped P1 pilot attempt 1 — PREPARATION FAILURE, NOT A MODEL RESULT

Canonical run **36276196059**, job **108499312084**, launch head `9aa5c9e89a41e08c2cc25681bf77fe481020a608`, attempt 1 completed **failure**.

The authorization/hash gate and exact frozen runtime installation passed. The run failed in **Prepare exactly four selected P1 training examples** before the training step. Therefore:
- real optimizer steps executed: **0**;
- model fitting/evaluation did not run;
- no advancement metrics exist;
- P2 and P3 were not accessed;
- no bounded-result artifact was uploaded;
- cleanup completed successfully.

P1 media access was limited to the first pinned archive, `P1_chords.zip`. Its hash checks passed, and exactly the selected `Drop3_7` MIDI and direct-input WAV were extracted before the preparation guard stopped:
- MIDI: `P1_chords/midi/midi_Drop3_7.mid`, 2729 bytes, SHA-256 `a5856f6a6c1306fa6f0070ba8cf14dd8d61c60f1e3cc852695e5e05031c2274a`;
- audio: `P1_chords/audio/directinput/directinput_Drop3_7.wav`, 29532984 bytes, SHA-256 `c3dccbba8365eb1a701c2bf47dca6aae8be894aff768323cea19ad00a3d1d34e`.

Failure:
`RuntimeError: metadata selection no longer matches frozen pilot capture keys`

Root cause: `select_pilot_capture_keys()` sorted bare performance names. With the real correction map, bare `"A"` sorts before `"Ab"`, while the frozen scale capture is `P1|scales|Ab|directinput`. The frozen identity was derived from full capture-key lexical ordering, where the separator makes `...|Ab|...` sort before `...|A|...`. The synthetic unit fixture omitted the competing `A` key, so this inconsistency escaped verification.

Offline repair: order performances by their lexicographically first **full capture key** and add a regression fixture containing both `A` and `Ab`. This does not change the four frozen capture identities, architecture, objective, thresholds, training budget, or P2/P3 boundary.

**The failed authorization was single-launch. A second real P1 run is not authorized.** After exact-runtime synthetic re-verification of the repair, create a new source-pinned authorization request and require new explicit user authorization before another real media/optimizer run.

## Offline repair verification — PASS

Repair commit: `12632441e4fc90ce41d0315ec3b9174f2a569607`.

Exact-runtime synthetic verification run **36277137786**, job **108501969202**: **SUCCESS**. Normal backend tests run **36277137773** also passed.

The repaired selector regression explicitly includes both P1 scale performances `A` and `Ab`, and `test_metadata_only_selection_is_frozen` passes while retaining the original frozen capture key `P1|scales|Ab|directinput`.

Repair verification boundary: **0 real optimizer steps; no P1/P2/P3 media accessed; no paid compute.** Candidate architecture, objective, thresholds, 200-step cap, four frozen capture keys and P2/P3 boundaries are unchanged.

Frozen repaired receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V2.json`.
Final V2 request blob: `9a2ad838e8e6e4de1d53ceee45fc35e0bc1b6bfe`.  
Dormant V2 workflow blob: `2e8a16371c11ca5ef7bf9aba3d2b4fbb9ec11324`.  
Synthetic artifact ID: `10917224706`.

## Retry gate — REQUEST ONLY

A new reviewable request is frozen at:
`docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V2.json`.

A separate dormant retry workflow is prepared at:
`.github/workflows/astra-tiny-fit-pilot-real-v2.yml`.

The V2 workflow triggers only on a future commit of `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V2.json`. That launch file does **not** exist. `TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json` also does **not** exist.

**Do not rerun attempt 1 and do not create V2 authorization/launch artifacts unless the user explicitly authorizes the exact V2 request.**

If explicitly authorized, verify every V2-pinned blob, create `TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json` matching the request exactly, then create exactly one source-pinned `TINY_FIT_PILOT_REAL_LAUNCH_V2.json`. One retry only; zero automatic retries.

Attempt 1 remains non-model evidence: 0 optimizer steps. P2/P3 remain closed and full training remains stopped.

## V2 capped P1 retry — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen V2 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V2.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V2.json`

Authorization commit: `5942493a9fc373e5fe20f9c7aeee21d58e7caedc`.  
Launch commit: `891bbcc00391163fc4820235886d3ca1be76c113`.  
Canonical V2 workflow run: **36277631151**, job **108503320536**.

Scope remains exactly frozen: four specified P1 training performances, one view each, 200 frames/example, at most 200 optimizer steps total, 2700-second train/eval cap, 3600-second job cap, one candidate, zero automatic retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Do not create another V2 launch, rerun this workflow, extend optimizer steps, retune thresholds, open P2/P3, or restart full training without new explicit authorization.**

Next action: inspect only run **36277631151**. Preserve its result/failure evidence when complete. If it fails, diagnose that existing run only. If it passes, preserve evidence and stop; no cross-performer screen is authorized yet.

## V2 capped P1 retry — PREPARATION FAILURE, NOT A MODEL RESULT

Canonical run **36277631151**, job **108503320536**, launch head `891bbcc00391163fc4820235886d3ca1be76c113`: **FAILURE during preparation**.

The V2 selector repair passed: authorization/source pins and runtime setup succeeded, and the first frozen capture `P1|chords|Drop3_7|directinput` was selected. The run then stopped because its chosen 200-frame event crop was not launch-ready:

`RuntimeError: prepared pilot example has unresolved labels`

Execution boundary:
- real optimizer steps: **0**;
- training/evaluation: **not executed**;
- P1 media access: first pinned chords archive only;
- P2/P3 access: **none**;
- automatic retry: **none**;
- result artifact: **none**;
- cleanup: **success**.

The exact unresolved subtype is **not recoverable from this run** because the V2 harness wrote the temporary metadata locally but raised before printing the unresolved diagnostics; cleanup then removed the temporary files. Do not invent whether it was overlap, sub-frame attack, frame-grid collision, unsupported fret or another registered unresolved condition.

Frozen failure receipt: `docs/astra/TINY_FIT_PILOT_REAL_FAILURE_V2.json`.

## Offline crop-repair direction

The next offline design is `docs/astra/TINY_FIT_PILOT_DESIGN_V2.json`.

It keeps the same four P1 captures, model architecture, objective, thresholds and 200-step budget. The only preparation change is source-driven and training-only: enumerate deterministic repeated-attack candidates first, then individual source-attack candidates, and select the earliest crop whose prepared labels are `launchReady` with zero unresolved selected-crop labels. Rejected candidates are not repaired; their unresolved-code summaries are retained. If no clean crop exists, fail closed before optimizer work.

The real harness now emits `TINY_FIT_PREPARE_REJECT=` structured diagnostics before a crop-preparation stop.

**No further real P1 run is authorized.** First require exact-runtime synthetic verification of this offline repair. Only after a frozen successful verification may a new request-only authorization artifact be prepared.

## Launch-ready crop repair — exact-runtime verification PASS

Repair commit: `192d61755924f296604fb1706666228e70dff378`.

Synthetic verification run **36279935269**, job **108509713391**: **SUCCESS**. Backend tests run **36279935295**: **SUCCESS**.

Verified in Python 3.10.15 / NumPy 1.21.6 / Torch 1.11.0+cpu:
- launch-ready crop selection skips unresolved candidates;
- an all-unresolved candidate set fails closed;
- unresolved crop rejection diagnostics are retained;
- existing event/carry/mask/reattack tests still pass;
- synthetic backward/loss-decrease and hard budget-extension guards still pass.

Verification boundary: **0 real optimizer steps; no P1/P2/P3 media accessed; no paid compute.**

Frozen receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V3.json`.  
Artifact ID: `10917829509`.

## V3 retry gate — REQUEST ONLY

Request: `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V3.json`.
Final V3 request blob: `00f74000650b97dc48f978cd05e4ee673aaf085c`.  
Dormant V3 workflow blob: `ccf8f50c28c49fce097f66e53bafb5bc7c7cc45c`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-pilot-real-v3.yml`.

The request is not authorization. `TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json` and `TINY_FIT_PILOT_REAL_LAUNCH_V3.json` do not exist.

The V3 workflow can trigger only on a future V3 launch document and remains capped at the same four P1 captures, 200 frames/example, at most 200 optimizer steps, one candidate, zero retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Require new explicit user authorization of the exact V3 request before any further P1 media access or real optimizer step.**

## V3 pre-launch guard repair

A final pre-launch verification found an impossible self-reference in the dormant V3 workflow: it required `TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json` to contain the Git blob SHA of itself before that blob could exist.

This was caught **before** creating a V3 authorization artifact, launch artifact, accessing any further P1 media, or executing any real optimizer step.

Repair: the future launch artifact must pin the authorization blob; the authorization artifact must pin every pre-existing frozen source but does not self-pin. This changes no capture, crop rule, model, objective, threshold, optimizer budget, P2/P3 boundary, or retry policy.

The user's chat authorization immediately preceding this discovery was **not consumed** because the exact frozen request was found invalid before authorization materialization. The repaired request must be explicitly authorized again before a V3 authorization or launch artifact is created.

## Repaired V3 capped P1 retry — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired V3 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V3.json`
- `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V3.json`

Authorization commit: `cb9916e409bd0fbb9790f592c02ba484619ab548`.  
Launch commit: `70e0cdb2440357dbcb61005b8a5ca1b49ff32329`.  
Canonical V3 workflow run: **36280547470**, job **108511412597**.

Scope remains exactly frozen: four specified P1 training performances, one view each, 200 frames/example, at most 200 optimizer steps total, 2700-second train/eval cap, 3600-second job cap, one candidate, zero automatic retries, zero paid compute. P2/P3 remain closed; full training remains stopped.

**Do not create another V3 launch, rerun this workflow, extend optimizer steps, retune thresholds, open P2/P3, or restart full training without new explicit authorization.**

Next action: inspect only run **36280547470**. If it fails before/during optimizer work, preserve and diagnose that single run only. If it completes training, preserve exact metrics/evidence and stop; no cross-performer screen or broader training is authorized.

## V3 capped P1 result — WORKFLOW GREEN, ENGINEERING GATE NOT MET

Canonical run **36280547470**, job **108511412597**, launch head `70e0cdb2440357dbcb61005b8a5ca1b49ff32329`: **GitHub Actions SUCCESS**.

All four P1 examples prepared successfully with zero unresolved selected-crop labels. The one authorized candidate completed exactly **200 optimizer steps** and stopped at `requested_steps_reached`.

Fit evidence:
- total loss: **5.8937435 -> 0.0399992**
- state loss: **3.0180442 -> 0.0124796**
- onset loss: **0.7189248 -> 0.0068799**

Engineering screen:
- recall on every example: **1.0**
- repeated-attack recall: **1.0**
- matched offsets within 50 ms: **0.9375** (passes 0.90)
- unresolved selected-crop labels: **0**
- minimum per-example event F1: **0.50** (fails required 0.95)
- `engineeringAdvancementThresholdsMet=false`

Per-example F1:
- Drop3_7 chord: **0.705882**
- Ab scale: **0.941176**
- allsinglenotes: **0.50**
- PalmMute: **0.666667**

Totals: **16 references, 25 predictions, 16 true positives, 9 false positives, 0 false negatives**. This is a precision/extra-attack failure, not a recall failure.

### Boundary scoring mismatch

The preparation contract retains carry-out attacks as positive onset targets but excludes carry-out events from `scorableEvents`. The evaluator decodes all model events and scores them only against `scorableEvents`.

These four crops contain **7 carry-out positive target attacks**. `onsetAdmissionRecall=1.0` on every example. Therefore boundary scoring explains **7 of the 9 observed false positives** under the current evaluator; **2 non-boundary extra attacks remain**.

This does not convert the pilot into a pass: even boundary-adjusted diagnostic accounting still leaves the minimum example below the frozen 0.95 F1 gate. No thresholds were retuned and no rerun occurred.

Frozen result: `docs/astra/TINY_FIT_PILOT_REAL_RESULT_V3.json`.  
Actions artifact: **10918434248**, digest `sha256:4b62ad7336a216cbee0bf8a52c3c9c56d51eca7f963702c95bba7be320a7c573`.  
Result JSON SHA-256: `1bda3d5b7c790641742a99c07685c8d477938cd7426ad48f58d84928a3328647`.  
Model SHA-256: `fba076f8b6e5fe177ba7b15e5d6780269194f530b2648037ac0763a4937eb67f`.

**Stop here.** Do not rerun V3, add optimizer steps, retune thresholds, open P2/P3, start a cross-performer screen, or restart full training. Cheapest next work: repair the evaluator boundary contract offline and design a zero-optimizer diagnostic that records decoded prediction events. Any new P1 media access or optimizer work requires fresh explicit authorization.

## V3 zero-optimizer boundary diagnostic — AUTHORIZED, PRE-LAUNCH

User instruction: **"Run the diagnostic."**

Authorized scope only:
- reprepare the same four frozen P1 crops;
- load the exact frozen V3 200-step model artifact;
- execute inference/scoring only, **0 optimizer steps**;
- reproduce the raw V3 score exactly;
- rescore with whole-event carry-in/carry-out boundary exclusions through the existing Event-v2 exclusion contract;
- record each remaining unmatched prediction with decoder probabilities and target/reference context.

No threshold retuning, model mutation, P2/P3, cross-performer screen, automatic retry, or full training is authorized.

Design: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_DESIGN_V1.json`.  
Authorization: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V1.json`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-v3-diagnostic.yml`.

The diagnostic workflow remains inert until exactly one `docs/astra/TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V1.json` is committed after tests/source pins are verified.

## V3 zero-optimizer boundary diagnostic — LAUNCHED ONCE

User authorized this diagnostic by instructing **"Run the diagnostic."**

Launch commit: `f581e98c0999ca9e4ef4ece2cea103df462b3800`.  
Canonical diagnostic run: **36281561748**.

Authorized execution remains:
- same four frozen P1 examples;
- exact frozen V3 model artifact from run 36280547470;
- **0 optimizer steps**;
- no threshold retuning or model mutation;
- no P2/P3;
- no automatic retry;
- no full training or cross-performer screen.

**Do not create another diagnostic launch or rerun this workflow.** Inspect run **36281561748** only. On completion, freeze the diagnostic JSON and exact remaining false-positive event evidence.

## V3 zero-optimizer diagnostic V1 — EVALUATOR INSTRUMENTATION FAILURE

Run **36281561748**, job **108514239716** failed inside the diagnostic evaluator after:
- authorization/source-pin verification: PASS;
- exact frozen V3 artifact download/hash verification: PASS;
- same four P1 examples re-prepared: PASS;
- optimizer steps executed: **0**.

Failure:
`ValueError: events require unique nonempty IDs`

Root cause is a Python module-identity mismatch, not duplicate IDs: `tiny_fit_pilot_v1.py` creates events using `evaluation.event_contract_v2.Event`, while the diagnostic imported the same source file as top-level `event_contract_v2.Event`. Those are different Python class objects, so `validate_events()` rejected valid decoder events at its `isinstance` check.

Offline repair: use the canonical `evaluation.event_contract_v2` namespace in the diagnostic and add a regression that sends actual `decode_event_list()` events through `detailed_score()`.

Frozen failure receipt: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_FAILURE_V1.json`.

**Do not rerun diagnostic V1.** The original diagnostic authorization specified zero automatic retries. After backend tests pass, prepare a new request-only V2 diagnostic gate; a second diagnostic run requires new explicit authorization.

## Repaired zero-optimizer diagnostic V2 — REQUEST ONLY

Namespace-repair commit: `cdf874c3d3a6c2429441c9f23605bafe407e4026`.  
Verification run **36281862601**: **SUCCESS** for complete backend and focused evaluation suites.

The repair changes only Python import identity: the diagnostic now uses canonical `evaluation.event_contract_v2.Event`, matching `tiny_fit_pilot_v1.py`. A regression sends actual `decode_event_list()` events through the diagnostic scorer and passes.

Request: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_REQUEST_V2.json`.  
Dormant retry workflow: `.github/workflows/astra-tiny-fit-v3-diagnostic-v2.yml`.

No V2 diagnostic authorization or launch exists. The retry remains **0 optimizer steps**, same four P1 crops, exact frozen V3 model, unchanged thresholds, no P2/P3.

**Require new explicit user authorization before creating `TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V2.json` or `TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V2.json`.**

## Repaired zero-optimizer diagnostic V2 — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired diagnostic V2 in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_V3_DIAGNOSTIC_AUTHORIZATION_V2.json`
- `docs/astra/TINY_FIT_V3_DIAGNOSTIC_LAUNCH_V2.json`

Authorization commit: `b8b85ea8e1948e8693efc15f441c4a973c9f4d50`.  
Launch commit: `a1b84b8a572678eae6d6c77af1fc0aaa4e19d0bc`.  
Canonical diagnostic V2 run: **36282028911**.

Scope remains:
- exact frozen V3 model and result artifact;
- same four P1 crops;
- **0 optimizer steps**;
- unchanged thresholds/model weights;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another V2 diagnostic launch or rerun this workflow without new explicit authorization.** Inspect only run **36282028911**. If it completes, freeze the exact boundary-corrected metrics and remaining unmatched prediction events. If it fails, preserve and diagnose that run only.

## Repaired zero-optimizer diagnostic V2 — GREEN

Canonical run **36282028911**, job **108515568798**: **SUCCESS**.

Execution boundary:
- exact frozen V3 model loaded and hash-verified;
- same four P1 crops re-prepared;
- optimizer steps: **0**;
- thresholds/model weights/crop selection: **unchanged**;
- P2/P3: **not opened**.

Raw V3 accounting reproduced exactly: **16 references, 25 predictions, 16 TP, 9 FP, 0 FN**.

Boundary-corrected accounting:
- references: **16**
- predictions: **17**
- true positives: **16**
- false positives: **1**
- false negatives: **0**
- minimum per-example F1: **0.9230769231**
- matched offsets within 50 ms: **0.9375**
- frozen 0.95 per-example F1 gate: **still not met**

Per-example boundary-corrected F1:
- PalmMute: **1.0**
- allsinglenotes: **1.0**
- Drop3_7: **0.9230769231**
- Ab scale: **1.0**

The boundary correction excludes **8 of the 9** raw false positives, confirming the V3 evaluator was substantially contaminated by carry-in/carry-out scoring.

### One genuine remaining false positive

Only one unmatched prediction remains, on `P1|chords|Drop3_7|directinput`:

- prediction ID: `diag:2:s1:2`
- string index: **1 (A string)**
- fret: **0**
- predicted onset: **0.2321995465 s**
- nearest true same-string/same-fret onset: **0.2058412698 s**
- onset delta: **+0.0263582766 s**
- the true reference remains active until **0.2370912698 s**
- target state at predicted onset: **fret 0 active**
- target onset at predicted onset: **0**
- onset probability: **0.5066716671**
- frozen onset threshold: **0.5**
- margin over threshold: only **0.0066716671**
- active probability: **0.7487640977**
- silence probability: **0.2512359321**

Classification: **same-string/same-fret duplicate reattack inside a still-active true note**. This is not a wrong-note error and not a recall error. The decoder split a held note because a borderline onset score barely crossed 0.5.

Frozen result: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_RESULT_V2.json`.  
Diagnostic artifact: **10918344868**, digest `sha256:7010e18f691153be935541898fdaf916f15ea7a592f25b3d3885340f577cd4ad`.  
Diagnostic JSON SHA-256: `c960a86f9f2847656598afb1ed790161bccca5bfe7700dfffc28027ac340842d`.

**Stop here.** Do not retrain, retune thresholds, rerun the diagnostic, open P2/P3, or start a cross-performer screen without new explicit authorization.

Cheapest next question: design an offline decoder-contract test for a short refractory/event-identity rule that suppresses this within-note duplicate reattack while preserving true same-fret repeated attacks. This should be tested first on synthetic and frozen-logit evidence with **0 optimizer steps**.

## V3 zero-optimizer diagnostic V2 — GREEN

Canonical run **36282028911**, job **108515568798**: **SUCCESS**.

Execution boundary:
- optimizer steps: **0**;
- thresholds changed: **no**;
- model weights changed: **no**;
- same four P1 crops reproduced: **yes**;
- P2/P3: **not opened**.

Raw V3 totals reproduced exactly: **16 references, 25 predictions, 16 TP, 9 FP, 0 FN**.

With whole-event carry-in/carry-out exclusions passed through the existing Event-v2 scoring contract:
- corrected totals: **16 references, 17 predictions, 16 TP, 1 FP, 0 FN**;
- matched offsets within 50 ms: **0.9375**;
- corrected minimum per-example F1: **0.923077**.

Corrected F1:
- PalmMute: **1.0**
- allsinglenotes: **1.0**
- Ab scale: **1.0**
- Drop3_7: **0.923077**

The boundary mismatch therefore explains **8 of the original 9 false positives**.

### Only remaining false positive

Capture: `P1|chords|Drop3_7|directinput`  
String: A (string index 1)  
Fret: 0  
Predicted onset: **0.23220 s**  
Nearest real same-string/fret onset: **0.20584 s**  
Delta: **+26.36 ms**

At the false onset frame:
- onset probability: **0.506672**
- frozen onset threshold: **0.50**
- margin above threshold: **+0.006672**
- active-state probability: **0.748764**
- target state: active fret 0
- target onset: **0**

This is a **near-threshold duplicate onset while the correct note state remains active**, not a wrong-note/state prediction.

Frozen diagnostic result: `docs/astra/TINY_FIT_V3_DIAGNOSTIC_RESULT_V2.json`.  
Artifact: **10918344868**, digest `sha256:7010e18f691153be935541898fdaf916f15ea7a592f25b3d3885340f577cd4ad`.

The corrected result still does **not** meet the frozen 0.95 per-example F1 gate because Drop3_7 remains at 0.923077. No threshold retuning is permitted retroactively.

**Next cheapest step:** offline analysis of duplicate-onset suppression / onset-separation semantics around this single event. Do not retrain, retune thresholds, open P2/P3, or start a cross-performer screen yet.

## Offline decoder V2 candidate — same-fret onset rising-edge gate

Frozen diagnostic V2 isolated one remaining false positive: A string, fret 0, in Drop3_7. The real source onset maps to target frame **9**; the false predicted reattack starts at frame **10**, exactly one 23.22 ms frame later. The false frame has target onset 0 and onset probability **0.506672**, only **0.006672** above the frozen 0.50 threshold.

Frozen V3 metadata contains two genuine scorable same-string/same-fret reattacks:
- Ab scale high-e fret 4: target frames 9 -> 30 (**21 frames / 487.6 ms grid spacing**);
- Drop3_7 A-string open: target frames 9 -> 185 (**176 frames / 4.0867 s grid spacing**).

Candidate `astra_backend/evaluation/event_decoder_v2.py` leaves both frozen thresholds at 0.50 but changes same-fret reattack semantics: while the same fret remains active, a reattack requires a **fresh below->above onset-threshold crossing**. Consecutive suprathreshold onset frames therefore remain one attack. Different-fret admitted onsets and state-change-without-onset behavior remain unchanged.

Synthetic regressions cover:
- consecutive same-fret onset plateau => one attack;
- separated fresh same-fret threshold crossing => two attacks;
- different-fret onset during an onset plateau => preserved;
- fret change without onset => still no invented attack.

Analysis receipt: `docs/astra/V3_REATTACK_DECODER_ANALYSIS_V1.json`.

This is offline evidence only. **No P1 media has been newly accessed for this decoder candidate, no optimizer step has run, and no threshold has been retuned.** After tests pass, the next permissible action is only to freeze a request for one zero-optimizer P1 re-decode with decoder V2; that real-data check requires new explicit authorization.

## Decoder V2 zero-optimizer P1 re-decode — REQUEST ONLY

Decoder V2 candidate commit `a7ce312ffb51037d5f9d978c676f721b69d1fd6f` passed complete backend and focused evaluation suites in run **36283349847**.

A dormant real-P1 check is staged to answer one narrow question: does the rising-edge same-fret decoder remove the single residual Drop3_7 false onset while preserving all true attacks, repeated-attack recall, offset quality, and silence behavior?

The check uses:
- exact frozen V3 model and hashes;
- exact same four P1 crops;
- boundary-corrected Event-v2 scoring;
- state threshold **0.50** and onset threshold **0.50** unchanged;
- **0 optimizer steps**;
- decoder V1 corrected metrics must reproduce diagnostic V2 before decoder V2 is interpreted.

Request: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_REQUEST_V1.json`.  
Design: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_DESIGN_V1.json`.  
Dormant workflow: `.github/workflows/astra-tiny-fit-v3-decoder-v2-check.yml`.

No authorization or launch file exists. **Fresh explicit authorization is required before any new P1 media access.** A pass would remain training-example evidence only and would not authorize P2/P3, cross-performer screening, or full training.

## Decoder V2 zero-optimizer P1 check — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the frozen decoder V2 request in chat on 2026-09-26.

Created:
- `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_V1.json`
- `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_LAUNCH_V1.json`

Authorization commit: `d3c9382782d9128b3f14bd92043e468b402e81a4`.  
Launch commit: `e45bc98ca9e7fbc38865987792ddff6aacabd137`.  
Canonical decoder V2 check run: **36283779556**, job **108520534718**.

Authorized scope remains:
- exact frozen V3 model and hashes;
- same four frozen P1 examples;
- decoder V2 rising-edge same-fret semantics;
- state threshold 0.50 and onset threshold 0.50 unchanged;
- **0 optimizer steps**;
- no threshold retuning;
- no model mutation;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another decoder V2 launch or rerun this workflow.** Inspect run **36283779556** only. On completion, freeze the exact V1 reproduction, decoder V2 metrics, remaining FP/FN evidence, repeated-attack recall, offset fraction, and engineering training-only gate. A pass does not establish generalization.

## Decoder V2 zero-optimizer P1 check V1 — FEATURE-BYTE IDENTITY FAILURE

Run **36283779556**, job **108520534718** passed authorization/source pins, frozen V3 artifact hashes, and preparation of all four exact P1 crops. It executed **0 optimizer steps** and failed before decoder V2 could be interpreted.

Failure:
`RuntimeError: prepared examples differ from frozen V3 target set`

All crop selections and target hashes reproduced exactly, but all four CQT feature byte hashes differed from the frozen V3 hashes. The successful diagnostic V2 and this failed check used the same Ubuntu runner image and pinned Python/NumPy/SciPy/librosa/Torch versions, so feature SHA byte equality is not a reliable semantic invariant for the hosted preprocessing path.

Repair: feature SHA remains recorded provenance, but the gate now requires exact non-feature source/crop/target identity and then requires decoder V1's boundary-corrected totals and minimum F1 to reproduce frozen diagnostic V2 exactly before decoder V2 may be interpreted.

Frozen failure: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_FAILURE_V1.json`.

No retry is authorized. After tests pass, freeze a new request-only repaired decoder V2 check.

## Repaired decoder V2 zero-optimizer P1 check retry V2 — REQUEST ONLY

Check V1 run **36283779556** stopped before decoder V2 interpretation because all four re-prepared CQT feature byte hashes differed from frozen V3, despite exact crop/target reproduction and the same runner image/pinned software. It executed **0 optimizer steps**.

Repair:
- feature SHA is retained as provenance, not semantic equality;
- exact non-feature source/crop/target identity is still required;
- decoder V1 boundary-corrected totals must reproduce diagnostic V2 exactly;
- decoder V1 boundary-corrected minimum F1 must reproduce diagnostic V2 exactly;
- only after those semantic guards pass may decoder V2 be interpreted.

Repair code run **36284377888**: SUCCESS.  
Regression/test run **36284381574**: SUCCESS.

Frozen V1 failure: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_FAILURE_V1.json`.  
Retry V2 request: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_AUTHORIZATION_REQUEST_V2.json`.  
Dormant retry workflow: `.github/workflows/astra-tiny-fit-v3-decoder-v2-check-v2.yml`.

No V2 authorization or launch exists. **Fresh explicit authorization is required before any new P1 media access or inference.** Scope remains exact frozen V3 model, same four P1 crops, decoder V2, unchanged 0.50/0.50 thresholds, 0 optimizer steps, no P2/P3, no automatic retry.

## Repaired decoder V2 zero-optimizer P1 check retry V2 — AUTHORIZED AND LAUNCHED ONCE

User explicitly authorized the repaired retry request in chat on 2026-09-26.

Authorization commit: `99b7dc85c7737d7ba4c59e8680a7f9e80aea22e6`.  
Launch commit: `5c9e9eb00cc777ee1ef81ca88d31e3b6f0982237`.  
Canonical retry V2 run: **36284602349**.

Authorized scope remains:
- exact frozen V3 model and artifact hashes;
- same four frozen P1 examples;
- decoder V2 rising-edge same-fret semantics;
- decoder V1 boundary-corrected semantic metrics must reproduce before decoder V2 is interpreted;
- state/onset thresholds remain 0.50 / 0.50;
- **0 optimizer steps**;
- no model mutation;
- no P2/P3;
- zero automatic retries;
- no cross-performer screen or full training.

**Do not create another retry V2 launch or rerun this workflow.** Inspect run **36284602349** only.

## Decoder V2 zero-optimizer P1 check retry V2 — GREEN, TRAINING-ONLY GATE MET

Canonical run **36284602349**, job **108522850285**: **SUCCESS**.

The repaired semantic guard passed before decoder V2 interpretation:
- decoder V1 boundary-corrected totals reproduced exactly: **16 references, 17 predictions, 16 TP, 1 FP, 0 FN**;
- decoder V1 corrected minimum per-example F1 reproduced exactly: **0.9230769231**.

Decoder V2 then produced:
- **16 references, 16 predictions, 16 TP, 0 FP, 0 FN**;
- PalmMute F1: **1.0**;
- allsinglenotes F1: **1.0**;
- Drop3_7 F1: **1.0**;
- Ab scale F1: **1.0**;
- minimum per-example F1: **1.0**;
- matched offsets within 50 ms: **0.9375**;
- repeated reference attacks: **2**;
- repeated-attack recall: **1.0**;
- synthetic silence false positives: **0**;
- unresolved labels: **0**;
- `engineeringTrainingOnlyGateMet=true`.

Decoder V2 uses the same frozen 0.50 state/onset thresholds and the same frozen V3 model weights. It executed **0 optimizer steps**. The only decoder semantic change is same-fret reattack admission requiring a fresh below->above onset-threshold crossing while the same fret remains active.

Frozen result: `docs/astra/TINY_FIT_V3_DECODER_V2_CHECK_RESULT_V2.json`.  
Result commit: `2a0de5c7a4ffe86325f9320f47e45fb811244380`.  
Actions artifact: **10919563631**, digest `sha256:099b87369a12cf6117e69199edfac292aee0af14b09746dddd1f118390676446`.  
Result JSON SHA-256: `1d974927660bd41fcb2e2367c172580720a2b72b2b4a6051cb4c786f7ded2c2d`.

### Meaning and hard boundary

This **establishes engineering learnability on the four selected P1 training examples** with decoder V2. It does **not** establish cross-performer generalization, customer readiness, or justify full training by itself.

**Stop here.** No P2/P3 access, cross-performer screen, full training, customer delivery, or additional optimizer work is authorized. The next scientifically meaningful step is a separately designed cross-performer/generalization screen with fresh explicit authorization.

