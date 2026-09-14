# Songsterr Fresh V6 — 2026-09-14 Post-Handoff Corpus Delta Sweep

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Starting branch head verified before work: `27acf1536557c42188fc74fe19079e54f2507623`
Canonical state checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## Scope

This was a metadata-only continuation under the frozen V6 replacement-holdout gates. No candidate media was accessed, downloaded, scored, decoded, aligned, repaired, tuned, or used for correctness. No Basic Pitch/V6 run occurred. No Modal, Vercel heavy-GPU, L4, procurement, performer/vendor contact, hiring, recording, or data acquisition occurred.

Archived V143/Gomyway work was not resumed. Archived GOAT/reference scoring was not reopened; GOAT appearances below are literature-only observations.

## Frozen pre-media gates

A replacement holdout must simultaneously establish, before media access:

1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

## Delta search performed

Targeted current-literature and dataset searches covered combinations of:

- guitar dataset + MIDI + audio + simultaneous performance;
- guitar transcription dataset + real guitar + 2025/2026;
- hexaphonic guitar dataset + MIDI/audio;
- Fishman TriplePlay / synchronized MIDI guitar datasets;
- September 2026 / ISMIR 2026 guitar transcription and dataset papers;
- recent amplifier-rendered electric-guitar dataset work.

The purpose was not to repeat the broad corpus inventory, but to identify genuinely new primary evidence, rights changes, or an independently captured performed note-level reference that could materially change a hard gate.

## Findings

### TART / September 2026 literature

`TART: A Modular Tool for Technique-Aware Audio-to-Tablature Guitar Transcription` (arXiv:2609.11904, 2026-09-10) evaluates GuitarSet, EGDB, Noisy GuitarSet, and Noisy EGDB. It does not introduce a new independently captured real-guitar corpus, a new independent performed onset+pitch reference, or a new rights chain. This is consistent with the existing TART checkpoint and does not change replacement-holdout status.

### Noise2Fret / GOAT mentions

Recent search surfaces continue to cite GuitarSet and GOAT as evaluation populations. These are literature mentions only. They do not establish a new population or new rights/reference evidence, and they do not reopen archived GOAT/reference scoring.

### EGDB-PG / EGDB-NDSP

The current project page for `Towards Generalizability to Tone and Content Variations in the Transcription of Amplifier Rendered Electric Guitar Audio` continues to describe EGDB-PG/EGDB-NDSP as amplifier-rendered material derived from the EGDB performance population, with dataset links supplied on request. The paper/project evidence therefore remains consistent with the existing derivative-holdout rejection: amplifier/preset multiplication does not create new independent performances, does not create a new independent performed onset+pitch truth stream, and does not cure untouched-status failure.

### Other surfaced datasets

Searches resurfaced GuitarSet, Guitar-TECHS, GAPS, IDMT-SMT-Guitar, GIHME, the Five guitar dataset, and older/non-guitar symbolic or synthetic datasets. Each is already governed by the canonical checkpoint or fails at least one frozen pre-media gate. No newly surfaced primary source established all five gates simultaneously.

## Outcome

**NO NEW ADMISSIBLE REPLACEMENT HOLDOUT FOUND.**

No candidate cleared all five frozen pre-media gates. Therefore:

- do not access candidate media on the basis of this sweep;
- do not run Basic Pitch/V6 correctness;
- do not bind a new holdout population;
- do not alter frozen V6/scoring settings;
- do not rescue a candidate with evaluated-audio-derived timing or derivative/effect multiplication;
- keep purpose-built independent-sensor capture as design-only unless the user explicitly authorizes spending/contact/acquisition.

## Primary/current sources checked

- TART arXiv: https://arxiv.org/abs/2609.11904
- EGDB-PG/NDSP project page: https://ss12f32v.github.io/Guitar-Transcription-with-Amplifier/
- EGDB-PG paper: https://arxiv.org/abs/2504.07406
- Guitar-TECHS Zenodo: https://zenodo.org/records/14963133
- GuitarSet Zenodo: https://zenodo.org/records/3371780
- GIHME Zenodo: https://zenodo.org/records/6798338
- Five guitar dataset Zenodo: https://zenodo.org/records/4988354

## Next allowed action

Continue metadata-only research only when genuinely new primary evidence, an authoritative rights change, or a newly established independent performed onset+pitch reference appears. If a candidate ever clears all five gates, stop before media access and freeze a candidate-specific reference-blind inventory/alignment preregistration first.
