# V168 — GOAT selection contract + metadata validator static-ready

Date: 2026-09-01 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **PRE-ACCESS STATIC PREPARATION COMPLETE / NO GOAT RESTRICTED BYTES / SCORING NOT ARMED**

## Scope

This checkpoint freezes and verifies the machine-checkable implementation of the pre-access GOAT integrity/selection preregistration. It does not admit GOAT assets, generate candidates, inspect restricted GOAT audio/reference content, or arm any scorer.

Controlling preregistration:
- `docs/checkpoints/V168_GOAT_INTEGRITY_SELECTION_PREREGISTRATION_20260901.md`
- creation commit `be69f777524ee24a1bb92e958f38e459689db4ae`.

## Frozen machine-readable contract

File:
- `validation/v168_holdout/goat_selection_contract_v168.json`
- creation commit `7e89671fe3dc14e91c52cc533d0e1ceb5605c16c`
- Git blob `ae3b33d89faa6cd31bb596b8553de75cb3320b9e`
- SHA256 `8c84eefa442d4c547180e1543cace9031ca2d801c1d04956893b3fb24e71096b`.

The contract freezes:
- Zenodo GOAT record `15690894`, DOI `10.5281/zenodo.15690894`, version `v1`;
- one `base_di` source role per independent base performance;
- target 3 independent works, minimum 2;
- Tier 1 official released-test-split selection;
- Tier 2 deterministic SHA256 fallback with salt `dadrock-v168-goat-v1-selection`;
- 50 ms scored-onset EOF tolerance;
- note-offset EOF overrun alone is not a failure;
- no repair;
- fixed integrity pass flags/failure reason codes;
- zero comparative score/candidate/scorer/GPU/main-production activity before selection freeze.

## Frozen metadata-only validator

File:
- `validation/v168_holdout/validate_goat_selection_receipt_v168.py`
- creation commit `263f9cdc8350f887f77fcc6021894ba2e00e26f6`
- Git blob `2f33b8c3df1caee63abe3493b64c16d6d4889b00`.

The validator:
- verifies the exact contract SHA256;
- accepts only a JSON metadata receipt plus the frozen contract;
- requires complete base-DI inventory and source/reference-pair inventory to be frozen score-blind;
- requires unique base IDs, normalized base IDs, source SHA256 values, and professional-reference SHA256 values;
- validates fixed integrity flags/reason codes;
- recomputes Tier 1 or Tier 2 selection deterministically;
- rejects selected-order/item drift;
- supports `INCONCLUSIVE_HOLDOUT_INSUFFICIENT` when fewer than 2 eligible works exist;
- has no audio/reference/candidate/scorer CLI surface.

## Static workflow

File:
- `.github/workflows/v168-goat-selection-static.yml`
- creation commit `bb5050522aada64304599b16ace99836a8f3eab8`
- Git blob `1d6eb422dcd02e36218ba32b11491bf123e6c5a5`.

GitHub Actions:
- run `33569762190`;
- job `100060930936`;
- head `bb5050522aada64304599b16ace99836a8f3eab8`;
- Ubuntu 24.04;
- Python 3.10.21;
- conclusion **SUCCESS**.

Verified in CI:
- exact contract Git blob matched;
- exact validator Git blob matched;
- exact contract SHA256 matched;
- validator Python compilation PASS;
- AST/static guard PASS with only stdlib imports;
- forbidden media/model/scoring imports absent;
- forbidden CLI flags for audio/reference/candidate/scorer/MIDI/Guitar-Pro absent.

Synthetic metadata self-test returned `SELF_TEST_PASS` and confirmed:
- Tier 1 selected synthetic IDs `item_20`, `item_67`, `item_21` under the frozen released-test ordering while a synthetic `item_96` EOF failure remained excluded by integrity rather than by item name;
- Tier 2 selected synthetic IDs `base-a1`, `base-z`, `base-c` under deterministic hash ordering;
- a one-work case returned `INCONCLUSIVE_HOLDOUT_INSUFFICIENT`;
- negative cases rejected: `selection-order-drift`, `comparative-score-leak`, `failed-eof-item-promoted-to-pass`;
- `audioRead=false`;
- `referenceNoteEventRead=false`;
- `candidateRead=false`;
- `scorerRead=false`;
- reference-facing score calls = 0.

The synthetic `item_67` / `item_96` names are test fixtures only. They prove the validator does not hard-code automatic exclusions for the public issue IDs; actual restricted-v1 items will be judged only from frozen metadata/integrity receipts if access is granted.

## Scientific state unchanged

- GOAT access request is still awaiting owner decision.
- No restricted GOAT bytes have been seen or hashed.
- No asset is admitted.
- No GOAT candidate generation exists or is armed.
- No GOAT/new-song scorer adapter exists or is armed.
- V168 prospective reference-facing score calls remain **0**.
- `main` / Production remain untouched.
- CPU-only boundary remains in force; no GPU/CUDA/Modal use occurred.

## Progress

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

The repository is now prepared through the metadata-selection validation boundary. The next primary event is external: explicit GOAT owner approval or denial. Approval must be checkpointed with exact non-secret grant wording/date/conditions before any restricted-v1 intake.
