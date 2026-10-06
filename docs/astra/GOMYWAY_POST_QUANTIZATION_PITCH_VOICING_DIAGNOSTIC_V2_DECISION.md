# Go My Way post-quantization pitch/voicing diagnostic V2 — decision brief

Date: 2026-10-06  
Branch: `astra-work`  
Authoritative run: `37425440848` — **SUCCESS**  
Artifact: `11394362287`  
Artifact digest: `sha256:4c5621f3552adcff4a6214d690822c0a91284cb5bcdef0056dd0df69483f0f97`  
Result JSON SHA-256: `be2fa35794b3f8be0a23220a7683f8592eced40c220abcf9486fa81bb0ea825d`

## What was verified

The diagnostic was model-free and used only frozen artifacts. Candidate SHA before and after remained `880446f4e93898395b91fa2b27a081817e93e7ed1883cf0d64940d22a453400e`. Original and quantized streams each contain 1065 events with identical ordered identity/MIDI and duration preservation to numerical tolerance (maximum error (1.42e-14) s). Original evidence was verified through its frozen manifest. Ten focused fixtures passed, including chord-order permutation, duplicate one-to-one matching, a greedy-cardinality counterexample, exact 50 ms tolerance, +/-12 versus +/-24 bucketing, exclusions/final endpoint, invalid/hash rejection, empty input, and mutation guards.

The primary matcher is maximum-cardinality onset-only matching followed by minimum total onset error. Pitch never selects a pair. Legacy greedy matching remains historical context only.

## Main measured result

### Rhythm

Original -> quantized:
- onset-matched targets: **444 -> 467**
- target recall: **46.93% -> 49.37%**
- unmatched targets: **502 -> 479**
- assignment-dependent exact MIDI among matches: **184/444 (41.44%) -> 155/467 (33.19%)**
- unambiguous exact-MIDI rate: **50.00% -> 50.00%**
- ambiguous matched events: **286 -> 303**
- pairing-invariant ambiguous pitch-multiset overlap: **84.27% -> 83.50%**

The raw fall in rhythm exact-MIDI pairing is therefore not stable evidence of a new octave/voicing defect. Chord/onset ambiguity changes the assignment while the unambiguous rate is unchanged and the pairing-invariant chord-pitch overlap remains high.

### Lead

Original -> quantized:
- onset-matched targets: **222 -> 236**
- target recall: **49.66% -> 52.80%**
- unmatched targets: **225 -> 211**
- assignment-dependent exact MIDI among matches: **89/222 (40.09%) -> 108/236 (45.76%)**
- unambiguous exact-MIDI rate: **57.48% -> 54.48%**
- ambiguous matched events: **95 -> 102**
- pairing-invariant ambiguous pitch-multiset overlap: **63.16% -> 67.65%**

Lead benefits from quantized timing in coverage, but the extra exact-MIDI gain is concentrated in ambiguous assignment territory. The unambiguous exact-MIDI count remains 73 while seven more unambiguous onsets become matched, so this does not justify a reference-derived pitch correction.

## Boundary, meter, and combined-score audits

Quantization changes assigned measure status for 45 events per role, but **0** events migrate eligible->ineligible and **0** migrate ineligible->eligible. This rules out excluded-population migration as the explanation for the legacy F1 gain.

The timing map confirms measure 104 is **2/4** and measure 105 is **4/4**. The frozen quantizer/scorer convention is 16 equal subdivisions of every measure duration; it must not be described as literal musical sixteenth notes in all meters.

The legacy combined score concatenates rhythm and lead targets and filters predictions by the union of role exclusions. There are **75 coincident same-pitch cross-role targets** and no cross-role deduplication. Preserve that historical convention; do not silently reinterpret the existing 37.01% combined F1.

## Decision

**Stop prediction changes here.** The diagnostic does not support an octave-placement or simple voicing-correction experiment from Go My Way references.

The strongest bounded next hypothesis is **missing or unsynchronized event evidence**: quantization exposes more target onsets, while residual unmatched targets remain larger than the wrong-pitch matched population in both roles. That is a hypothesis, not a finding that a particular recovery algorithm will work.

Any next experiment must be predeclared and validated on independent rights-cleared development material or held-out performer-disjoint clean data without using Go My Way references to choose parameters. Go My Way is exposed development/scoring material and may not drive a correction.

Preserve the immutable 1065-event quantized candidate, spectral bass V1, frozen BS-Roformer separator, V4-origin timing, original Basic Pitch V4 evidence, and `main` unchanged.
