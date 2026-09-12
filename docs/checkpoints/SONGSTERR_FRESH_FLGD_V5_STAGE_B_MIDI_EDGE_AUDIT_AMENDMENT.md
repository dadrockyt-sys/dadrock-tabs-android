# Songsterr Fresh — FLGD V5 Stage B MIDI Edge Audit Amendment

Status: **FROZEN AFTER STRUCTURAL FAIL-CLOSED EVENT / BEFORE ANY CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Why this amendment exists

The first real Stage B manifest attempt ran on the exact preregistered FLGD release and failed closed before producing any report:
- one-shot workflow source `43b8ed6a15fe1fee792db9a20ed36d6baa08c5a6`
- workflow run `34719399752`
- job `103622351601`
- failure: `MIDI_UNMATCHED_NOTE_OFF:midi/Fp24c.mid:(0, 48):65091`.

No Basic Pitch inference, V5 classification, estimate/reference matching, precision/recall, or correctness result was produced.

The original Stage B preregistration required unmatched note-offs/onsets to fail closed. The real canonical reference structure has now falsified the assumption that every note-off necessarily has a preceding same-file onset under the initial parser convention.

This amendment does **not** authorize silently dropping the event or relaxing correctness scoring. It authorizes one structural audit only so the reference convention can be frozen from evidence rather than guessed.

## Authorized audit scope

Run once over all 79 metadata-named canonical `midi/` files at the same exact FLGD revision.

The audit may parse SMF message structure/ticks/channels/notes/tempo exactly as Stage B already preregistered and report:
- note-on count;
- note-off count;
- unmatched note-off count and exact `(file, track, tick, channel, MIDI, velocity/status form)` identities;
- unmatched note-on count remaining at end-of-file with exact identities;
- same-key overlap count;
- duplicate release count where multiple offs target a key with no active onset after a valid pair;
- for each unmatched edge, whether the same channel/MIDI has any earlier/later note-on or note-off in the file;
- whether the edge occurs at the earliest or latest tick for that channel/MIDI;
- MIDI header/PPQ/track metadata needed to contextualize the edge.

The audit may also record ordering ties at identical ticks to determine whether deterministic track-order merging can explain an apparent unmatched edge.

## Explicitly forbidden

The audit MUST NOT:
- decode audio samples;
- invoke Basic Pitch, V5, Demucs, librosa, NumPy/SciPy signal processing or source separation;
- use syncpoint values to judge note correctness;
- compare any estimate to reference MIDI;
- compute precision, recall, F-score, correctness, or admission metrics;
- change the 79-file population;
- use `test_set/` or model-output MIDI as truth;
- alter customer/model/duration authority.

## Decision rule after audit

No parser behavior is changed by this document.

After the audit, a second explicit Stage B parser amendment must be committed **before rerunning the real Stage B manifest**. That amendment must choose one deterministic rule justified by the structural audit, for example:
- preserve strict failure if the file is genuinely structurally unusable; or
- classify a proven boundary/double-release convention mechanically and exclude only the unmatched edge from note-event construction while preserving the file/population; or
- specify another deterministic SMF pairing convention supported by the audit.

No rule may depend on audio correctness, V5 behavior, or desired validation performance.

## Authority boundary

Remains exactly:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- protected song unused.
