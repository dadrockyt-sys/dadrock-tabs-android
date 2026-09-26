# Astra — current handoff

Updated: 2026-09-26 UTC  
Branch: `astra-work`  
Status: **V2 CAPPED P1 RETRY AUTHORIZED AND LAUNCHED ONCE; RUN 36277631151 IN PROGRESS; NO SECOND V2 LAUNCH/RERUN AUTHORIZED**  
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

