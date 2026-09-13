# Songsterr Fresh V6 — Replacement Holdout Metadata Search

Status: **REFERENCE-BLIND METADATA/LICENSE/STRUCTURE RESEARCH ONLY — NO CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Why this search exists

Guitar-TECHS was rejected before correctness by the immutable reference-blind audit result in `SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md` (outcome C). V6 and its scoring framework remain frozen. This search may inspect only public metadata, licensing, file structure, annotation type and contamination risk for replacement untouched corpora.

No Basic Pitch, V6, reference matching or correctness is authorized by this checkpoint.

## Candidate 1 — GAPS (Guitar-Aligned Performance Scores) — REJECTED ON RIGHTS GATE

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
- Hugging Face dataset-card metadata declares MIT;
- total HF dataset size is approximately 16.4 GB.

Scientific strengths:
- genuine real-guitar performance rather than synthesis;
- polyphonic musical material;
- note-level aligned MIDI;
- large enough that V6's >=1,000-positive evidence-volume requirement is plausible;
- broad performer diversity.

### Rights/provenance resolution — decisive rejection

The official GAPS companion site states that the dataset contains copyright material and imposes explicit conditions that override any attempt to infer unrestricted audio rights from the Hugging Face repository-level MIT tag. The surfaced official conditions include:
- use only by the signing individual and members of that individual's research group/organisation;
- **non-commercial research purposes only**;
- GAPS or data enabling its reproduction may not be sold, leased, published or distributed to third parties without written permission from the GAPS administrator;
- attribution/citation is required for released research results.

The older Zenodo release also states that it distributed aligned MIDI/scores/downbeats while supplying YouTube URLs for the audio/video, confirming that the underlying performance recordings have a rights/provenance layer distinct from repository metadata.

Therefore the Hugging Face `license: mit` field is not sufficient authority to treat the included third-party performance audio as unrestricted MIT-licensed media. The explicit official GAPS terms are materially narrower and non-commercial.

Current disposition: **REJECTED as the V6 admission holdout under the current product-validation path unless the GAPS administrator later provides explicit written permission broad enough for this use. Do not download/audit or score GAPS.**

Because the rights gate is already terminal, the previously pending branch-specific GAPS contamination audit is no longer required for selection. No GAPS correctness has been run.

## Candidate 2 — EGFxSet

Public sources:
- https://zenodo.org/records/7044411
- https://egfxset.github.io/
- mirdata EGFxSet loader documentation

Public metadata says:
- real electric-guitar recordings captured through hardware;
- 8,970 five-second files total;
- 690 clean tones from all 138 playable notes across five pickup configurations;
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

The surfaced Zenodo record `6798338` is definitively a **conference paper** artifact containing only `79.pdf` (~680.6 kB), not the underlying multi-hour dataset. The University of Mons page likewise points to the paper and describes the dataset, but does not expose a stable dataset archive or license in the surfaced metadata.

Current blockers:
- actual downloadable dataset package location unresolved;
- dataset license unresolved;
- exact note annotation representation/timing resolution unresolved;
- immutable audio/reference file identities unresolved.

Current disposition: **promising scientific metadata lead but not audit-ready; do not infer a dataset package or license from the paper record.**

## Candidate 4 — EGSet12 — NEW LEADING OPEN-LICENSE LEAD, NOT YET SELECTED

Public sources:
- Zenodo record `11406378`: https://zenodo.org/records/11406378
- project page: https://robust-guitar-tabs.github.io/
- DAFx 2024 paper: “Leveraging Real Electric Guitar Tones and Effects to Improve Robustness in Guitar Tablature Transcription Modeling.”

Public metadata says:
- twelve **original, real solo electric-guitar performances**;
- 31.65 s average duration / 379.8 s total;
- diverse pop, funk, jazz and twelve-tone material with melodies and chord complexity;
- single professional guitarist, Sire T7 Telecaster and Yamaha B15 amplifier;
- microphone capture at 48 kHz, stereo channels duplicated from an effectively mono recording;
- twelve WAV/JAMS/GP triplets are deposited with stable per-file MD5 identities;
- JAMS is used publicly as the ground-truth tablature/reference representation in downstream evaluations;
- Zenodo API license metadata has been independently surfaced as `cc-by-4.0`, `access_right: open`, permitting commercial use with attribution.

Scientific/legal strengths:
- original performances made for the research project, unlike GAPS third-party/YouTube provenance;
- real electric guitar and real musical/polyphonic content;
- permissive CC BY 4.0 deposit-level license;
- stable small Zenodo corpus with explicit WAV/JAMS/GP identities;
- likely much simpler reference-blind inventory/alignment audit than GAPS.

Unresolved gates before selection:
1. **Untouched status:** perform a branch-specific contamination/history audit for any prior EGSet12 truth/correctness use on `songsterr-fresh-pipeline-v1`. Default-branch GitHub search is not sufficient.
2. **Evidence volume:** only 379.8 s / twelve tracks. The frozen V6 framework requires >=1,000 V6-positive events; public metadata does not provide a defensible pre-correctness event-count guarantee. Do not inspect JAMS event truth merely to optimize candidate choice without a preregistered reference-blind audit.
3. **Reference timing semantics:** confirm in a preregistered structural audit that JAMS note timing represents the performed audio closely enough for the frozen <=50 ms onset matcher, rather than only score/grid timing.
4. **Population diversity:** one performer means the frozen player-stratum rule would have only one player; this is permitted mechanically but weakens external-diversity evidence versus Guitar-TECHS/GAPS.

Current disposition: **best clean-license candidate currently surfaced, but not yet selected or downloaded. A branch-specific contamination audit plus a corpus-specific reference-blind inventory/alignment preregistration are required before touching its real WAV/JAMS truth.**

## Explicit exclusions

- GuitarSet: closed/revealed by prior V3 work; not eligible as a new untouched holdout.
- IDMT-SMT-Guitar: closed/revealed by prior V4 work; not eligible.
- Guitar-TECHS: outcome C; closed for V6 correctness and cannot be repaired/rescued.
- GAPS: explicit non-commercial/copyright-material terms conflict with this admission path absent written permission.
- Slakh/SynthTab: synthesized rather than untouched real-guitar performance holdouts.
- GuitarJam: clean real DI audio but currently no surfaced note-level ground-truth annotations, so not suitable for admission correctness as-is.

## Next metadata-only work

1. Perform a branch-specific contamination/history audit for EGSet12 on `songsterr-fresh-pipeline-v1`; do not rely on default-branch code search.
2. Continue searching for another permissively licensed real-guitar corpus with note-level performed timing and more diversity/volume than EGSet12.
3. Resolve GIHME's actual dataset download location/license/annotation representation; the paper record is not sufficient.
4. Keep EGFxSet as a narrow backup; determine whether a fixed/preregisterable note onset exists in metadata or recording protocol before considering an audit.
5. Select one candidate only after license/provenance/untouched status are defensible and the frozen evidence-volume gate is plausibly satisfiable without duplication/rescue rules.
6. Freeze a new corpus-specific reference-blind inventory/alignment preregistration before downloading/auditing real audio-reference pairs.
7. If that audit is structurally suitable, bind immutable identities into the already-frozen V6 scoring framework; otherwise reject without correctness.

No real-corpus correctness may occur during this search.
