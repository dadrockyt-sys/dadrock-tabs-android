# Songsterr Fresh V6 — electric-guitar-samples Pre-Media Rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **IMMUTABLE PRE-MEDIA REJECTION; NO CORRECTNESS EXPOSURE**

## Scope

This checkpoint records metadata/license/reference screening only for the public `ZulfadhliM/electric-guitar-samples` corpus as a possible untouched real-guitar V6 replacement holdout after Guitar-TECHS frozen audit decision C.

No WAV/LFS payload was downloaded or opened. No Basic Pitch inference, V6 classification, correctness matching, reference scoring, Modal, Vercel heavy-GPU, or L4 execution occurred.

## Authoritative metadata inspected

Public GitHub repository metadata and its README were inspected without fetching media.

The README describes the corpus as electric-guitar samples used for pickup/plucking-position estimation. Its filename hierarchy encodes six strings, eight plucking distances, and five pickup configurations. It does not establish synchronized MIDI/JAMS or another pre-existing note-event reference stream aligned to the audio performances.

The GitHub repository metadata reports `license: null`, and the README contains no dataset usage/license grant.

## Frozen-framework conflicts

The candidate fails before media access for independent reasons:

1. **License/usage gate not established.** Public repository metadata has no detected license and the README does not provide a dataset license grant.
2. **Independent synchronized note-event ground truth not established.** Filename metadata describes string/plucking/pickup conditions, not an aligned MIDI/JAMS event reference suitable for the frozen one-to-one onset/pitch matcher.
3. The frozen V6 framework may not manufacture, infer, hand-label, or derive a replacement reference from candidate audio after selection.

These are structural/pre-media failures, not model-correctness observations. No frozen V6 constant, Basic Pitch setting, audio path, matcher, tolerance, uncertainty statistic, admission gate, stratum rule, or deferred-reveal/single-run rule is changed.

## Decision

**REJECT BEFORE MEDIA ACCESS.**

Do not use this corpus for V6 correctness under the frozen framework unless a future authoritative source independently resolves the missing license and synchronized-reference requirements before any media/correctness exposure; any such reconsideration must be checkpointed prospectively.

## Invariants retained

- Guitar-TECHS remains frozen decision C and is not scored.
- `modelValidationComplete:false`.
- `customerEligibleEvents:0`.
- `mayAdvanceDelivery:false`.
- duration authority unchanged/paused.
- Policy C remains `UNENROLLED`.
- protected-song execution remains embargoed.
- no Modal, Vercel heavy-GPU, or L4 work occurred.
