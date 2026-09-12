# Songsterr Fresh — FLGD V5 External Validation Stage A Result

Status: **IMMUTABLE INVENTORY-ONLY RESULT / NO CORRECTNESS SCORING**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This record freezes the one real Stage A inventory of the selected François Leduc Guitar Dataset (FLGD) release before any Basic Pitch inference, V5 classification, estimate/reference matching, or correctness metric.

It is not admission evidence. It establishes only dataset identity, canonical file membership, metadata structure, container/header structure, and pairability needed to preregister later stages.

## Frozen source / execution

Selected dataset:
- Hugging Face repository: `xavriley/FrancoisLeducGuitarDataset`
- canonical origin: `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact Git revision: `a38306c244b3ea81496ad58b4514622185e58211`
- release license declaration: MIT

Inventory preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_INVENTORY_PREREGISTRATION.md`

Inventory implementation:
- `scripts/songsterr-fresh/inventory_flgd_v5_external_validation.py`
- origin-binding hardening commit `43cfb6785fa36cf20eaedee986e7176d7128867c`

One-shot real inventory workflow:
- `.github/workflows/songsterr-fresh-flgd-v5-real-inventory.yml`
- workflow/source commit `77a0c8fddeecaf6e361e4c95772e2e80378258b9`
- workflow run `34719034991`
- job `103621353045`
- result: SUCCESS

The dataset was cloned into GitHub runner temporary storage outside the application repository. Git LFS objects were materialized, exact HEAD/origin/clean-worktree provenance was verified, and only the frozen inventory tool was executed.

## Immutable report identity

Inventory report SHA-256:
`f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`

Uploaded report-only artifact:
- artifact name: `flgd-v5-stage-a-inventory`
- artifact ID: `10305947650`
- artifact ZIP digest: `a7ea158d81c66589b24433991cb1effff8560c8decf44523e139b846bfbcce07`
- retention configured by workflow: 30 days

The artifact contains only the JSON inventory report, not dataset media.

## Observed inventory

Whole selected checkout, excluding `.git/` implementation metadata:
- regular files: `281`
- total bytes: `281,515,466`
- extension counts:
  - `.csv`: `1`
  - `.json`: `79`
  - `.log`: `1`
  - `.md`: `1`
  - `.mid`: `106`
  - `.mp3`: `88`
  - `.pkl`: `2`
  - `.py`: `1`
  - no extension: `2`

Canonical corpus directories:
- `audio/`: `79` MP3 files
- `midi/`: `79` MIDI files
- exact one-to-one canonical audio/MIDI leaf-stem pairs: `79`
- ambiguous canonical stem groups: `0`
- unpaired canonical audio: `0`
- unpaired canonical MIDI: `0`

Additional noncanonical material exists outside the canonical `audio/` and `midi/` roots, including `test_set/` duplicates and model-output material. No such material is authorized as reference truth. Stage B must bind population only through canonical metadata rows and canonical paths.

## metadata.csv

Identity:
- SHA-256 `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`
- rows: `79`
- columns, in observed order:
  - `split`
  - `midi_filename`
  - `audio_filename`
  - `guitar_type`
  - `slice_id`
  - `artist`
  - `name`

Observed value domains include:
- `split`: `test`, `train`, `validate`
- `guitar_type`: `acoustic`, `electric`, `electric-band`, `nylon`

Stage A did not use those metadata labels to select favorable outcomes; no outcomes existed.

## Container / MIDI-header observations

Canonical audio is MP3, therefore the inventory intentionally performed no sample-domain audio analysis and emitted no WAV-header signatures.

MIDI SMF header signatures were inventoried structurally. The checkout contains canonical `midi/` references plus additional MIDI files elsewhere; therefore Stage B must restrict reference identity to canonical metadata-named MIDI files and must not treat `test_set/` or model-output MIDI as truth.

Observed repository-wide MIDI header groups included:
- format 1 / TPQ 220 / 2 tracks: `88`
- format 1 / TPQ 480 / 2 tracks: `9`
- format 1 / TPQ 480 with other track counts also present in small numbers.

These repository-wide counts are structural diagnostics only; Stage B must establish exact canonical-reference timing semantics separately before correctness scoring.

## Policy boundary

The real Stage A run verified exactly:
- `basicPitchInvoked:false`
- `v5ClassifierInvoked:false`
- `demucsInvoked:false`
- `audioSamplesUsedForPitchAnalysis:false`
- `estimateReferenceMatchingPerformed:false`
- `correctnessMetricComputed:false`
- `protectedSongUsed:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`

No correctness result has been produced for FLGD.

## Consequence / next boundary

Stage A is complete.

Before any Basic Pitch or V5 correctness run, Stage B must be preregistered and must mechanically establish:
1. the exact 79 metadata rows and canonical `audio/` / `midi/` identities;
2. exact `train` / `validate` / `test` membership and guitar-type counts from metadata only;
3. exact syncpoint membership/format and authoritative timing semantics without computing correctness;
4. an explicit prohibition on `test_set/` duplicates/model outputs as reference truth;
5. exact canonical reference-MIDI structural/timing semantics;
6. any mechanically required exclusions before results;
7. a hash-bound Stage B population manifest.

Only after those metadata/timing facts are frozen may a separate final scoring preregistration define Basic Pitch runtime/settings, V5 execution, matching, uncertainty, minimum positives, pass gates and provenance.
