# Astra — current handoff

Updated: 2026-09-26 UTC  
Branch: `astra-work`  
Status: **OFFLINE EVENT/CROP ADAPTER + CAPPED TINY-FIT PREPARATION VERIFIED; REAL PILOT AWAITING EXPLICIT AUTHORIZATION**  
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

## Current authorization boundary

A reviewable request is frozen at:
`docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V1.json`.

That file is **a request only**. It does not grant authorization. No real authorization document and no launch document exist. Therefore the real workflow is inert.

If the user later explicitly authorizes that exact request, the next chat may create the matching authorization and one launch document. Until then: do not access P1 media, do not execute a real optimizer step, and do not restart full training.

## Advancement rule if the real pilot is later authorized

Training-example explicit-event F1 >= 0.95; matched offsets within 50 ms >= 0.90; repeated-attack coverage must be present and recall >= 0.90; all metrics finite; zero unresolved selected-crop labels.

Passing is only an engineering learnability screen. It does not prove generalization and does not authorize full training, P2/P3, production use or customer delivery. Failure stops the candidate; no extra epochs, retries, threshold rescue or second architecture are automatic.

## Verification notes

The earlier workflow-definition failures at runs created before the UTF-8 workflow repair are configuration-only and are not pilot evidence. The repaired synthetic run above is the canonical verification.

Normal `Astra backend tests` also passed on the design-trigger commit. Historical V1–V5 results and Event-v2 evidence remain unchanged.

## Preserved history

The pre-pilot history remains at `docs/checkpoints/archive/CURRENT_STATE_2026_09_26_PRE_PILOT.md` (original Git blob `1ae91540ac02133a4a1c63989350ad615f065954`). Consult specific sections only when needed.
