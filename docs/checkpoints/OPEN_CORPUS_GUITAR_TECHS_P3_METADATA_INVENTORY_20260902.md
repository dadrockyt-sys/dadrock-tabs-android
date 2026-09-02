# Open-Corpus Guitar-TECHS P3 Music — Metadata-Only Inventory

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Purpose

Freeze the structure and identity of a previously unused public music partition before any P3 reference-note content or candidate outcome is read. This is preparation for a V169-style reference-blind candidate-proposal experiment and is isolated from V168/GOAT.

## Public source / rights

- Dataset: Guitar-TECHS
- Zenodo record: `14963133`
- archive: `P3_music.zip`
- official MD5: `071ba80aecf00f4a31fbd167b3f22198`
- project site states all data are licensed **CC BY 4.0**.
- Zenodo describes P3 `Music` as full musical excerpts and documents synchronized per-string MIDI annotations; the public project site reports 12 P3 musical excerpts.

## Metadata-only inventory run

Workflow:
- `.github/workflows/open-corpus-guitar-techs-p3-metadata-inventory.yml`
- creation commit `2f8add621d0bd198b92303f05a03a05aaaffa3d3`.

GitHub Actions:
- run `33577994728`
- job `100086035966`
- conclusion **SUCCESS**.

Observed archive SHA256:
- `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`.

Inventory report:
- SHA256 `e2237f182f8db4f896748a87b16b449eb42a06de03c3f98f06ace87dbe1e3765`;
- artifact ID `9827368055`;
- artifact ZIP digest `ed423317d64b6741a920beab50f57f339687db4033f7bede593c1cf97bc598d4`.

## Structure observed without opening file contents

Archive entry count: **82**.

Extensions:
- 12 `.mid` files;
- 32 `.wav` entries (including Apple metadata/resource-fork entries in `__MACOSX`);
- 25 `.mp3` entries;
- 2 `.DS_Store` entries;
- 11 directory/no-extension entries.

Canonical P3 material paths establish complete indices `01` through `12` for:
- `P3_music/midi/midi_XX.mid`;
- `P3_music/audio/directinput/directinput_XX.wav`;
- `P3_music/audio/micamp/micamp_XX.wav`;
- `P3_music/video/ego/ego_XX.mp3`;
- `P3_music/video/exo/exo_XX.mp3`.

Thus all 12 excerpts have an unambiguous MIDI + direct-input + mic/amp filename binding by the same two-digit index. The future first bridge experiment will use all 12 works; no content-based song selection is needed.

## Boundary counters

The inventory workflow only read ZIP central-directory metadata/path information.

- file contents read by inventory code: **false**;
- P3 reference note events read: **false**;
- P3 candidate generated: **false**;
- P3 score calls: **0**;
- V168 reference-facing score calls: **0**;
- V168 policies modified: **false**;
- GOAT holdout selection modified: **false**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

## Next boundary

Before extracting/reading any P3 MIDI note events or running any P3 candidate inference, freeze the full reference-blind proposal/correction/scoring contract. Candidate predictions must be generated and cryptographically frozen before the reference MIDI files are extracted for scoring.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
