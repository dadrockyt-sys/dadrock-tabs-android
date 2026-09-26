# Event-preserving measurement — implementation handoff

Status: offline primitives implemented; real-corpus integration and prevalence audit pending.

## Run the focused checks

```sh
python -m unittest discover -s astra_backend/evaluation -p 'test_event_contract_v2.py' -v
```

Python standard library only. This command opens no corpus, loads no model and performs no optimizer steps. Local verification: Python 3.12.14, 26 passed. Python 3.10 CI also passed: run 36273580660, job 108491956218, implementation commit 7d6e8e894b9a8ff9b09128ca936433a97753de58.

## What changed

- `event_contract_v2.py` accepts explicit events with independent attack IDs, string, fret, start and end seconds. Adjacent same-fret attacks stay distinct.
- `from_string_notes` adapts the tuple dictionary emitted by the existing `midi_string_events`, using the existing positive-lag convention. It does not import the legacy trainer or read a MIDI file.
- `frame_targets` returns state, onset and event-ID arrays. An onset comes from source events, never merely a change of fret state.
- `score_events` uses one-to-one maximum-count/minimum-onset-error matching within exact string/fret groups. Offset error is reported separately. Perfect onset F1 is not proof of correct duration.
- Masks are explicit, preregistered exclusion intervals. Intersecting events are excluded whole on both sides and counted; clipping never creates a false attack at a mask edge.
- `delivery_counts` calculates abstention from actual request statuses; an empty note list is not automatically an abstention. Event scoring reports unknown abstention as null.
- `diagnostic_histogram_v2.py` provides increasing-recall PR integration and separately named trapezoidal PR area and step average precision. Histogram ties enter together. Undefined single-class metrics remain null.

## Boundaries that must remain explicit

1. This is a NEW diagnostic schema. The frozen V1–V5 label/scoring functions and outcomes remain unchanged. Do not compare its score to legacy F1 as though denominators were identical.
2. A tied note is one attack with an extended end. The adapter does not infer ties from sound or merge neighboring source notes.
3. Same-string overlap, out-of-range fret, negative aligned time and sub-frame attacks fail explicitly. Do not silently delete these cases to improve scores. Count them and freeze a documented resolution policy before corpus integration.
4. The helper requires full event coverage; there is no implicit crop/window clipping. A future crop adapter must distinguish carry-in notes from new onsets, preserve absolute source IDs, and report boundary exclusions.
5. Frame targets currently accept resolved, unmasked source events. Training masks and MIDI parsing provenance are future adapter work. Scoring exclusions are implemented, not a complete corpus mask adapter.
6. IDs are capture/string/source-index scoped. Freeze source ordering and hashes in the prepared manifest. Source IDs/labels remain private under the existing corpus rules.
7. No change to frozen alignment offsets, accepted capture population or historical thresholds.
8. Small-clip matching stores paths in dynamic programming; profile before applying to full songs.
9. The histogram helper is verified but not wired into the frozen V5 diagnostic runner. Use it in a new diagnostic revision; keep the old runner hash and negative-AUPRC exclusion intact. Existing raw report does not emit histogram bins, so do not invent corrected historical AUPRC from summary fields.

## Next implementation, in order

1. Build a private prepared-event adapter from the existing MIDI parser output plus the exact alignment allowlist. Test on fabricated MIDI/event fixtures, not real P1/P2 files. Record source hashes and excluded/ambiguous events explicitly. Resolve crop carry-in and mask semantics synthetically.
2. Add a training-only tiny-fit harness using explicit onset targets and an event-list decoder capable of emitting same-fret reattacks. A state-only decoder cannot satisfy this contract.
3. The harness must emit losses per head, event counts, onset admission recall, onset/offset metrics, wall time, steps and target/event hashes. Save stopped/failed results too.
4. Freeze the candidate initialization, loss, decoder, example selection and exact limits in the pilot proposal. Verify synthetic forward/backward and cap enforcement under the frozen runtime.
5. Only then prepare a concrete authorization request. Do not automatically dispatch real training from this measurement milestone.
