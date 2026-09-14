# Songsterr Fresh V6 — TART 2026 Corpus Delta Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/literature-only replacement-holdout research. No media acquisition, Basic Pitch, V6 correctness, GOAT/reference scoring, protected-song execution, duration research, Modal, Vercel heavy-GPU, or L4 GPU.

## Authority preserved

Frozen V6 method remains `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.

Frozen external scoring framework remains `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS official reference-blind alignment/inventory run `34754519541`, job `103716527380`, remains `completed/success`; artifact `10317695640` (`guitar-techs-v6-alignment-inventory`) remains unexpired with GitHub-reported digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`. Frozen decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no correctness run is authorized.

## New evidence reviewed

A newly posted September 10, 2026 paper, **TART: A Modular Tool for Technique-Aware Audio-to-Tablature Guitar Transcription** (arXiv:2609.11904), evaluates on GuitarSet, EGDB, Noisy GuitarSet, and Noisy EGDB. The paper reports the noisy benchmarks as augmented versions of the already-known corpora rather than a new independent real-guitar capture corpus.

Primary source:
- arXiv abstract page: https://arxiv.org/abs/2609.11904

## Frozen-gate assessment

TART does **not** surface a new untouched external holdout that can enter V6 admission:

1. GuitarSet is explicitly out of scope / previously revealed under the standing authority.
2. EGDB is already governed as rights-unestablished with audio-derived/expected-score onset construction.
3. Noisy GuitarSet and Noisy EGDB are derived/augmented benchmarks, not new independent real-guitar performances with independent performed note-level onset+pitch truth.
4. Derived noisy versions cannot be counted as new independent evidence and cannot repair the underlying corpus provenance/rights gates.
5. TART therefore creates no basis to reopen GuitarSet/V3, EGDB, GOAT/reference scoring, or any correctness exposure.

## Decision

**NO NEW ADMISSIBLE HOLDOUT FROM TART 2026.**

This is a metadata-only delta result. It does not alter any V6 constant, Basic Pitch setting, matcher, tolerance, uncertainty rule, admission gate, stratum, deferred-reveal rule, or single-run rule.

Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed

No candidate media was acquired and no real Guitar-TECHS/V6 correctness was exposed.
