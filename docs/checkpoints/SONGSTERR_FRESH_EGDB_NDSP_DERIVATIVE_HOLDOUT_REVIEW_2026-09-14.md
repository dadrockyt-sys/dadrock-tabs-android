# Songsterr Fresh V6 — EGDB-NDSP Derivative Holdout Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference review only; no candidate media access; no Basic Pitch/V6 correctness.

## Authority

Frozen V6 method remains governed by `SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` (`f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`) and implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28` / blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. Frozen external scoring framework remains commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

## Public evidence reviewed

1. Zenodo record `19789500` describes one FLAC bundle containing **EGDB-PG and EGDB-NDSP**, both explicitly characterized as datasets for *amplifier-rendered electric guitar transcription*. The record gives no explicit license value in the Rights section.
2. The authors' public demo/project page states that EGDB-NDSP is the evaluation counterpart to EGDB-PG and consists of audio rendered with six out-of-domain Neural DSP amplifier presets: two low-gain, two crunch, and two high-gain presets.
3. The same project page states that training data consists of EGDB-PG and that the EGDB-NDSP clips are rendered using Neural DSP specifically to provide unseen amplifier tones. This establishes EGDB-NDSP as a tone-domain rendering/evaluation transformation, not a newly recorded performance population.

## Frozen-gate analysis

- **Real guitar source:** underlying source population derives from the EGDB pipeline, but EGDB-NDSP itself is a rendered view rather than a new independently performed corpus.
- **Independent performed note-level onset+pitch truth:** no new independent performed-event reference stream is established for EGDB-NDSP. Any labels inherit the underlying EGDB symbolic/reference authority rather than establishing a fresh independent holdout truth source.
- **Population capacity:** the six amplifier presets cannot multiply the number of independent guitar performances. Multiple tonal renders of the same underlying performance count as derivative views only.
- **Untouched status:** EGDB is already governed/revealed in this project, so a derivative render of that population cannot be treated as an untouched external holdout.
- **Rights:** the current Zenodo v2 Rights section exposes no explicit license value sufficient to establish product-validation performance-audio rights.

## Decision

**REJECT EGDB-NDSP AS A V6 REPLACEMENT HOLDOUT.**

The decisive reason is structural/governance-level: EGDB-NDSP is a six-preset out-of-domain amplifier-rendered evaluation set derived from the already-governed EGDB population. It contributes tonal-domain variation but no new independent real-performance population and no new independent performed onset+pitch truth. Its rendered variants must not inflate the frozen V6 evidence count. Untouched status also fails because the source population is already governed.

No candidate media was downloaded. No Basic Pitch, V6 correctness, Modal, Vercel heavy-GPU, or L4 compute was used.

## Fail-closed state

`modelValidationComplete:false`
`customerEligibleEvents:0`
`mayAdvanceDelivery:false`
Duration authority unchanged/paused.
Policy C remains `UNENROLLED`.
Protected-song execution remains embargoed.
