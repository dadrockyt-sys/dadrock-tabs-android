# Songsterr Fresh V6 — Late-Summer 2026 Corpus Delta Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/literature-only replacement-holdout search; no candidate media access; no correctness exposure.

## Frozen authority

This review does not alter any frozen V6 method or scoring authority.

- V6 method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- V6 implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.
- Guitar-TECHS remains closed at frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness is permitted.

## Question

Do the newest late-summer 2026 guitar-transcription papers disclose a genuinely new untouched real-guitar corpus that could satisfy the frozen V6 pre-media gates?

Frozen pre-media gates remain:

1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

## Primary-source delta reviewed

### Noise2Fret — arXiv:2608.30854, submitted 2026-08-31

`Playability-Aware Audio-to-Tablature Guitar Transcription via Diffusion Models`, Riccardo Simionato and Louis Bigo.

Authoritative paper source: https://arxiv.org/abs/2608.30854

The paper states that its experiments are on **GuitarSet and GOAT**. It does not introduce a new independently captured real-guitar dataset. Its dataset discussion cites existing GuitarSet/GOAT material and prior datasets such as EGDB/GAPS; no new corpus package, new rights chain, new independent performed onset+pitch reference stream, or new untouched population is disclosed.

Governance consequence: this paper is a method/results delta only. It does **not** create a replacement V6 holdout. Mention of GOAT here is literature-only and does not reopen archived GOAT/reference scoring.

### Explicit Note-Event Tokenization — arXiv:2607.26440, submitted 2026-07-29

`Explicit Note-Event Tokenization and Pitch-Validity Constrained Decoding for MIDI-to-Tablature Transcription`, Ting-Kai Hsu, Wei-Chin Wang, Kai-Xi Hong, and Yu-Hua Chen.

Authoritative paper source: https://arxiv.org/abs/2607.26440

The paper states that evaluation is on **DadaGP** and the **François Leduc** dataset. DadaGP is symbolic tablature data rather than a new untouched real-guitar performance-audio holdout, and François Leduc is already closed under the V6 governance record because its performed timing is aligned/fine-aligned using transcription-model activations from evaluated audio.

Governance consequence: this paper introduces no new qualifying real-guitar corpus and does not materially change the frozen reference-provenance status of François Leduc.

### TART — arXiv:2609.11904, submitted 2026-09-10

Already separately reviewed and checkpointed. TART evaluates GuitarSet, EGDB, and noisy derivatives; it provides no new independent real-performance holdout. No change from checkpoint `4a6d8e9b9860d2693e72fc0b4bb0af0404692959`.

## Decision

**NO NEW ADMISSIBLE HOLDOUT FOUND IN THIS LATE-SUMMER 2026 DELTA.**

The newly surfaced papers are methodological/evaluation work over already-governed, symbolic, or derivative datasets. None supplies all five frozen pre-media requirements for a new untouched real-guitar external holdout.

Therefore:

- do not access candidate media based on these papers;
- do not score Guitar-TECHS;
- do not reopen GOAT/reference scoring;
- do not alter V6 constants, Basic Pitch settings, matcher, tolerances, admission gates, strata, uncertainty handling, or deferred-reveal/single-run rules;
- continue only metadata/license/alignment search for genuinely new primary evidence or authoritative rights/reference changes.

## Fail-closed state preserved

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed

No Basic Pitch/V6 correctness, Modal, Vercel heavy-GPU, or L4 GPU work occurred in this review.
