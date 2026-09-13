# Songsterr Fresh V6 — Replacement Holdout Metadata Search

Status: **REFERENCE-BLIND METADATA/LICENSE/STRUCTURE RESEARCH ONLY — NO CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Why this search exists

Guitar-TECHS was rejected before correctness by the immutable reference-blind audit result in `SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md` (outcome C). V6 and its scoring framework remain frozen. This search may inspect only public metadata, licensing, file structure, annotation type and contamination risk for replacement untouched corpora.

No Basic Pitch, V6, reference matching or correctness is authorized by this checkpoint.

## Candidate 1 — GAPS (Guitar-Aligned Performance Scores)

Public sources:
- https://huggingface.co/datasets/xavriley/GAPS
- https://zenodo.org/records/17152440
- https://aim-qmul.github.io/GAPS/
- paper: arXiv:2408.08653

Public metadata says:
- real solo classical-guitar performances;
- approximately 14 hours;
- 300 performances;
- over 200 performers;
- high-resolution note-level aligned MIDI and MusicXML;
- Hugging Face v1.1 includes audio;
- Hugging Face dataset card declares MIT license;
- total HF dataset size is approximately 16.4 GB.

Scientific strengths:
- genuine real-guitar performance rather than synthesis;
- polyphonic musical material;
- note-level aligned MIDI;
- large enough that V6's >=1,000-positive evidence-volume requirement is plausible;
- broad performer diversity.

Current concerns / unresolved gates:
- original GAPS audio provenance is public performance audio linked to YouTube; the dataset-level MIT declaration may not necessarily grant independent copyright rights to every underlying performance recording. Rights/provenance must be resolved before this can be the admission holdout.
- acoustic/classical guitar differs from the desired electric-guitar/DI domain, though V6 itself is guitar-domain rather than electric-only.
- current branch has prior inspection of Xavier Riley's separate monophonic transcription model (`xavriley/hf_midi_transcription`), but no known GAPS correctness exposure. A branch-wide contamination audit must still be frozen and performed before use.

Current disposition: **scientifically strongest replacement lead, but licensing/audio-provenance review required before any corpus audit.**

## Candidate 2 — EGFxSet

Public sources:
- https://zenodo.org/records/7044411
- https://egfxset.github.io/
- mirdata EGFxSet loader documentation

Public metadata says:
- real electric-guitar recordings captured through hardware;
- 8,970 five-second files total;
- 690 clean DI-like tones from all 138 playable notes across five pickup configurations;
- 8,280 hardware-effect variants derived from those clean tones;
- string/fret/note and guitar/effect metadata;
- project/paper describes full open-access rights and CC BY 4.0.

Strengths:
- cleanly licensed real electric-guitar source;
- stable Zenodo identity;
- exact pitch identity can be inferred from string/fret;
- real hardware / isolated guitar.

Current concerns / unresolved gates:
- material is isolated single-tone recordings rather than musical/polyphonic performances;
- public metadata does not establish high-resolution note-onset timestamps inside each five-second WAV;
- only 690 unique clean performances exist; effect versions reuse the same underlying performances and cannot automatically be treated as independent admission evidence;
- therefore it may be too narrow or unable to meet the frozen >=1,000 V6-positive gate without scientifically questionable duplication.

Current disposition: **useful cleanly licensed structural backup, but likely too narrow for the official V6 admission holdout unless onset/reference and independence issues are resolved pre-correctness.**

## Candidate 3 — GIHME

Public source discovered:
- https://zenodo.org/records/6798338 (paper record)

Public metadata describes roughly ten hours of richly annotated real hexaphonic-guitar improvisations with note, playing-technique, tuning and effect-configuration annotations.

Current blocker: the surfaced Zenodo record is the conference-paper artifact rather than an obvious stable downloadable dataset package. Dataset location, license, exact annotation format and audio/reference identities remain unresolved.

Current disposition: **promising metadata lead but not audit-ready.**

## Explicit exclusions

- GuitarSet: closed/revealed by prior V3 work; not eligible as a new untouched holdout.
- IDMT-SMT-Guitar: closed/revealed by prior V4 work; not eligible.
- Guitar-TECHS: outcome C; closed for V6 correctness and cannot be repaired/rescued.
- Slakh/SynthTab: synthesized rather than untouched real-guitar performance holdouts.
- GuitarJam: clean real DI audio but currently no surfaced note-level ground-truth annotations, so not suitable for admission correctness as-is.

## Next metadata-only work

1. Resolve GAPS audio rights/provenance and exact v1.1 file identities without inspecting model correctness.
2. Search the current research branch/checkpoints for any prior GAPS corpus use or correctness exposure; model-code inspection alone is not automatically corpus contamination, but any GAPS truth/result use would disqualify it.
3. Resolve GIHME's actual dataset download location/license/annotation representation.
4. Keep EGFxSet as a narrow backup; determine whether a fixed/preregisterable note onset exists in metadata or recording protocol before considering an audit.
5. Select one candidate only after license/provenance/untouched status are defensible.
6. Freeze a new corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio-reference pairs.

No real-corpus correctness may occur during this search.
