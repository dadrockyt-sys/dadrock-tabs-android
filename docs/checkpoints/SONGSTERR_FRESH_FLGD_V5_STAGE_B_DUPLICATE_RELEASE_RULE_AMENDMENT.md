# Songsterr Fresh — FLGD V5 Stage B Duplicate-Release Rule Amendment

Status: **FROZEN AFTER STRUCTURAL EDGE AUDIT / BEFORE ANY FLGD CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Evidence that triggered this amendment

The first real Stage B manifest attempt failed closed before producing a report:
- workflow source commit `43b8ed6a15fe1fee792db9a20ed36d6baa08c5a6`;
- run `34719399752`;
- job `103622351601`;
- first failure `MIDI_UNMATCHED_NOTE_OFF:midi/Fp24c.mid:(0, 48):65091`.

The preregistered structural edge audit was then run once on all 79 canonical metadata-named MIDI files at exact FLGD revision `a38306c244b3ea81496ad58b4514622185e58211`:
- audit preregistration: `SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_EDGE_AUDIT_AMENDMENT.md`;
- controlled audit CI run `34719493782`: SUCCESS;
- real audit workflow source commit `77ac002c34555ee35279bbdef2acb2bb1c7c1f56`;
- real audit run `34719520796`;
- real audit job `103622678813`: SUCCESS;
- audit report SHA-256 `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`;
- audit edge-identity SHA-256 `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`.

Observed structural totals:
- note messages: `152808`;
- note-ons: `76392`;
- note-offs: `76416`;
- FIFO matched pairs: `76392`;
- same-key overlaps: `0`;
- unmatched note-ons at EOF: `0`;
- unmatched note-offs: `24` across exactly 7 files;
- every unmatched note-off occurred with no active onset for its channel/MIDI **after** that same channel/MIDI had already had an earlier valid onset/off history;
- every unmatched note-off was classified by the frozen audit as `duplicateReleaseCandidate:true`;
- no audited unmatched note-off was a leading-boundary release candidate.

Files containing the 24 audited unmatched releases:
`midi/Fp24c.mid`, `midi/SM54c.mid`, `midi/YNC4c.mid`, `midi/3H74c.mid`, `midi/hwC4c.mid`, `midi/LDC4c.mid`, `midi/MDC4c.mid`.

No audio was decoded, Basic Pitch/V5/Demucs were not invoked, no estimate/reference matching occurred, and no correctness metric was produced.

## Frozen parser rule

The Stage B parser may now distinguish a structural duplicate release from a fatal unmatched edge using only the canonical MIDI message sequence.

For each exact `(channel, MIDI)` key, process note messages in the already-frozen merged ordering `(tick, trackIndex, eventOrder)` with the already-frozen FIFO active-note queue.

1. A note-on appends to the active FIFO queue.
2. A note-off with an active note pairs to the oldest active onset exactly as before and increments a completed-pair counter for that exact key.
3. A note-off with **no active note** is accepted only when the completed-pair counter for that exact key is already greater than zero. It is classified as a `duplicateReleaseEdge`.
4. A `duplicateReleaseEdge` MUST NOT create a second reference note event and MUST NOT alter any existing paired note identity.
5. Every accepted duplicate-release message MUST remain explicitly represented in the Stage B output with at least its canonical MIDI path/stem, tick, track index, event order, channel, MIDI and velocity. The output must report per-file/global counts and deterministic SHA-256 identity hashes for these edges. Therefore the message is not silently dropped.
6. A note-off with no active onset and no prior completed pair for that exact key remains a fatal `MIDI_UNMATCHED_NOTE_OFF_BEFORE_MATCHED_PAIR` condition.
7. Any active onset remaining at end of file remains a fatal `MIDI_UNMATCHED_NOTE_ON` condition.
8. Existing same-key overlap behavior remains FIFO and unchanged. This amendment does not authorize dropping or rewriting overlapping onsets.

## Dataset binding

The parser remains bound to the exact FLGD origin, revision, metadata identity, 79-row population and Stage A provenance already frozen. `test_set/` and model-output MIDI remain forbidden as reference truth.

This amendment does not authorize post-hoc row exclusion. All 79 metadata rows remain mandatory.

## Validation required before real Stage B retry

Before another real Stage B manifest attempt:
- controlled synthetic CI must prove a valid pair followed by an extra release is preserved as a `duplicateReleaseEdge` while producing only the original paired note event;
- a leading unmatched release must still fail closed;
- a trailing unmatched onset must still fail closed;
- existing tempo/running-status/FIFO/canonical-population/provenance/non-scoring guards must remain green.

Only after that controlled CI is green may the one real Stage B non-scoring manifest be retried on the same exact FLGD revision.

## Explicitly still forbidden

This amendment does not authorize:
- Basic Pitch inference;
- V5 classification;
- audio-sample pitch analysis;
- estimate/reference matching;
- precision/recall/F-score or any correctness metric;
- row selection by observed correctness;
- duration authority changes;
- protected-song execution;
- customer promotion.

Authority remains exactly:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged / duration research paused;
- protected song unused.
