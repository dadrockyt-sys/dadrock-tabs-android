# Songsterr Fresh V6 — Five guitar dataset pre-media rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/alignment search only; no correctness exposure.

## Frozen authority

V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. External scoring remains frozen by commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS run `34754519541`, job `103716527380` was re-inspected before this search and remains `completed/success`. Artifact `guitar-techs-v6-alignment-inventory` remains artifact ID `10317695640`, digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`. Its frozen audit decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no duplicate audit and no Guitar-TECHS correctness were started.

## Candidate screened

Candidate: **Five guitar dataset**, Eduard Vergés Franch, Zenodo record `4988354`, DOI `10.5281/zenodo.4988354`.

Public metadata establishes 30 performances of six songs, each recorded with five guitars and simultaneously through three setups, including DI. The record enumerates 90 WAV files and publishes per-file MD5 values. The recording description states that electric guitars were plugged into a DV Mark Little Jazz amplifier whose DI output fed the audio interface; acoustic guitars used pickup/preamp paths into the interface.

## Pre-media admission decision

**REJECT BEFORE MEDIA / REFERENCE ACCESS.**

Reason: the authoritative Zenodo record exposes WAV performances only and does not establish a synchronized note-event ground-truth/reference stream (MIDI, JAMS, or equivalent event timing/pitch annotations) required to apply the already-frozen V6 one-to-one onset/pitch scoring framework. The filenames encode song, guitar, tempo and recording setup, not note-event truth. Therefore the candidate cannot satisfy the frozen external-scoring reference/alignment gate without introducing a new or inferred reference construction, which is not permitted.

This rejection is structural and reference-related, not a model-correctness observation. No candidate audio was downloaded, decoded, previewed, listened to, transcribed, or passed through Basic Pitch/V6. No reference data were accessed. No scoring constants, Basic Pitch settings, matcher, tolerances, uncertainty rules, admission gates, strata rules, or deferred-reveal/single-run rules changed.

## State

- Guitar-TECHS remains closed at decision C.
- Five guitar dataset is rejected for V6 external correctness before media access.
- Search may continue only for another untouched real-guitar holdout that independently clears the frozen metadata/license/audio/reference/alignment gates.
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration remains unchanged/paused.
- Policy C remains `UNENROLLED`.
- protected-song execution remains embargoed.
- No Modal run, Vercel heavy-GPU run, or L4 GPU run was used.