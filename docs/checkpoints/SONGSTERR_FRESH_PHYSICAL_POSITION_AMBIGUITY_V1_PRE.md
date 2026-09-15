# Songsterr Fresh — Physical Position Ambiguity V1 Pre-Implementation Freeze

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `IMPLEMENTATION_AUTHORIZED_NO_MEDIA_MODEL_EXECUTION`

## Problem

The deterministic fretboard core can find more than one physically playable string/fret assignment for the same MIDI event or onset cluster. It currently returns the best-scoring playable shape and exposes `shapeResolved:true`, which can be misread as physical string/fret truth even when multiple assignments are possible.

## Frozen semantics

1. Preserve the existing preferred playable assignment for backward-compatible rendering/UX.
2. Do not reinterpret a heuristic preferred assignment as observed physical string/fret truth.
3. Enumerate/count every valid one-event-per-string assignment for an onset cluster under the existing tuning/capo/max-fret rules.
4. `shapeResolved` remains backward-compatible and means only that a complete playable shape was found.
5. Add `shapeCandidateCount` to every output event in the cluster.
6. Add `physicalShapeResolved`, true only when `shapeCandidateCount === 1`.
7. Add `positionSelectionMethod`:
   - `unique-physical-layout` when exactly one full assignment exists;
   - `heuristic-preferred-layout` when multiple full assignments exist and the existing score/tie-break selects one;
   - `unassigned` when no full playable assignment exists.
8. Keep pitch identity exact and unchanged. Do not change the existing shape score or tie-break.
9. Add metrics separating playable assignment from physical certainty.
10. No model, media, reference tab, expected answer, Songsterr truth, or closed/reserved dataset may participate in this decision.
11. This is deterministic core metadata hardening only; it creates no validation/customer/delivery authority.

## Required tests

- standard guitar MIDI 40 alone: exactly one assignment, physical shape resolved;
- standard guitar MIDI 64 alone: more than one assignment, preferred playable assignment retained, physical shape unresolved;
- a multi-note cluster with multiple full layouts: playable shape resolved but physical shape unresolved;
- exact MIDI remains unchanged in all cases.

Global authorization fields remain false/zero and archived V143/Gomyway remains closed.
