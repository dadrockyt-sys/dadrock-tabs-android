# Songsterr Fresh V6 — GuitarJam pre-media rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/alignment screening only; no media/reference access and no correctness.

## Candidate

`Julian-br/GuitarJam` (Hugging Face dataset repository).

Public dataset metadata states:

- approximately 2.5 hours of clean monophonic electric-guitar improvisations;
- 580 clips of about 15 seconds each;
- raw guitar recorded by direct input (DI), without effects or amplifiers;
- WAV, 44.1 kHz, 16-bit;
- recording chain: Fender Stratocaster -> Focusrite Scarlett Solo -> Audacity;
- repository metadata declares `license: cc0-1.0`.

Public repository history identifies the 580-file upload at commit `2d467bfec90af19301b01123494f4b2ba64c5a3a` and the README/license metadata at commit `41ad464fc252f6b19f7e11f6186b954e5ec3b411`.

## Frozen-gate assessment

GuitarJam clears the real-guitar / isolated clean DI / public-license metadata characteristics, but the authoritative public dataset description and repository inventory expose an audio-only corpus and do not establish synchronized note-event ground truth (MIDI/JAMS or equivalent immutable event annotations) aligned to the performances.

The frozen V6 external-scoring framework requires pre-existing synchronized reference note events suitable for its frozen matcher. Creating, transcribing, inferring, or otherwise manufacturing reference events from the candidate audio would violate the reference-blind/pre-existing-ground-truth boundary.

Decision: **REJECT BEFORE MEDIA ACCESS**.

Reason: synchronized pre-existing note-event ground truth is not established by the candidate's authoritative public metadata/repository. This is a structural admission failure, not a model-correctness observation.

## Audit boundary

- No GuitarJam WAV was downloaded, opened, decoded, measured, or scored.
- No candidate-derived note reference was accessed or created.
- No Basic Pitch or V6 correctness inference was run.
- No V6 constants, Basic Pitch settings, audio path, matcher, tolerances, uncertainty rules, admission gates, strata rules, or deferred-reveal/single-run rule changed.
- No Modal, Vercel heavy-GPU, or L4 GPU work occurred.
- Guitar-TECHS remains rejected under frozen alignment decision C and must not be scored.
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration remains paused/unchanged.
- Policy C remains `UNENROLLED`; protected-song execution remains embargoed.

This checkpoint is an immutable pre-media rejection record. It does not authorize any correctness execution or retry.
