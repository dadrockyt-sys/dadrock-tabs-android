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

### 2026-09-13 metadata refinement

Fresh public-source review confirms:
- the current Hugging Face repository explicitly advertises `license: mit` in its dataset-card metadata;
- the same repository states that v1.1 added the audio and currently exposes `audio/`, `match/`, `midi/`, `musicxml/`, scripts and metadata, with a total repository size of about 16.4 GB;
- surfaced Hugging Face history shows the v1.1 upload/README update on 2025-09-18, including commit `b4c89a3...` for the README state surfaced by public indexing;
- the older Zenodo release explicitly says it distributed aligned MIDI/scores/downbeats while providing YouTube URLs for audio/video, and recommends the newer Hugging Face version that includes audio.

This does **not** resolve the rights gate. No separate license notice or provenance statement was surfaced that explicitly says the dataset authors own or obtained redistribution/relicensing rights for every underlying third-party performance recording. Therefore the Hugging Face MIT label must not be interpreted as proven clearance of each audio recording without stronger evidence.

Contamination search note: repository code search for the exact corpus name `Guitar-Aligned Performance Scores` returned no result in the searchable repository index. Generic `GAPS` hits were unrelated variable names in archived analyzer files. This is weak supporting evidence only because GitHub code search is indexed against the repository default branch rather than a guaranteed exhaustive history of `songsterr-fresh-pipeline-v1`; do not treat it as the final contamination audit.

Current disposition: **scientifically strongest replacement lead, but still blocked on audio-rights/provenance and a branch-specific contamination audit. Do not download/audit GAPS audio yet.**

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

Public sources surfaced:
- conference-paper Zenodo record: https://zenodo.org/records/6798338
- University of Mons announcement describing the dataset/paper.

Public metadata describes roughly ten hours of richly annotated real hexaphonic-guitar improvisations with note, playing-technique, tuning and effect-configuration annotations, plus roughly five hours of interviews.

### 2026-09-13 metadata refinement

The current surfaced Zenodo record `6798338` is definitively a **conference paper** artifact containing only `79.pdf` (~680.6 kB), not the underlying multi-hour dataset. The University of Mons page likewise points to the paper and describes the dataset, but does not expose a stable dataset archive or license in the surfaced metadata.

Current blockers:
- actual downloadable dataset package location unresolved;
- dataset license unresolved;
- exact note annotation representation/timing resolution unresolved;
- immutable audio/reference file identities unresolved.

Current disposition: **promising scientific metadata lead but not audit-ready; do not infer a dataset package or license from the paper record.**

## Explicit exclusions

- GuitarSet: closed/revealed by prior V3 work; not eligible as a new untouched holdout.
- IDMT-SMT-Guitar: closed/revealed by prior V4 work; not eligible.
- Guitar-TECHS: outcome C; closed for V6 correctness and cannot be repaired/rescued.
- Slakh/SynthTab: synthesized rather than untouched real-guitar performance holdouts.
- GuitarJam: clean real DI audio but currently no surfaced note-level ground-truth annotations, so not suitable for admission correctness as-is.

## Next metadata-only work

1. Continue GAPS rights/provenance research, seeking an explicit statement covering redistribution/reuse of the included audio rather than relying solely on repository-level MIT metadata.
2. Perform a branch-specific contamination audit of `songsterr-fresh-pipeline-v1` for any prior GAPS corpus truth/correctness use before selection.
3. Resolve GIHME's actual dataset download location/license/annotation representation; the paper record is not sufficient.
4. Keep EGFxSet as a narrow backup; determine whether a fixed/preregisterable note onset exists in metadata or recording protocol before considering an audit.
5. Select one candidate only after license/provenance/untouched status are defensible.
6. Freeze a new corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio-reference pairs.

No real-corpus correctness may occur during this search.
