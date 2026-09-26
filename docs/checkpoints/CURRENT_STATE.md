# Astra — current handoff

Updated: 2026-09-26 UTC
Branch: `astra-work`
Status: **OFFLINE EVENT/CROP ADAPTER + CAPPED TINY-FIT IMPLEMENTED; EXACT-RUNTIME SYNTHETIC VERIFICATION PENDING; REAL PILOT NOT AUTHORIZED**
Next-chat guide: `docs/astra/NEXT_CHAT.md`

## Product and current priority

Jimmy PAIge for DadRock Tabs: audio upload -> selected bass/rhythm/lead -> accurate playable preview -> optional full professional PDF. The frontend and deterministic backend remain useful; musical correctness is the bottleneck.

Do not restart full V1–V5-style training. First prove the explicit-event path can fit a tiny bounded set, then decide whether a same-budget cross-performer screen is justified.

## Historical evidence unchanged

- V1–V5 remain FAIL. Legacy development macro F1: V1 ~0.2136; V2 0.216208; V3 0.237452; V4 0.243523; V5 0.064131.
- V5 hard onset admission collapse was already diagnosed; do not repeat it.
- Event-v2 remains a separate diagnostic protocol. Historical thresholds, results and P3 status are unchanged.
- P3 is sealed. No paid compute, production/main mutation, published-checkpoint initialization, threshold rescue or customer delivery is authorized.

## Completed offline implementation

- `astra_backend/evaluation/prepared_event_adapter_v1.py`
  - preserves source attack IDs and frozen lag identity;
  - retains carry-in occupancy without inventing crop-edge attacks;
  - keeps carry-out source attacks but excludes boundary events from event/offset scoring;
  - masks whole events that intersect registered exclusions;
  - reports unsupported frets, same-string overlap, negative aligned time, sub-frame attacks and frame-grid collisions instead of silently repairing/dropping them;
  - reports out-of-crop source issues without letting them veto an unrelated selected crop;
  - freezes source/event/target hashes.
- `astra_backend/tiny_fit_pilot_v1.py`
  - one candidate only: 192->128 ReLU shared encoder, six-string state head and explicit onset head;
  - onset supervision comes from source attack IDs, never state changes;
  - event-list decoder can emit a same-string/same-fret reattack and never invents a fret-change attack without onset admission;
  - random initialization, seed 20260921, Adam lr 0.01;
  - hard code caps: four examples, 200 frames each, 200 optimizer steps total, 2700 s training/eval, one candidate;
  - records per-head losses, event/offset/repeated-attack/onset-admission diagnostics, source hashes, elapsed time and stop reason.
- Exact metadata-only P1 capture selection is frozen:
  1. `P1|chords|Drop3_7|directinput`
  2. `P1|scales|Ab|directinput`
  3. `P1|singlenotes|allsinglenotes|directinput`
  4. `P1|techniques|PalmMute|directinput`
- Training-only crop selection may use source events *after* capture identity is frozen, preferring the earliest 200-frame-capable repeated same-fret pair. This is fitting coverage, not validation/generalization selection.
- ZIP handling is bounded: after future authorization, list the pinned archive and extract exactly one selected MIDI plus one canonical-view audio member. Unrelated P1 media is not extracted.
- `docs/astra/TINY_FIT_PILOT_DESIGN_V1.json` freezes source archives, design, budget, thresholds and guards.
- Fabricated local checks are green: 13 adapter tests + 9 tiny-fit/cap/source-selection tests, plus a 20-step synthetic backward smoke. These local checks are not the frozen-runtime receipt.
- Added `.github/workflows/astra-tiny-fit-pilot-synthetic.yml` for exact Python 3.10.15 / torch 1.11.0+cpu verification with zero real-media access.
- Added dormant `.github/workflows/astra-tiny-fit-pilot-real.yml`. It has no `workflow_dispatch`; it can trigger only from a future separately authorized `TINY_FIT_PILOT_REAL_LAUNCH_V1.json` commit. Its job timeout is 60 minutes and it contains no P2/P3 source path.

## Exact next gate

1. Let the synthetic workflow verify this exact implementation under the frozen ML runtime and preserve its receipt.
2. If and only if that passes, freeze the receipt plus a source-pinned **authorization request**. Do not fabricate authorization.
3. Await a new explicit user authorization for the exact four-P1, 200-step real pilot.
4. Only after that authorization may a launch document be committed. The real workflow then prepares the four selected examples and runs one bounded pilot. It must not automatically retry, extend epochs/steps, open P2/P3 or start full training.

## Pilot advancement rule (already frozen, not yet measured on real data)

Training-example explicit-event F1 >= 0.95; matched offsets within 50 ms >= 0.90; repeated-attack coverage present and recall >= 0.90; finite metrics; zero unresolved selected-crop labels. Passing is only an engineering learnability screen and cannot imply generalization, customer eligibility or permission for full training.

## Verify only what changed

Offline fabricated checks:

```sh
PYTHONPATH=astra_backend:astra_backend/evaluation python -m unittest -v \
  astra_backend.evaluation.test_event_contract_v2 \
  astra_backend.evaluation.test_prepared_event_adapter_v1 \
  astra_backend.evaluation.test_tiny_fit_pilot_v1
PYTHONPATH=astra_backend:astra_backend/evaluation \
  python astra_backend/tiny_fit_pilot_verify_synthetic_v1.py
```

Exact-runtime workflow: `.github/workflows/astra-tiny-fit-pilot-synthetic.yml`.

## Preserved history

The complete pre-pilot history remains unchanged at `docs/checkpoints/archive/CURRENT_STATE_2026_09_26_PRE_PILOT.md` (original Git blob `1ae91540ac02133a4a1c63989350ad615f065954`). Consult specific sections only when needed.
