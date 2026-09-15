# Songsterr Fresh V6 — GAPS Replacement-Holdout Metadata Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/alignment research only; **no audio/media access, no Basic Pitch, no V6 correctness**.

## Binding authorities

- V6 method preregistration: `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`
- V6 implementation: `3a6cbb144fec5613ab6350deb6539297d713df28`
- V6 scoring framework preregistration: `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`
- Guitar-TECHS remains closed as `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no rescue/repair/scoring/rerun.

## Candidate reviewed

**GAPS (Guitar-Aligned Performance Scores), version 1.1 / public dataset card**

Public metadata observed without opening candidate media:

- 300 solo-guitar performances.
- Approximately 14 hours of real guitar audio.
- More than 200 performers.
- High-resolution note-level MIDI alignments and MusicXML scores are advertised.
- Dataset card marks the dataset MIT licensed.
- Version 1.1 states that audio is included.
- Public dataset size is approximately 16.4 GB.

Primary metadata source reviewed: `https://huggingface.co/datasets/xavriley/GAPS` (dataset card; paper arXiv:2408.08653 linked there).

## Frozen V6 admission comparison

GAPS is attractive as a real-guitar, audio+aligned-symbolic corpus, but the frozen V6 audio path requires **isolated-guitar DI**. The public GAPS description instead characterizes performances as recorded in diverse conditions and does not establish that the audio population is a qualifying direct-instrument/DI capture population.

This is an upstream metadata/admission mismatch, not a model-correctness observation.

## Decision

**REJECT / DO NOT ACCESS MEDIA FOR V6 HOLDOUT PURPOSES.**

Reason: the required frozen isolated-guitar DI identity is not established by the public metadata. Therefore GAPS does not clear the pre-media V6 admission gates and must not be consumed merely to inspect whether its correctness would look favorable.

No GAPS audio, MIDI, MusicXML, performance video, or correctness output was downloaded, decoded, listened to, scored, or used to alter V6.

## State preserved

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration research remains paused/unchanged
- Policy C remains `UNENROLLED`
- protected-song execution remains embargoed
- no Modal, Vercel heavy-GPU, or L4 GPU work was used

Continue only metadata/license/alignment search for another untouched real-guitar holdout unless the user explicitly changes scope.