# Songsterr Fresh V6 — SJSU Patil 2025 Corpus Metadata Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/rights/reference review only; no media acquisition and no correctness exposure.

## Authority and frozen boundary

This review is subordinate to:

- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
- `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`
- frozen V6 implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`
- `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`

No V6 constants, Basic Pitch settings, evaluated-audio path, matcher, tolerances, uncertainty policy, admission gate, strata rule, or deferred-reveal/single-run rule is changed here.

## Candidate lead

Institutional source: San Jose State University ScholarWorks, Ritwik Patil, *Automatic Guitar Transcription of Polyphonic Music* (Fall 2025 master's thesis):

- https://scholarworks.sjsu.edu/etd_theses/5745/
- DOI: https://doi.org/10.31979/etd.qx8v-u985

The institutional abstract states that the model was trained and evaluated on a large annotated corpus of **75,579 songs totaling more than 5,134 hours**, with stereo audio input and detailed guitar outputs including string, fret, timing and expressive technique labels.

This is potentially large enough to attract attention as a replacement-holdout lead, but corpus size alone is not an admission criterion.

## Pre-media V6 gate review

### Gate 1 — explicit usable/permissive performance-audio rights

**FAIL / not established.**

The authoritative institutional thesis landing page identifies the thesis and describes the dataset used in the research, but it does not expose a corpus-level public license granting product-validation use of the underlying performance audio. No authoritative public corpus release with immutable package identity and explicit permissive performance-audio rights was located in this review.

### Gate 2 — real guitar

**UNRESOLVED.**

The abstract discusses stereo audio and guitar transcription across varied genres/recording conditions, but the public landing-page metadata does not establish that the 75,579-song corpus is a population of newly captured real-guitar performances suitable for isolated-guitar V6 evaluation rather than existing recordings, mixtures, symbolic/rendered material, or some combination. Do not infer a qualifying real-guitar population from task language alone.

### Gate 3 — independent performed note-level onset + pitch truth

**FAIL / not established.**

The landing-page metadata does not establish an independent physical/performance reference stream for note identity and timing. It reports detailed target annotations, but does not establish that onset and pitch truth were captured independently of the evaluated audio rather than transcribed, aligned, derived, or reconstructed from it. Under the frozen V6 rules, unspecified annotation provenance is insufficient.

### Gate 4 — plausible >=1,000 V6-positive capacity without duplicate/effect inflation

**UNRESOLVED despite nominal scale.**

The reported 75,579 songs / 5,134+ hours would be nominally large, but there is no frozen public population manifest proving unique real-guitar performances, isolated-guitar suitability, duplicate handling, or the expected V6-positive population. Raw headline size cannot satisfy this gate.

### Gate 5 — defensible untouched status

**FAIL for this project.**

The thesis explicitly reports training and evaluation on the corpus. Even if an independently released subset existed later, the current public evidence does not identify a previously untouched, immutable holdout partition suitable for this project. A future genuinely new external split would require separate evidence before any media access.

## Decision

**REJECT AS A CURRENT V6 REPLACEMENT HOLDOUT / METADATA-ONLY LEAD.**

Reasons are independent and fail closed:

1. no authoritative public corpus package with explicit permissive performance-audio rights was established;
2. independent performed note-level onset+pitch reference provenance is not established;
3. the qualifying real-guitar/isolation population and duplicate semantics are not established;
4. no defensible untouched external holdout partition is established.

No media was accessed, downloaded, inspected, decoded or scored. No Basic Pitch/V6 correctness was run. This decision does not reopen GuitarSet/V3, IDMT/V4, GOAT/reference scoring, V143/Gomyway, duration work, protected-song execution, main or Production.

## Guitar-TECHS required first-check state

Before this review, official Guitar-TECHS audit run `34754519541`, job `103716527380` was reverified as `completed/success` on `songsterr-fresh-pipeline-v1`.

Exact artifact remains live/unexpired:

- name: `guitar-techs-v6-alignment-inventory`
- artifact ID: `10317695640`
- GitHub archive digest: `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
- run head: `f3c9d4a88740146918c34a3538c565f21079f3bf`

Frozen decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`. Guitar-TECHS correctness remains forbidden.

## Authority after this checkpoint

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
- no Modal, Vercel heavy-GPU, or L4 work was used or authorized

Next allowed action remains metadata/license/reference research for genuinely new untouched real-guitar holdout evidence. If a future candidate clears all five pre-media gates, freeze candidate-specific reference-blind inventory/alignment rules before media access.