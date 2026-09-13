# Songsterr Fresh V6 — Geoff Bremner Corpus Reference Provenance Review

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **PRIVATE-LICENSE LEAD / NOT AUDIT-READY — PUBLIC METADATA DOES NOT ESTABLISH INDEPENDENT PERFORMED GUITAR MIDI**

## Purpose

Resolve as far as public metadata permits whether the Geoff Bremner Multimodal Music Corpus provides a contemporaneous independently captured performed guitar note stream suitable for the frozen V6 replacement-holdout gate.

This review is metadata-only. No audio, MIDI, Guitar Pro, Ableton project, stem, PDF or other candidate corpus file was downloaded or parsed. No rights-holder contact was made. No Basic Pitch/V6 execution or correctness occurred.

## Public sample reviewed

Hugging Face dataset:
`geoffbremneraudio/Geoff_Bremner_Multimodal_Music_Corpus_SAMPLE`

The dataset card states:
- one-track sample from a growing commercially licensable corpus;
- 100% original music written, recorded and produced by Geoff Bremner;
- single creator / single rights holder / complete version history;
- public sample license CC BY-NC 4.0;
- separate Professional / Enterprise licensing is offered for commercial use;
- sample contents include master audio, stems, MIDI, Guitar Pro, PDF notation and metadata.

This is a materially cleaner chain-of-title story than most third-party or popular-song corpora, but rights and reference provenance are separate gates.

## Public file structure

The public repository tree exposes, among other items:
- `Pharisaism.mid` — one MIDI file;
- `Pharisaism.gp` — one Guitar Pro file;
- `Pharisaism-git-1.pdf` and `Pharisaism-git-2.pdf` — separate guitar notation PDFs;
- `Pharisaism-bass.pdf` / `Pharisaism-drums.pdf`;
- an Ableton project directory and `Pharisaism.als`;
- rendered stems including `Pharisaism Guit L.wav`, `Pharisaism Guit R.wav`, `Pharisaism Guitar.wav`, bass, drums, keys, lead and effects;
- full mix/master material.

The sample card does **not** document:
- what instrument(s) the single `.mid` contains;
- whether guitar MIDI is present at all, versus drums/keys/full arrangement;
- whether any guitar MIDI was recorded simultaneously from the guitar performance;
- whether MIDI was authored before recording, exported from Guitar Pro/notation, quantized in the DAW, transcribed after recording or otherwise post-produced;
- whether MIDI timing represents performed attack times rather than score/arrangement times;
- whether multiple guitar stems map one-to-one to independent per-performance MIDI tracks/events;
- exact clock/alignment semantics between MIDI and real guitar stems.

## Reference-provenance result

The public sample establishes **coexistence** of real audio stems, an arrangement MIDI file, notation and Guitar Pro assets. It does not establish **independent contemporaneous performed guitar note truth**.

Under the frozen V6 gate, coexistence is insufficient. A score/arrangement MIDI export, DAW MIDI, Guitar Pro sequence or post-produced transcription cannot become performed-reference truth merely because it accompanies the same original song.

The repository structure arguably makes authored/production MIDI plausible — one arrangement MIDI exists alongside a Guitar Pro score and multiple guitar stems — but this review does **not** convert that observation into a factual claim about how the MIDI was made. The decisive point is simply that public documentation does not establish the required capture provenance.

## Rights status

The public sample itself is CC BY-NC 4.0 and therefore cannot directly clear commercial/product use. The creator explicitly advertises separate commercial licensing, which means a usable rights path may exist in principle.

However, do not contact the creator or acquire the full corpus under the current metadata-only search. Even a commercial license would not make this V6-ready unless the performed-reference semantics are separately established before media access.

## Evidence volume / population status

The public sample is only one track / 38 repository rows and does not establish:
- size of the full corpus;
- number of real guitar performances;
- player diversity;
- raw performed guitar note count;
- category coverage under the frozen `chords/scales/singlenotes/techniques/music` strata;
- plausible >=1,000 V6-positive capacity without duplicate/production inflation.

Therefore volume cannot be assumed from the phrase “growing corpus.”

## Disposition

**Keep only as a private-license metadata lead; do not advance to media access or structural audit.**

To reconsider, authoritative pre-media documentation would need to establish all of the following:
1. guitar-specific MIDI/note events were captured contemporaneously from the real performances through a reference path independent of the evaluated guitar audio;
2. onset timestamps represent performed attacks rather than authored/quantized score times;
3. exact audio/reference mapping and clock/alignment semantics;
4. full-corpus real-guitar population/evidence volume and stable identities;
5. explicit license/permission covering this product-validation use.

If reference provenance is instead authored Guitar Pro/DAW MIDI, post-hoc transcription, quantized score data or audio-derived MIDI, reject for V6 admission even if commercial rights are available.

## Authority unchanged

No media was downloaded or parsed. No rights-holder contact was made. No V6 method/scoring rule changed and no correctness was exposed.

Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song embargoed

Archived V143/Gomyway and GOAT/reference scoring remain closed.
