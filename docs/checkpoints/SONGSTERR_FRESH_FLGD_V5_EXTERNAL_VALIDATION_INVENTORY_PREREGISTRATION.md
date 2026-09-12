# Songsterr Fresh FLGD V5 External Validation — Stage A Inventory Preregistration

Status: **FROZEN BEFORE DOWNLOAD / INVENTORY ONLY / NO CORRECTNESS SCORING**

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This document selects the candidate external corpus for V5 and authorizes only metadata/file inventory. It does **not** authorize Basic Pitch inference, V5 classification, estimate/reference matching, correctness metrics or admission decisions.

## Candidate corpus identity

Dataset: François Leduc Guitar Dataset (FLGD)

Canonical source for this V5 evaluation candidate:
- provider: Hugging Face dataset repository owned by `xavriley` (Xavier Riley, dataset co-author)
- repository: `xavriley/FrancoisLeducGuitarDataset`
- exact revision: `a38306c244b3ea81496ad58b4514622185e58211`
- revision is the verified `Update README.md` commit from 2025-09-18
- current repository size reported by the provider: about 282 MB
- current repository card declares license `mit`
- current repository card describes audio + aligned MIDI for 79 solo-guitar performances.

The older Zenodo v1.0.0 record is **not** the selected artifact. That older record is restricted but explicitly states that a newer version is freely available at the Hugging Face repository and recommends that version for future research. V5 binds only the exact Hugging Face revision above.

No FLGD correctness result has been viewed or generated in this V5 line as of this preregistration.

## Untouched-holdout rationale

Before selecting FLGD, repository checkpoint history was screened for previously used guitar corpora. GuitarSet, IDMT and Guitar-TECHS are already historical/observed and are excluded from untouched V5 admission validation. No prior FLGD checkpoint/result was identified in the active Songsterr Fresh line.

FLGD is selected because it provides real solo-guitar audio with aligned MIDI annotations while remaining distinct from the previously observed GuitarSet/IDMT/Guitar-TECHS correctness corpora.

## Stage A allowed operations

Stage A may only:
- obtain the exact revision outside the Git repository;
- verify the checked-out/snapshot revision identity;
- enumerate all files recursively;
- record relative paths, file sizes and SHA-256 hashes;
- classify file extensions;
- inspect non-signal container/header metadata needed for later planning;
- identify exact audio/MIDI stem pairings mechanically;
- inspect `metadata.csv` column names/row count/value domains needed to freeze population/splits;
- inspect MIDI container/header structure and count syntactic MIDI events if needed for annotation planning;
- emit a deterministic JSON inventory outside the repository.

Stage A MUST NOT:
- invoke Basic Pitch;
- invoke V5;
- invoke Demucs;
- analyze audio samples for pitch or correctness;
- align estimates to MIDI/reference notes;
- compute precision, recall, F1, accuracy, admission metrics or any V5 correctness statistic;
- exclude files based on model behavior/performance;
- inspect the protected song;
- change model/duration/customer authority.

## Frozen inventory population rule

Inventory every regular file in exact HF revision `a38306c244b3ea81496ad58b4514622185e58211`, excluding only VCS implementation metadata under `.git/` if the revision is obtained by Git clone.

Do not selectively omit dataset files based on extension, performer, split, duration, audio quality or model behavior.

## Pairing rule for Stage A report

For planning only, form candidate audio/MIDI pairs when:
- one file lives under top-level `audio/`;
- one file lives under top-level `midi/`;
- their leaf filename stems are exactly equal after removing only the final extension;
- each stem maps to exactly one audio file and exactly one MIDI file.

Ambiguous/unpaired files are reported, not silently dropped.

No pairing created at Stage A becomes an admission inclusion automatically. Final inclusion/exclusion must be frozen in a later Stage B preregistration before correctness scoring.

## Stage A report requirements

The deterministic inventory report must record at minimum:
- dataset/repository/revision identity;
- inventory tool contract/version;
- total regular-file count and total bytes;
- extension counts;
- SHA-256 of every regular file;
- exact audio/MIDI one-to-one pair count;
- unpaired and ambiguous counts;
- metadata.csv SHA-256, columns and row count if present;
- audio extension counts and non-signal header/container facts available without sample-domain analysis;
- MIDI extension counts and basic SMF header facts;
- policy boundary proving no inference/classification/matching/correctness work occurred.

The report itself must be SHA-256 bound before Stage B is written.

## Licensing/use posture

The selected exact Hugging Face release declares MIT. The evaluation corpus must remain outside the application repository and must not be redistributed or shipped with product artifacts. This preregistration authorizes local evaluation/inventory use only and does not make any broader claim about third-party works beyond the provider's current release terms.

## What happens after Stage A

After the real inventory report is generated and reviewed, but before any correctness result:
1. freeze exact eligible population/mechanical exclusions;
2. freeze MIDI annotation parsing/time semantics;
3. freeze Basic Pitch runtime/settings;
4. freeze V5 implementation/source identities;
5. freeze matching protocol, uncertainty method, minimum positive count and overall/stratum gates;
6. implement a controlled validation harness and synthetic/contract CI with no real FLGD correctness access;
7. only then permit one official FLGD correctness run.

## Policy boundary

Stage A cannot change authority. It must retain:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- protected song unused.
