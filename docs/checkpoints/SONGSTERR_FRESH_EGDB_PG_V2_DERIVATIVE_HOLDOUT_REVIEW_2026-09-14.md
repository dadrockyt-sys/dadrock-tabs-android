# Songsterr Fresh V6 — EGDB-PG v2 derivative holdout review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/reference/rights review only; no candidate media access and no V6 correctness.

## Frozen authority

V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28` / blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`, and external scoring framework commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

A replacement holdout must, before media access, have defensible product-validation audio rights, real guitar, immutable independent performed note-level onset+pitch truth not reconstructed from the evaluated audio, plausible >=1,000 V6-positive capacity without derivative inflation, and defensible untouched status.

## Current authoritative public evidence

Zenodo record `10.5281/zenodo.19789500` (v2; created 2026-04-27, modified 2026-04-29) describes EGDB-PG and EGDB-NDSP as datasets for **amplifier-rendered electric guitar transcription**. It states that EGDB-PG contains 256 presets; the public record hosts a 135.4 GB FLAC bundle (`EGDB_FLAC_bundle.zip`, MD5 `4c0e0801b966084002178d738c34f208`) and a preset archive (`random_presets_json.rar`, MD5 `a2c0359c1fc40053e54faae242db5335`). The record's Rights section exposes no explicit license value.

Primary record: https://zenodo.org/records/19789500

The associated 2025 paper, `Towards Generalizability to Tone and Content Variations in the Transcription of Amplifier Rendered Electric Guitar Audio` (arXiv:2504.07406), introduces EGDB-PG specifically to increase amplifier/cabinet tone diversity. It is therefore a rendered/augmented descendant of the already-governed EGDB performance population, not a newly captured independent real-guitar holdout population.

Primary paper: https://arxiv.org/abs/2504.07406

The original EGDB work (`Towards Automatic Transcription of Polyphonic Electric Guitar Music: A New Dataset and a Multi-Loss Transformer Model`, ICASSP 2022 / arXiv:2202.09907) describes 240 tablature performances rendered with multiple tones and a collection pipeline using hexaphonic activity signals. EGDB itself is already closed in the canonical V6 state for reference-provenance/rights reasons.

Primary original paper: https://arxiv.org/abs/2202.09907
Institutional record: https://scholars.lib.ntu.edu.tw/entities/publication/cd18bf56-ad04-465d-9c1e-ac7748a7b227

## Frozen-gate assessment

1. **Product-validation audio rights: FAIL / UNESTABLISHED.** The current Zenodo v2 record is public/open but does not expose an explicit license value in its Rights section. Public downloadability is not equivalent to a permissive product-validation performance-audio license.
2. **Real guitar: derivative source only.** EGDB-PG renders existing EGDB guitar performances through amplifier/cabinet presets. It does not establish a new independent performance population.
3. **Independent performed onset+pitch truth: FAIL under existing EGDB governance.** EGDB-PG inherits the underlying EGDB reference lineage; the v2 release provides no new independent physical/performed note-reference stream that cures the existing EGDB provenance failure.
4. **Population capacity without derivative inflation: FAIL as a new holdout.** The 256 presets are tone renderings of the same underlying performance content. Presets cannot be counted as independent real performances or independent V6 evidence.
5. **Untouched status: FAIL as replacement holdout.** EGDB/EGDB-PG are already part of the governed research history and cannot become a newly untouched external holdout by publishing additional renderings or package versions.

## Decision

`REJECT_EGDB_PG_V2_AS_V6_REPLACEMENT_HOLDOUT`

The 2026 public v2 release is useful for reproducibility and tone-robustness research, but it does not change V6 admission. It is a derivative rendering corpus over the already-governed EGDB population, lacks a newly independent performed onset+pitch reference, cannot inflate population by amplifier presets, and currently exposes no explicit permissive license value on the authoritative Zenodo record.

Do not download the 135.4 GB media bundle for V6 holdout evaluation. Do not run Basic Pitch/V6 correctness. Do not use rendered presets as independent observations. Do not reopen EGDB correctness/history.

## Guitar-TECHS re-verification before this review

Official Guitar-TECHS audit run `34754519541`, job `103716527380`, remains `completed/success`.
Artifact `guitar-techs-v6-alignment-inventory`, ID `10317695640`, remains live/unexpired.
GitHub-reported artifact digest: `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`.
The artifact ZIP was downloaded again in this continuation and independently SHA-256 checked to the same digest. The merged JSON SHA-256 remains `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`; 104 DI/MIDI pairs and 18,934 reference events remain recorded; anomaly totals remain 5 same-key overlaps, 7 unmatched note-ons, 0 unmatched note-offs; all 104 alignment statuses remain `OK`; frozen decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION` and `datasetStructurallySuitable:false`.

No Guitar-TECHS correctness, repair, duplicate audit run, Modal, Vercel heavy-GPU, or L4 work occurred.

## Authority after this checkpoint

Fail closed unchanged: `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration remains paused/unchanged; Policy C remains `UNENROLLED`; protected-song execution remains embargoed.
