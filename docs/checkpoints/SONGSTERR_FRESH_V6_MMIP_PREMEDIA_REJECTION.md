# Songsterr Fresh V6 — MMIP pre-media rejection

Date: 2026-09-15
Branch: `songsterr-fresh-pipeline-v1`
Scope: V6 replacement-holdout metadata/license/alignment search only. No correctness exposure.

## Candidate

Multi-Modal Instrument Performances (MMIP), Kyriakou, Aristidou, Charalambous (2025).

Authoritative/public metadata establishes:

- real guitar performances are included;
- guitar audio is captured through a Focusrite Scarlett 2i2 audio interface;
- WAV audio is 44.1 kHz stereo;
- synchronized MIDI files are provided;
- repository content is CC BY-NC-SA 4.0, with commercial use requiring separate licensing.

## Frozen-gate finding

MMIP is **not an admissible untouched V6 external correctness holdout**.

The MMIP paper explicitly states that for guitar, MIDI was obtained with audio-to-MIDI plugins, specifically describing NeuralNote, whose internal transcription model uses Spotify Basic Pitch. The MIDI is therefore model-derived from the guitar audio rather than an independent capture/annotation reference. Frozen V6 external scoring uses Basic Pitch predictions and requires an independent external note-event reference; using Basic-Pitch-derived reference labels would contaminate/circularize the correctness audit.

The CC BY-NC-SA 4.0 / separate-commercial-license condition is also materially narrower than an unrestricted commercial-compatible dataset grant, but the non-independent reference provenance is independently dispositive for this audit.

## Decision

**REJECT BEFORE MEDIA ACCESS.**

No MMIP WAV, MIDI, motion, or video payload was downloaded or opened. No Basic Pitch/V6 correctness was run. No V6 constants, Basic Pitch settings, audio path, matcher, tolerances, uncertainty, admission gates, strata rules, deferred-reveal rule, or single-run rule changed.

Guitar-TECHS remains frozen at alignment/inventory decision C and must not be scored. Search may continue only at metadata/license/alignment level for another untouched real-guitar holdout.

## Safety / authorization state

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration research unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
- no Modal run
- no Vercel heavy-GPU run
- no L4 GPU run
