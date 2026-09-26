# Next chat: start here

Repository: `dadrockyt-sys/dadrock-tabs-android`, branch `astra-work`.  
Canonical status: `docs/checkpoints/CURRENT_STATE.md`.

## Current state

Offline adapter and capped tiny-fit preparation are complete and exact-runtime synthetic verification passed. **Do not restart full training. Do not rerun V5 diagnosis. Do not open P2 or P3.**

Canonical exact-runtime evidence:
- receipt: `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V1.json`
- GitHub run: **36275788105**
- job: **108498148554**
- verified head: `2975017d9632f75a9e24e4eb5d8e3b2ae0546468`
- runtime: Python 3.10.15 / NumPy 1.21.6 / Torch 1.11.0+cpu
- real optimizer steps: **0**
- P1/P2/P3 media accessed: **none**

## Frozen pilot

Read:
1. `docs/astra/TINY_FIT_PILOT_DESIGN_V1.json`
2. `docs/astra/TINY_FIT_PILOT_SYNTHETIC_VERIFICATION_V1.json`
3. `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V1.json`
4. `astra_backend/evaluation/prepared_event_adapter_v1.py`
5. `astra_backend/tiny_fit_pilot_v1.py`

Exact capture keys are:
- `P1|chords|Drop3_7|directinput`
- `P1|scales|Ab|directinput`
- `P1|singlenotes|allsinglenotes|directinput`
- `P1|techniques|PalmMute|directinput`

Caps are four underlying P1 performances, one view each, 200 frames/example, 200 optimizer steps total, 2700 seconds train/eval inside a 60-minute CPU job, one candidate, zero automatic retries, zero paid compute.

## Exact next gate

There is **no active real-data authorization**.

If the user explicitly authorizes the exact request in `TINY_FIT_PILOT_REAL_AUTHORIZATION_REQUEST_V1.json`, then:
1. create `docs/astra/TINY_FIT_PILOT_REAL_AUTHORIZATION_V1.json` matching the request exactly;
2. verify every frozen Git blob and receipt identity;
3. create one source-pinned `docs/astra/TINY_FIT_PILOT_REAL_LAUNCH_V1.json`;
4. allow the dormant workflow `.github/workflows/astra-tiny-fit-pilot-real.yml` to run once;
5. inspect and preserve the bounded result.

Without that explicit authorization, stop here. Do not access P1 archives or execute a real optimizer step.

## After a future real pilot

If it fails: preserve evidence and diagnose inputs/targets/objective. Do not automatically add steps, rerun, alter thresholds or invent V6.

If it passes the already frozen training-only thresholds: design a **separate same-budget cross-performer screen**. Passing does not authorize full training, P3, production or customer delivery.

## Important implementation facts

- Explicit source attack IDs are preserved through crop/mask preparation.
- Carry-in occupancy cannot create a crop-edge onset.
- Source onsets are separate from state occupancy.
- Same-fret reattacks are representable by the decoder.
- Unsupported frets, overlaps, negative aligned time, sub-frame attacks and frame-grid collisions are explicit unresolved labels, never silent repairs.
- The future source extractor opens only selected MIDI/audio members after a pinned archive hash is verified.
- The real workflow has no manual-dispatch trigger and no P2/P3 source path.
