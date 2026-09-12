# Songsterr Fresh — FLGD V5 Stage B MIDI Pairing Amendment

Status: **FROZEN AFTER STRUCTURAL AUDIT / BEFORE ANY CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Evidence requiring amendment

The first real Stage B attempt failed closed on an unmatched note-off before producing a report. A separately preregistered structural-only audit was then run across all 79 canonical metadata-named MIDI files.

Audit identity:
- preregistration: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_EDGE_AUDIT_AMENDMENT.md`
- real audit workflow source `77ac002c34555ee35279bbdef2acb2bb1c7c1f56`
- workflow run `34719520796`
- job `103622678813`
- audit report SHA-256 `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`
- edge identity SHA-256 `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`
- uploaded audit artifact ID `10305342788`
- artifact ZIP digest `3c140423b3e9add74d37d3f6d6b6be0f75efdd3d2c83ecff2e3a0c29e83f9355`.

Structural audit result:
- note messages `152,808`
- note-on messages `76,392`
- note-off messages `76,416`
- valid FIFO matched pairs `76,392`
- unmatched note-offs `24`
- unmatched note-ons `0`
- same-key overlap count `0`
- files with extra note-offs: 7
- every unmatched note-off was observed only after the same `(channel, MIDI)` had both an earlier onset and earlier release; none was a leading boundary release.

No audio samples, Basic Pitch, V5, estimate/reference matching or correctness metric were used.

## Frozen deterministic pairing rule

For each canonical MIDI file, process note messages in deterministic merged order `(absolute tick, track index, event order)`.

For each `(channel, MIDI)` key:
1. note-on with velocity > 0 appends an active onset FIFO;
2. note-off (including note-on velocity zero) with an active onset pops the oldest onset and creates one reference event;
3. note-off with no active onset is allowed **only if that same key has already completed at least one valid onset/off pair earlier in the same file**;
4. such an allowed edge is classified `ignored-duplicate-release` and creates no additional reference event;
5. note-off with no active onset and no earlier completed pair remains a hard failure;
6. any active onset remaining at end-of-file remains a hard failure;
7. overlapping same-key onsets continue to pair FIFO and are counted diagnostically.

This rule is based only on canonical MIDI structure and cannot depend on audio, V5, Basic Pitch, desired correctness, split, guitar type, artist, or validation outcome.

## Audit binding in Stage B output

The amended Stage B tool must record:
- `midiEdgeAuditReportSha256 = 111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`;
- total ignored duplicate releases;
- per-file ignored duplicate release count;
- deterministic ignored-duplicate-release identity SHA-256.

Because the exact FLGD revision is frozen and the audit observed exactly 24 such messages, the amended real Stage B run must reproduce total `ignoredDuplicateReleaseCount = 24`; otherwise it fails closed and requires another preregistration amendment.

No canonical file or metadata row is excluded by this structural rule.

## Authority boundary

Unchanged:
- no correctness result has been produced;
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- protected song unused.
