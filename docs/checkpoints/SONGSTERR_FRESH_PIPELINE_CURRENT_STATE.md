# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — boundary-aware V2 remains frozen FAIL on the authorized EGFxSet diagnostic; replacement-holdout search rejected GuitarJam, URMP, GAPS, and EGDB pre-media; AG-PT-set cleared pre-media gates but its frozen reference-blind structural audit closed as decision C because the released annotation `audio_file_path` values did not bind to unique archive WAV members under the prospectively frozen resolver. No Basic Pitch or V6 correctness was executed on AG-PT-set.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`
Hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
Boundary V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
Boundary V2 result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
AG-PT-set pre-media clearance: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_PREMEDIA_CLEARANCE.md`
AG-PT-set reference-blind PRE: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`
AG-PT-set reference-blind result: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_RESULT.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.
- Do not rewrite or soften any frozen historical FAIL/C result.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The user's `Please try the run again` authorization was consumed by EGFxSet hardened-V1 run `34938917218`, attempt 1.

The user's later instruction `Lets take what was learned, repair and run again` authorized one boundary-repair cycle plus exactly one new non-authoritative EGFxSet V2 diagnostic after prospectively frozen synthetic gates. That authorization was consumed by run `34940292514`, attempt 1.

There is no remaining authorization for another EGFxSet run, Basic Pitch rerun, V6 correctness run, threshold variation, modified real rule, or candidate substitution under those instructions.

## HISTORICAL EGFxSET ALL-EVENTS SMOKE — FROZEN FAIL

Candidate: EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, truth string 6 / fret 0 / MIDI 40.

Repaired Basic Pitch run `34936227380` emitted immutable proposals `[40,68]`.

Historical score remains:

- `PASS_RUNTIME`
- `FAIL_PITCH`
- `FAIL_POSITION`
- overall `FAIL_NON_AUTHORIZING_SMOKE`

Never rewrite this as a PASS.

## PIPELINE HARDENING V1 — CODE/SYNTHETIC GREEN

Combined regression run `34938422696`, job `104281318739`, passed the hardened proposal/qualification regressions.

Frozen core design:

- Basic Pitch events are proposals only;
- only independently `corroborated` proposals promote;
- `rejected` proposals are preserved but do not promote;
- `insufficient` remains unresolved/fail-closed;
- Basic Pitch confidence is diagnostic-only;
- physical-position ambiguity remains explicit.

## HARDENED V1 REAL-AUDIO DIAGNOSTIC — FROZEN FAIL

PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`
Result: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`
Run: `34938917218`

V1 rejected both immutable proposals. MIDI 40 was analyzed with synthetic left zero-padding and failed the physical-template plausibility gate; MIDI 68 failed frozen necessity.

Frozen score:

- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`

That result identified the unsafe synthetic-precontext boundary policy. It remains immutable history.

## BOUNDARY QUALIFIER V2 — REPAIR COMPLETE, REAL RESULT FROZEN FAIL

PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
PRE commit: `819d7a9a855d6f067aa40a007fdd0570d231d782`

V2 prospectively removed fabricated left context from clip-start decisions. Its synthetic prerequisite suite passed ordinary in-clip onset-birth, confidence inversion, true clip-start fundamentals, alias suppression, real polyphony, noise rejection, missing-context fail-closed behavior, and physical-position ambiguity regression.

Dedicated real result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
Result commit: `42b8fc30de468b123d6c5f5d7df6d5a43db86c81`
Run: `34940292514`
Job: `104287207091`
Artifact: `10385620104`

Observed immutable proposals remained `[40,68]`.

- MIDI 40 used the genuine one-sided clip-start path with zero fabricated pre-context and was rejected as `BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE` before NNLS necessity.
- MIDI 68 used the unchanged normal in-clip path and remained rejected with necessity fraction `0.000513675778819313` below frozen minimum `0.01`.

Frozen V2 score:

- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`

The zero-padding boundary defect is fixed. The remaining concrete EGFxSet weakness is the inherited physical harmonic-template plausibility model. Do not lower the frozen `0.20` ratio, remove that gate, special-case MIDI 40, or tune from the EGFxSet observation.

Any future EGFxSet/model/media experiment requires a new explicit prospective authorization.

## V6 REPLACEMENT-HOLDOUT SEARCH — CLOSED CANDIDATES

### GuitarJam — REJECT_PREMEDIA

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_GUITARJAM_PREMEDIA_REJECTION.md`

Real monophonic guitar and usable licensing were established, but public evidence did not establish synchronized pre-existing note-event ground truth aligned to the exact performances. No media/model run occurred.

### URMP / GAPS / EGDB — REJECT_PREMEDIA

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_URMP_GAPS_EGDB.md`

- URMP: no guitar in the corpus instrumentation.
- GAPS: licensing/use restrictions and model-assisted alignment provenance fail the frozen ingress rule.
- EGDB: no usable public dataset license established.

No candidate payload was opened and no V6 correctness ran for these pre-media rejections.

## AG-PT-SET — PRE-MEDIA PASS, THEN REFERENCE-BLIND DECISION C

### Pre-media clearance

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_PREMEDIA_CLEARANCE.md`
Clearance checkpoint lineage includes commit `636403d0d168700cb77e36462d8f71caf9bc2809`.

AG-PT-set was the first current replacement candidate to clear all frozen pre-media gates:

- real monophonic acoustic/electro-acoustic human guitar performances;
- Zenodo record `10.5281/zenodo.10159492` under CC BY 4.0;
- released note-level onset/audio/pitch/string references;
- reference provenance independent of Basic Pitch/V6 for ingress purposes.

That clearance was only admission to prospective structural planning.

### Frozen reference-blind PRE

`docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`
PRE commit: `0a84d6be1373d538b251663b1fa7af8f33bbf378`

The PRE allowed only a reference-blind structural/alignment/inventory audit. Basic Pitch and V6 correctness were explicitly forbidden.

Frozen archive identity:

- `aGPTset_z.zip`
- expected MD5 `1dff8103f9ad6e1a86cee2e5e39cbe87`
- CC BY 4.0

Frozen A/B/C rule:

- A: released timing/source pairing structurally synchronized as-is;
- B: only a deterministic metadata-implied conversion is required;
- C: pairing/timing is ambiguous or would require learned/post-hoc correction; reject and do not score.

### Execution history

The audit workflow was added in commit `1d37950d03e26af6fcdf3a905aa08e2f863ee878` with a path-scoped `push` trigger. That commit automatically started the first audit.

Authoritative first-started audit:

- run `35020989444`
- job `104556302921`
- head `1d37950d03e26af6fcdf3a905aa08e2f863ee878`
- artifact `10418038649`
- artifact ZIP SHA-256 `eefea849f7431ffa20262ce5e1b893dd96ae93f2df0d695b59b056c257f495e4`
- conclusion `success`

A later trigger commit `6125e000a16a0bb44dfa69721f2120d75e8cfc63` started a duplicate execution while the first was still running:

- run `35021035914`
- job `104556457264`
- artifact `10417543492`
- artifact ZIP SHA-256 `4d55de96b83db084a08862125c8f8444bd2d3a641d4b93552c741757c692e549`
- conclusion `success`

The two ZIP containers differ, but every inner result file is byte-identical. The second run is duplicate history only and must not be counted as an independent validation replicate.

### Frozen observed identities

Archive:

- size `6749621615` bytes
- MD5 `1dff8103f9ad6e1a86cee2e5e39cbe87` — exact PRE match
- SHA-256 `6d03ee80f53e64e703b64f58526b6465264032fcc195aea9ad1058a7ebefba64`

Annotation table:

- `aGPTset/metadata/note_labels.csv`
- SHA-256 `75502d20e5149641eb4d3449240413673ace6885a5c822df38760df422e98fa1`
- `32592` rows

Frozen row filter admitted `24180` pitched/onset-labeled reference rows.

### Frozen structural result

The prospective exact/suffix resolver could not bind any admitted released `audio_file_path` value to exactly one archive `.wav` member.

Observed:

- admitted reference rows: `24180`
- admitted WAVs: `0`
- anomalies: `24180`
- fatal anomalies: `24180`
- fatal type: `missing_or_ambiguous_audio`
- source WAVs structurally inspected: `0`
- Basic Pitch runs: `0`
- V6 correctness runs: `0`

Representative released path value:

`acoustic_guitar_pitched_allstring1_naturalharmonics_mf_DavRos_20200820.wav`

Because no WAV identity could be bound, the audit did not reach sample-rate/timing or signal/onset alignment checks. This is a source-pairing structural C, not a V6 correctness failure and not a claim that the underlying dataset audio itself is unsynchronized.

The frozen artifact also contains some integer `pitch_midi` values outside conventional MIDI `0..127`. No post-access reinterpretation is permitted under the frozen PRE.

### Frozen AG-PT-set decision

Result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_RESULT.md`
Result commit: `89ad50b10c37cece15fbcd03db50672bfad8ea92`

Decision: **C**

Frozen reason:

`structural timing/source anomaly requires fail-closed rejection`

AG-PT-set therefore does not advance to V6 scoring in this audit attempt.

Do not repair the resolver and rerun this audit as though the C result never happened. A new AG-PT-set structural-binding experiment would require a new prospective PRE and explicit authorization appropriate to new data access.

## CURRENT SAFE ENGINEERING DIRECTION

Permitted without new real-model authorization:

- inspect frozen code and already-captured metadata/artifacts;
- continue metadata/license/alignment/provenance search for another untouched real-guitar holdout under the existing frozen ingress requirements;
- design synthetic/non-EGFxSet V3 physical-template research without touching closed real media;
- improve documentation/checkpointing and prevent accidental duplicate workflow execution, provided no closed real run is triggered.

Not permitted without new explicit authorization:

- any Basic Pitch run on AG-PT-set or EGFxSet;
- any V6 correctness run;
- any AG-PT-set structural re-audit or resolver-repair execution against the real archive;
- any EGFxSet retry or modified real rule;
- Modal, Vercel heavy-GPU, L4 or other external heavy compute for closed real-media correctness;
- physical procurement/calibration/capture;
- protected-song execution.

## FRESH CHAT — EXACT NEXT STEPS

On a fresh chat:

1. re-fetch live `songsterr-fresh-pipeline-v1` and this checkpoint;
2. treat EGFxSet V2 run `34940292514` and its result as frozen completed FAIL evidence;
3. treat Guitar-TECHS as decision C; GuitarJam, URMP, GAPS, EGDB as closed pre-media rejections;
4. treat AG-PT-set as pre-media PASS followed by frozen reference-blind structural decision C; do not score it with V6 under the current attempt;
5. preserve authoritative AG-PT-set audit run `35020989444`; preserve run `35021035914` only as an accidental duplicate with byte-identical inner outputs;
6. do not rerun the AG-PT-set audit, Basic Pitch, V6, EGFxSet, or any closed real-media line without new prospective authorization;
7. next default work is metadata-only search for another untouched holdout and/or synthetic V3 physical-template research;
8. keep all historical all-events, hardened-V1, V2, pre-media rejection, clearance, PRE, and result records unchanged;
9. do not reopen V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution, `main`, Production, reserved GFN splits, or physical procurement/calibration/capture unless separately authorized.

## AUTHORITATIVE ROUTE

The completed software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
