# Songsterr Fresh V6 — Purpose-Built External Holdout Option

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **DESIGN / FEASIBILITY OPTION ONLY — NO DATA ACQUISITION, PROCUREMENT, MODEL RUN, OR CORRECTNESS AUTHORIZED**

## Why this option exists

The public replacement-corpus search has become highly constrained. The scientifically strongest known candidates are blocked by rights, reference provenance, prior exposure/contamination, structural anomalies, synthetic rendering, insufficient volume, or missing note-level performed truth.

Rather than weaken the frozen V6 experiment to fit a compromised public corpus, this checkpoint records a cleaner fallback strategy: commission or capture a genuinely new external real-guitar holdout **after the V6 method/scoring framework was frozen**, using an independent contemporaneous reference path and explicit rights.

This document does **not** select a corpus, purchase equipment, hire performers, contact vendors, authorize spending, collect media, change V6, or authorize any Basic Pitch/V6 correctness run.

## Frozen authority preserved

Nothing here changes:

- frozen V6 implementation/settings;
- Basic Pitch `0.4.0` settings;
- event-preservation rule;
- 50 ms onset / 50-cent pitch matcher;
- one-sided Wilson statistic;
- pooled `0.9900` lower-bound gate;
- frozen player/category robustness gates;
- minimum `1,000` V6-positive estimates;
- deferred-reveal / single-run rule;
- duration authority;
- protected-song embargo;
- `modelValidationComplete:false`;
- `customerEligibleEvents:0`;
- `mayAdvanceDelivery:false`;
- Policy C `UNENROLLED`.

The frozen scoring categories remain exactly:
`chords`, `scales`, `singlenotes`, `techniques`, `music`.

## Core scientific requirement

The holdout must be generated without any access to V6 correctness or model outputs. The reference stream must be captured contemporaneously through a path independent of the **evaluated DI waveform**; it cannot be constructed afterward by Basic Pitch, onset detection, pitch tracking, source separation, score-to-audio alignment, manual listening to the evaluated DI, or any other evaluated-audio-derived transcription.

The evaluated signal remains clean isolated real-guitar DI only.

## Preferred reference architecture — physical fret/trigger sensing

A stronger candidate architecture is a real electric guitar whose reference MIDI is generated from **physical fret-position + independent trigger/dynamics sensors**, while the evaluated audio comes from a conventional magnetic-pickup DI output.

Current feasibility example (not selected/endorsed): Industrial Radio Fretsense / Solange 6.

Primary vendor pages reviewed:
- https://industrialradio.com.au/products/fretsense/
- https://industrialradio.com.au/products/solange-6-midi-guitar/
- https://industrialradio.com.au/products/fsi-1-fretsense-interface/

The manufacturer states that Fretsense:
- uses a wired fretboard to detect held fret/note position by string/fret conductivity rather than relying solely on pitch-to-voltage conversion;
- uses additional bridge/piezo sensors for triggers/dynamics and pitch-bend sensing;
- supports polyphonic MIDI and per-string behavior;
- provides a real six-string electric guitar with conventional magnetic audio;
- exposes MIDI plus a separate magnetic-pickup audio output through the FSI-1 interface.

This is **feasibility evidence only**, not proof that the resulting MIDI is error-free or automatically acceptable as V6 truth. Any exact hardware/firmware/settings would have to be frozen before capture and then survive a reference-blind structural audit.

### Why this is preferable to ordinary pitch-to-MIDI

The candidate reference note identity is not inferred from the same evaluated magnetic DI waveform. Fret position and trigger state are sensed through distinct instrument sensors. That creates a materially stronger independence story than post-hoc audio transcription or an onset detector run on the candidate DI.

However, independence is not enough by itself. The system can still emit bad/missing/overlapping MIDI, so strict pre-correctness structural rejection remains mandatory.

## Secondary feasibility architecture — separate hexaphonic MIDI pickup

A lower-confidence fallback is a real MIDI guitar using a dedicated six-channel hexaphonic pickup while evaluated audio is captured simultaneously from the separate standard guitar output.

Current example reviewed: Jamstik MIDI Guitar.

Primary vendor/support pages:
- https://jamstik.com/pages/how-it-works
- https://jamstik.com/pages/faq
- https://support.jamstik.com/hc/en-us/articles/11591028822285-Jamstik-MIDI-Guitar-Device-Settings
- https://support.jamstik.com/hc/en-us/articles/360045248411-Getting-Started-with-the-Jamstik-in-Ableton-Live

Jamstik states that it has separate traditional 1/4-inch guitar audio and MIDI paths, with MIDI derived independently per string from a six-channel hexaphonic pickup. It can output six MIDI channels / MPE.

But vendor support explicitly documents potential extra or missed MIDI notes depending on string sensitivity, and some DAW/MPE implementations do not preserve per-string MIDI channel identity. Therefore this architecture must **not** be assumed correct merely because audio and MIDI are simultaneous. If ever evaluated for capture, exact hardware/firmware, sensitivity, pickup geometry, MIDI mode, DAW and raw MIDI preservation path must be frozen before data creation.

A physically fret-sensed architecture is preferred when practical because pitch identity is less dependent on real-time audio-to-MIDI inference.

## Independent market-feasibility evidence

Current public commissioning posts demonstrate that rights-cleared real recordings with simultaneous note-level MIDI are commercially obtainable in principle. Example Twine postings request real audio + note-level MIDI, with pitch/onset/offset, often captured in the same take, prohibit MIDI-rendered synthetic audio and automatic-transcription-generated annotations, and require rights for commercial/AI use:

- https://www.twine.net/projects/b9q9i0-music-composer-real-recordings-with-midi-annotations-music-composer-remote-job
- https://www.twine.net/projects/b9ods0-musician-real-recordings-with-midi-annotations-remote-musician-remote-job

These postings are only evidence that such commissioning workflows exist. They are **not a dataset, rights grant, performer source, or authorization to hire anyone**. Their looser annotation options (for example manual annotation/score alignment) would not satisfy this frozen V6 design and are explicitly excluded here.

## Proposed capture contract — design requirements

If the purpose-built route is later explicitly selected, a corpus-specific preregistration must be committed **before any performer records a candidate holdout take**. At minimum it should freeze all of the following.

### 1. Rights / originality

- every exercise/excerpt must be newly composed for the project, public-domain, or otherwise covered by an explicit written grant suitable for commercial product-validation use;
- no protected-song performance;
- every performer grants the exact recording/data rights needed for this validation use;
- rights must cover audio, raw MIDI/reference data, metadata, reproducibility storage and internal validation use;
- no ambiguous mirror/repository license may substitute for the actual performer/data rights.

### 2. Performer independence

- performers must not receive V6 predictions, Basic Pitch predictions, correctness results, target failure examples, optimizer output, or protected-song observations;
- no performer may alter playing or retake a passage based on model correctness;
- capture personnel may see only preregistered capture/structural QA results.

### 3. Signal independence

- evaluated audio: clean isolated guitar DI from a declared conventional guitar output path;
- reference: simultaneous independent fret/trigger/MIDI sensor path;
- no reference event may be created from the evaluated DI waveform;
- the raw unedited reference stream must be retained and hashed;
- exact audio/reference clocking and transport topology must be documented.

### 4. Reference preservation

- preserve raw MIDI event order, channel, note number, timing and edge identity;
- no manual deletion, insertion, repitching, quantization, onset shifting or audio-guided cleanup after capture;
- any normalization needed only to parse standard MIDI semantics must be deterministic and frozen in advance;
- string/channel identity may be retained diagnostically but cannot enter V6 classification.

### 5. Structural acceptance rules

Before any Basic Pitch/V6 use, run a reference-blind audit analogous to the Guitar-TECHS audit.

At minimum require:
- exact source hashes and complete manifest;
- unambiguous one-to-one audio/reference pairing;
- finite nonempty audio and declared format;
- deterministic MIDI parsing;
- zero orphan note-ons;
- zero orphan note-offs;
- zero same-key overlaps under the frozen MIDI semantics;
- all expected channels/strings preserved;
- no silent file/take dropping;
- deterministic reference-blind audio/reference alignment decision;
- immutable accepted-population manifest hash.

If the **frozen corpus-level audit** encounters structural anomalies that violate the preregistered acceptance rules, reject the corpus/population before correctness rather than repairing events based on the audio. Guitar-TECHS already demonstrated why this fail-closed boundary matters.

### 6. Capture-QA boundary

Capture-stage QA must be frozen before collection and must not inspect model correctness.

Permissible capture QA may include objective acquisition failures such as:
- missing/corrupt files;
- clipping beyond a predeclared limit;
- device disconnect;
- absent reference channel;
- wrong sample rate/format;
- known transport failure;
- malformed MIDI stream under a predeclared parser.

It must not include:
- whether Basic Pitch/V6 would succeed;
- whether a passage seems "easy" or "hard" for the model;
- audio-guided editing of individual MIDI events;
- selective retakes after inspecting model output.

The exact distinction between a failed acquisition attempt and an admitted holdout take must be frozen before capture so rejected acquisition failures cannot become post-result cherry-picking.

### 7. Musical population

Retain the already-frozen scoring categories exactly:
- `chords`
- `scales`
- `singlenotes`
- `techniques`
- `music`

The final population must not be selected using model outcomes.

Original/public-domain musical excerpts should cover realistic clean-guitar playing, including polyphony and technique variation, rather than only isolated easy notes.

### 8. Diversity

A defensible external holdout should use multiple independent players and heterogeneous real capture conditions where feasible. Exact player count, guitars/pickups, interfaces, rooms, tempos and category allocation must be preregistered before capture.

A single-player/single-instrument corpus is scientifically weaker even if it technically clears the frozen pooled gate.

### 9. Evidence planning — not a new admission gate

The existing mandatory gate remains **>=1,000 V6-positive estimates**. The number of V6 positives is unknowable without exposing correctness-era model output, so collection should be conservatively larger.

A provisional planning target of **>=20,000 raw reference note-ons** across all accepted takes is reasonable because Guitar-TECHS contained 18,934 reference events yet was still only one structural candidate. This `20,000` figure is **not a replacement scoring gate** and does not modify the frozen >=1,000-positive requirement; it is only pre-model capacity planning.

Likewise, a provisional planning preference is >=5 players and broad category coverage, but the exact collection design would have to be frozen in a separate corpus-specific capture preregistration before any data is made.

## Required ordering if this route is ever selected

1. explicit user decision to pursue a purpose-built holdout and any spending/procurement;
2. choose/reference hardware only after confirming real signal/reference semantics;
3. freeze exact rights contract + capture protocol + hardware/firmware/settings + QA rules + population design in Git before capture;
4. collect original/public-domain real-guitar data with zero model access;
5. hash raw source bytes and freeze full inventory;
6. run a reference-blind structural/alignment audit only;
7. if audit outcome is unsuitable, reject without correctness and do not repair it into eligibility;
8. if suitable, bind immutable identities into the already-frozen V6 external scoring framework;
9. build/run controlled synthetic/contract-only harness CI with no real-holdout correctness;
10. launch exactly one ordinary-GitHub-CPU official correctness run under the frozen single-run rule;
11. write immutable result before interpretation and retain fail-closed policy state pending separate review.

## What is NOT authorized now

- no purchase/order/deposit for Industrial Radio, Jamstik or other hardware;
- no hiring/commissioning/contacting performers or vendors;
- no download/acquisition of a candidate holdout;
- no purpose-built recording session;
- no Basic Pitch/V6 run on any prospective data;
- no protected-song capture;
- no change to V6 or its frozen scoring framework;
- no V143/Gomyway or other archived-line work;
- no Modal, Vercel heavy-GPU or L4 use.

## Current disposition

**Purpose-built external holdout: scientifically plausible fallback, not selected and not acquisition-authorized.**

The preferred technical direction, if ever chosen, is a real guitar with a physical fret/trigger sensing reference path plus separate clean magnetic DI, because it best preserves independence between evaluated audio and note identity. Ordinary hexaphonic pitch-to-MIDI remains a weaker fallback that would need stricter structural verification.

Continue metadata-only public/private corpus search in parallel. Do not lower the V6 gates merely because the public corpus frontier is sparse.
