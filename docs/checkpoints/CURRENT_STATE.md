# Astra — current handoff

Updated: 2026-09-26 UTC
Branch: `astra-work`
Status: **OFFLINE EVENT-CONTRACT FOUNDATION VERIFIED; TINY-FIT PILOT PROPOSED, NOT LAUNCH-READY**
Next-chat guide: `docs/astra/NEXT_CHAT.md`

## Product and current priority

Jimmy PAIge for DadRock Tabs: audio upload -> selected bass/rhythm/lead -> accurate playable preview -> optional full professional PDF. The frontend and deterministic backend remain useful; musical correctness is the bottleneck.

Before more full training: preserve actual note attacks in labels/scoring, prove a model can fit a few training examples, then test generalization with staged budgets.

## Completed this handoff

- Reviewed this week's V1–V5 evidence and training/diagnostic/scoring source.
- Legacy development macro F1: V1 ~0.2136; V2 0.216208; V3 0.237452; V4 0.243523; V5 0.064131. All remain FAIL.
- V5 hard onset gate rejects ~91–98% of true starts. Existing zero-optimizer state-only ablation recovers 0.218843, still below V4. Do not repeat the completed diagnosis.
- Reproduced an independent scoring/target issue: two adjacent same-string/same-fret attacks collapse into one occupancy run. Frequency in real recordings is unknown.
- Added `astra_backend/evaluation/event_contract_v2.py`: explicit event IDs, tuple-source adapter with frozen-lag semantics, separate occupancy/onset targets, one-to-one event scoring, offset reporting, explicit uncertainty exclusions and status-based abstention counts.
- Added `diagnostic_histogram_v2.py`: corrected increasing-recall integration, explicit trapezoidal PR vs average precision, single-class null results.
- Added `test_event_contract_v2.py`: **26 passed on Python 3.12.14**, no external dependencies, real media, models or optimizer steps.
- Added a five-minute Python 3.10 synthetic-only workflow. Run `36273580660`, job `108491956218`: **SUCCESS** on implementation commit `7d6e8e894b9a8ff9b09128ca936433a97753de58`. This verifies the stdlib helpers on Python 3.10, not the frozen ML training stack.
- Prepared `docs/astra/TINY_FIT_PILOT_PROPOSAL_V1.json`: a proposal with explicit launch blockers, not authorization.
- Inventoried V5 saved artifacts; final model artifacts expire October 2–3 UTC. Inventory is not a durable model backup.

## Read these next

1. `AGENTS.md`
2. `docs/astra/NEXT_CHAT.md`
3. `docs/astra/EVENT_CONTRACT_V2.md`
4. `docs/astra/TINY_FIT_PILOT_PROPOSAL_V1.json`

## Exact next implementation

1. Implement the private prepared-event/crop/mask adapter using fabricated MIDI/event fixtures. Preserve original source attacks, lag/allowlist identity, carry-in notes and explicit exclusions. Do not silently discard overlaps, unsupported frets or sub-frame events.
2. Implement ONE tiny training-only fitting harness with event-preserving onset supervision and an event-list decoder that can emit same-fret reattacks. Freeze model/loss/decoder/initialization before real execution.
3. Add per-head losses, event counts, onset admission recall, offset metrics, elapsed time, optimizer steps, source/event hashes and stop reasons. Verify gradients and budget enforcement synthetically under the frozen ML runtime.
4. Freeze metadata-only selection and exact source/manifest identities. The proposal suggests four P1 training performances, one view each, 200 frames each, random initialization, 200 optimizer steps total and 45 minutes training/evaluation within a 60-minute CPU job. No automatic retry or full-run extension.
5. When implementation and evidence are concrete, request the specifically scoped real-data pilot authorization. Do not request another full V6 run by default.
6. If the pilot later fails, diagnose inputs/targets/objective; if it passes, design a same-budget cross-performer screen. Neither outcome is customer acceptance.

## Important evidence limits

- Event-v2 is a separate diagnostic protocol. Historical scores/thresholds/FAIL decisions are unchanged.
- The new helper is not integrated into real training, production, or the frozen V5 diagnostic runner. Negative historical AUPRC remains invalid; no corrected real AUPRC has been measured.
- Scoring masks are implemented; a complete training crop/mask adapter is not.
- Source MIDI ties must arrive as one extended attack; the adapter cannot infer them from occupancy.
- 78–86% V5 pitch-head F1 is frame/pitch-bin performance, not tab/event quality.
- Legacy abstentionRate was hardcoded zero; actual abstention is unknown.
- These guitar experiments do not establish bass, full-mix separation, lead/rhythm distinction or professional full-song quality.

## Verify only what changed

```sh
python -m unittest discover -s astra_backend/evaluation -p 'test_event_contract_v2.py' -v
```

Verification receipt: `docs/astra/EVENT_CONTRACT_V2_VERIFICATION.json`.
Local work was staged separately from a stale checkout with unrelated unfinished changes; those changes were preserved.

## Authorization and saving

Ordinary reversible offline implementation and synthetic checks are authorized. Existing freezes require explicit authorization for new real P1/P2 optimizer work after the pilot is concrete. P3 stays sealed. No paid compute, published-checkpoint initialization, threshold rescue, main/Production mutation or customer delivery is authorized here.

Commit code/tests/status together to astra-work and verify the remote. Keep this handoff short; put detailed completed evidence in receipts. Do not treat historical task queues as active.

## Preserved history

The complete pre-compaction checkpoint is stored unchanged at:
`docs/checkpoints/archive/CURRENT_STATE_2026_09_26_PRE_PILOT.md`
Original Git blob: `1ae91540ac02133a4a1c63989350ad615f065954`.

It contains original sources, authorization receipts, five training results, diagnoses and the full September 26 review. Consult specific sections when needed; do not reread the entire archive on each turn.

