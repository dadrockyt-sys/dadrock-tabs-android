# Songsterr Fresh V6 — EGDB metadata-only holdout screen

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/alignment research only; no media access and no correctness exposure.

## Authority and frozen boundaries

V6 remains frozen by preregistration `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation `3a6cbb144fec5613ab6350deb6539297d713df28`, and external scoring framework `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS remains closed at `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness is permitted. Archived GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution were not reopened.

## Candidate

EGDB (Electric Guitar Dataset; described in public secondary metadata as a corpus for automatic transcription of polyphonic electric guitar music).

Public metadata located during this screen describes approximately 118 minutes of guitar performance, with activity captured using a hexaphonic pickup and a Direct Input (DI) recording path, subsequently re-rendered through multiple amplifier tones. This is directionally compatible with the frozen isolated-guitar/DI requirement at the metadata level.

## Fail-closed gate result

**REJECT / DO NOT ACCESS MEDIA.**

Reason: the public metadata located in this screen does not establish an acceptable dataset license/usage grant for the underlying corpus. The frozen pre-media screening requires license/usage eligibility to be established before any holdout media or reference data are accessed. Therefore EGDB does not clear the pre-media gates and cannot be admitted as an untouched V6 external holdout from the evidence presently available.

No audio, MIDI, tablature, annotations, package archive, or correctness outputs were downloaded or inspected. No Basic Pitch/V6 inference was run. No V6 constant, matcher, tolerance, uncertainty rule, admission gate, stratum rule, or deferred-reveal rule changed.

## State

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C remains `UNENROLLED`
- protected-song execution remains embargoed
- no Modal, Vercel heavy-GPU, or L4 GPU work used

This candidate may only be reconsidered if authoritative licensing/usage terms are found without accessing holdout media/reference contents; any later admission must still satisfy every frozen pre-media gate prospectively.
