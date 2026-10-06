# Guitar-FL integration Stage B source decision V1

Date: 2026-10-06
Branch: `astra-work`
Status: **SOURCE CLASS SELECTED / NO CAPTURE OR EMPIRICAL EXECUTION AUTHORIZED**

## Decision

No currently reviewed public real-guitar corpus clears both of the Stage-B requirements:

1. independently captured performed note truth suitable for pitch/onset and, preferably, string/fret validation; and
2. a rights chain suitable for product-validation work rather than research-only / non-commercial use.

Therefore Stage B will not weaken the reference standard or reuse consumed material.

The selected Stage-B source class is:

> **a purpose-built untouched real-guitar holdout with independently captured physical string/fret state plus independent event-birth timing, synchronized to the evaluated clean-DI recording by a shared hardware clock or preregistered hardware sync markers.**

This selection is a design decision only. It does not authorize performer contact, procurement, recording, spending, capture, model inference, or scoring.

## Public-corpus frontier reviewed

### GAPS v1.1

Rejected for Stage B:
- high-resolution per-note timing is reconstructed from evaluated performance audio via alignment/model activations;
- the consumed 30-track test population is no longer fresh;
- public package-level licensing does not establish a track-by-track rights chain for the underlying third-party performances.

### François Leduc Guitar Dataset

Rejected as Stage-B truth:
- performed timing is reconstructed using score/audio alignment and model activations;
- it is the training substrate of the frozen intervention, so it cannot serve as independent evaluation truth;
- product-rights provenance remains unresolved.

### GuitarSet

Rejected for fresh Stage B:
- multiple project populations have already been consumed in prior development/validation;
- the remaining players are not treated as a clean untouched product-validation population without a separately justified contamination audit.

### Guitar-TECHS

Not reopened:
- already used extensively for development/training/diagnosis;
- P3 remains sealed by prior governance;
- cannot be treated as a fresh Stage-B holdout.

### IDMT SMT Guitar

Rejected:
- already consumed by prior official external validation;
- cannot be reused as fresh evidence.

### EGDB / EGDB-PG

Rejected:
- onset truth is derived from the recorded DI string signals via onset detection;
- public corpus-wide product-validation rights remain insufficiently established.

### AG-PT-set

Rejected:
- onset labels were created/corrected while inspecting the evaluated audio/spectrogram and onset-detector proposals;
- not independent performed timing.

### Five Guitar Dataset

Rejected:
- no independent performed note-level reference stream.

### Klangio GST-MM-2025

Rejected:
- supervision is strum/chord level rather than independent per-note MIDI/string-fret truth;
- onset timing incorporates spectral-flux analysis of evaluated audio;
- dataset-audio rights suitable for product validation are not established.

### GOAT (2025)

Scientifically attractive but not eligible for this product-validation Stage B:
- real electric-guitar DI with tablature/aligned MIDI;
- current public record describes CC BY-NC 4.0 / research-only use and explicitly says it is not intended for use in a commercial product;
- prior project access path was closed after a research-access denial.

A public/research-only dataset must not be promoted into product-validation authority merely because it is convenient.

## Selected purpose-built source requirements

The Stage-B holdout must use three independent evidence planes:

1. **Evaluated audio:** clean real-guitar DI only.
2. **Physical pitch identity:** independently captured string/fret state.
3. **Independent event birth:** separately captured excitation/rearticulation evidence sufficient to distinguish repeated same-pitch attacks.

Reference timing must not be recovered from evaluated audio, spectrograms, DTW, onset detection, transcription-model activations, or manual waveform alignment.

## Rights requirements

Before any holdout capture authorization:

- performer release/license must explicitly allow recording plus product-validation use;
- recording ownership/use grant must be explicit;
- composition/content provenance must be explicit;
- protected-song material must be excluded;
- every rights document must have a stable identifier and SHA-256;
- all admitted performances must link to the applicable rights documents.

Preferred content: original material, public-domain material, or expressly commissioned/rightsholder-cleared exercises.

## Freshness requirements

The future holdout must be permanently disjoint from:
- GAPS;
- Go My Way;
- GuitarSet;
- Guitar-TECHS;
- IDMT;
- François Leduc training material;
- all calibration performances;
- any material used to choose thresholds, decoder rules, timing semantics, or fretboard parameters.

## Current boundary

This decision does not authorize capture or empirical Stage B.

The next permissible step is to freeze the Stage-B capture/evaluation preregistration, including population size, category balance, invariants, numerical gate, and anti-cherry-picking rules.
