# Songsterr Fresh — IDMT V4 External Validation Inventory Preregistration

Status: **STAGE A REOPENED / INVENTORY ONLY / NO CORRECTNESS SCORING YET**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Authorization

The user explicitly reopened V4 holdout/external validation after V4 synthetic development was frozen.

This document authorizes only the first fail-closed stage needed to turn the public IDMT metadata into an exact future holdout contract. It does **not** authorize a correctness result.

## Frozen dataset identity

Dataset: **IDMT-SMT-Guitar Dataset**

- Zenodo version: `1.0.0`
- DOI: `10.5281/zenodo.7544110`
- archive: `IDMT-SMT-GUITAR_V2.zip`
- expected archive MD5: `06796e08731bccffaed6ae59361486e4`
- public source/license authority: Fraunhofer IDMT dataset page; CC BY-NC-ND 4.0

Only this archive/version is authorized for Stage A.

## Stage A permitted operations

After verifying the exact archive MD5, Stage A may:

1. list every ZIP member path in sorted order;
2. record each member's uncompressed size and ZIP CRC32;
3. compute SHA-256 for individual archive members without modifying them;
4. identify directory/subset structure from member paths;
5. identify `.wav` / `.xml` stem pairings and unpaired members;
6. inspect WAV container headers only, including channel count, sample rate, sample width, frame count and compression type;
7. parse XML syntax and record structural information needed for a future parser contract, including root tags, element/tag paths, attribute names, and whether element text is present;
8. preserve a bounded set of representative XML files outside the repository for manual schema/units inspection if needed;
9. record archive-level SHA-256 in addition to the preregistered MD5;
10. write all inventory output outside the repository.

## Stage A forbidden operations

Stage A MUST NOT:

- invoke Basic Pitch;
- invoke the V4 classifier on IDMT audio;
- invoke Demucs;
- read audio sample values for scoring or signal analysis;
- classify any event as correct/incorrect;
- pair any model estimate to any reference note;
- compute precision, recall, F-score, Wilson bounds, admission gates, or any other correctness metric;
- inspect GuitarSet V3 event-level errors for V4 design;
- change the frozen V4 evaluator or synthetic method;
- run the protected song;
- change duration authority;
- set model validation/customer eligibility/delivery state.

No Stage A output may be interpreted as evidence that V4 is accurate.

## Inventory output contract

The canonical inventory report must contain at minimum:

- archive filename;
- archive MD5 and SHA-256;
- total ZIP member count;
- sorted exact member manifest;
- counts by file extension;
- exact WAV/XML stem-pair table;
- list of unpaired WAV/XML members;
- WAV-header signature counts;
- XML structural signature counts;
- subset/top-level directory counts;
- an explicit policy boundary proving no model/scoring/correctness operation occurred.

The manifest must preserve path identity exactly. No member may be silently dropped.

## XML inspection boundary

Stage A may inspect XML field/tag names and representative values only to establish **meaning, type and units** for a future parser contract. It MUST NOT use label distributions or event difficulty to choose V4 thresholds, windows, model settings, exclusions or scoring gates.

Any future exclusion must be justified by public documentation or an objective integrity failure (missing/corrupt/unpairable/unsupported file) that is frozen before model correctness is computed.

## Stage B requirement before correctness execution

After Stage A inventory is complete, a separate versioned V4 external-validation execution preregistration must be committed **before any Basic Pitch/V4 correctness result**. It must freeze:

- exact included IDMT subsets/files;
- exact exclusions and reasons;
- exact XML pitch/onset interpretation and units;
- exact Basic Pitch inference settings/runtime;
- exact frozen V4 source identity;
- exact estimate/reference one-to-one matching rule and tolerances;
- minimum V4-positive count;
- uncertainty method;
- overall and any stratum pass/fail gates;
- execution provenance and fail-closed rules;
- protected-song embargo until a separate policy review.

## Current authority state

Reopening Stage A changes no product authority:

- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- persistent Policy C `UNENROLLED`

## Next permitted operation

Implement and controlled-test an inventory-only tool, then run it once on the exact verified IDMT v1.0.0 archive. Stop again before any model inference/correctness scoring until the Stage B preregistration is frozen.
