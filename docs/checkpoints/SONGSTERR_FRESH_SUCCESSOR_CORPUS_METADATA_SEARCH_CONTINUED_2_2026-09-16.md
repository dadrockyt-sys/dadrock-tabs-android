# Songsterr Fresh — Successor Corpus Metadata Search, Continued 2

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Parent state: `c9cd333c0c307a655d6a729f136b19ad0294b394`
Scope: metadata/provenance research only

Status: **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**

## Purpose

Continue the strict successor-corpus search without opening candidate corpus media, annotation payloads, model output, or correctness results. The frozen target remains a genuinely new real-guitar population with deterministic performed-note onset + integer-MIDI-pitch truth, stable prospective source identities, a defensible research-use basis, and no prior Songsterr-fresh lineage exposure.

No Basic Pitch inference, Songsterr-fresh qualification, correctness scoring, candidate change, threshold change, or archived V143/Gomyway work is authorized or performed here.

## Newly reviewed candidates

### GIHME — Guitar Improvisations with Hexaphonic Multieffect

Public paper/record identities reviewed:

- title: `Guitar Improvisations with Hexaphonic Multieffect (GIHME) Dataset and Practice Analysis`;
- Zenodo conference-paper record: `6798338`, DOI `10.5281/zenodo.6798338`;
- conference-paper DOI/source also indexed as `10.5281/zenodo.6573697`;
- public repository named by the paper: `https://github.com/numediart/GIHME`.

Public metadata describes approximately ten hours of real guitarist improvisations from five guitarists using a hexaphonic-guitar/multieffect setup. The paper states that the dataset carries note, playing-technique, tuning, effect-configuration and interview annotations, and that dry/clean hexaphonic signals were recorded separately from effected signals.

Initial Songsterr-fresh repository-history searches found no prior commit hit for:

- `GIHME`;
- the full dataset title;
- `6798338`;
- `6573697`.

Therefore GIHME is not presently known to be lineage-exposed.

However, the public repository currently contains only a README stating `Information on this dataset will be uploaded soon.` The repository exposes no corpus release files, tags, or stable media/annotation identities. The Zenodo records surfaced in this review contain the paper, not a freezeable corpus archive. The paper also states that annotation work was not finished at publication time.

Disposition: **PROMISING / INITIAL-LINEAGE-CLEAN, BUT NOT PRE-READY — authoritative public corpus media/reference identities are not currently available to freeze prospectively.**

Do not treat GIHME as selected unless a stable authoritative corpus release becomes publicly identifiable and its exact note-onset/pitch annotation semantics and rights can be verified before media access.

No GIHME audio or annotation payload was opened.

### MMIP — Multi-Modal Instrument Performances

Public identities reviewed:

- title: `Multi-Modal Instrument Performances (MMIP): A Musical Database`;
- paper DOI: `10.1111/cgf.70025`;
- dataset host: `https://mmip.cs.ucy.ac.cy`;
- publication year: `2025`;
- repository license page: `CC BY-NC-SA 4.0` for repository content.

The online repository exposes twelve guitar performance rows, recorded with a PRS SE Paul Allender electric guitar, stereo WAV audio at 44.1 kHz, and MIDI downloads for most listed guitar rows. The paper describes the overall database as synchronized audio, motion, video, and MIDI data.

Initial Songsterr-fresh repository-history searches found no prior commit hit for:

- `MMIP`;
- `Multi-Modal Instrument Performances`;
- `cgf.70025`;
- `mmip.cs.ucy.ac.cy`.

Therefore MMIP is not presently known to be lineage-exposed.

Despite that clean provenance lead, MMIP is **scientifically invalid as the independent correctness reference for this Basic-Pitch proposal evaluation**. The authoritative paper states that guitars lack native MIDI output and that the guitar MIDI was obtained by audio-to-MIDI conversion. It specifically identifies NeuralNote as an audio-to-MIDI tool and states that NeuralNote internally uses Spotify's Basic Pitch model. The paper later states that guitar MIDI was included through audio-to-MIDI conversion software rather than hardware MIDI capture.

Because the Songsterr-fresh raw proposal generator under the frozen evaluation lineage is also `basic-pitch==0.4.0`, treating Basic-Pitch-derived guitar MIDI as independent ground truth would create a circular/self-referential evaluation. The paper's generic use of the term `ground truth` for MIDI does not remove this provenance problem for guitar.

Disposition: **REJECT FOR THIS BOUNDARY — real guitar audio and usable access exist, but the guitar MIDI reference is model-derived from the same audio and is not independent performed-note ground truth.**

No MMIP audio or MIDI payload was downloaded or opened.

### M-M / Perez-Carrillo multimodal guitar corpus

The 2019 `Finger-String Interaction Analysis in Guitar Playing With Optical Motion Capture` paper describes ten monophonic classical-guitar fragments, performed by two guitarists, with synchronized audio and motion data and approximately 1,500 plucks.

For this boundary it fails two independent requirements:

1. the paper's note onsets and pitch used by the analysis are extracted from the recorded audio by onset detection and pitch tracking rather than provided as an independent performed-note truth source; and
2. later MMIP literature explicitly describes the M-M Guitar Dataset as not publicly available.

Disposition: **REJECT FOR THIS BOUNDARY — no stable public corpus release and no independent note-birth truth established.**

No M-M Guitar media or annotation payload was opened.

## Search conclusion

This continuation produced no eligible successor:

- GIHME remains an interesting clean-lineage lead but cannot presently be frozen because the advertised public corpus release is not actually exposed through stable authoritative files;
- MMIP is accessible and initially lineage-clean, but its guitar MIDI is audio-to-MIDI/Basic-Pitch-derived and therefore unsuitable as an independent reference for evaluating a Basic-Pitch-based proposal path;
- the M-M/Perez-Carrillo corpus is unavailable and uses audio-derived note-event analysis rather than an independent reference.

Therefore:

- successor corpus selected: `none`;
- new evaluation PRE created: `no`;
- successor media opened: `0`;
- successor annotation payloads opened: `0`;
- successor model runs: `0`;
- successor correctness scores: `0`;
- candidate/threshold changes: `0`;
- V143/Gomyway activity: `0`.

## Next boundary

Continue metadata/provenance-only discovery. Prioritize lesser-known institutional, motion/performance, and newly released 2025–2026 guitar corpora, but require an **independent** note-onset + MIDI-pitch reference rather than a transcription generated from the same audio by Basic Pitch or another AMT model.

For any new promising candidate:

1. search full repository history for exact corpus name, DOI/record ID, source repository and distinctive identifiers before media access;
2. reject prior lineage exposure immediately;
3. verify stable public corpus identities and rights/access;
4. verify that pitch/onset truth is independent of the model path being evaluated and deterministically tied to the performed audio;
5. only then write a new prospective PRE;
6. update the canonical current-state checkpoint;
7. stop for fresh post-freeze authorization before any media/model/correctness execution.

Do not reopen a closed/exposed corpus by implication, do not weaken provenance, and do not use model-generated pseudo-ground-truth as the authoritative correctness target.

Archived V143/Gomyway remains untouched.
