# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — EGFxSet boundary-aware V2 remains a frozen non-authorizing FAIL; AG-PT-set cleared pre-media ingress but its frozen reference-blind audit closed as decision C before any WAV/model correctness exposure; the subsequent metadata-only replacement search has now also rejected GuitarDuets, EG-Solo, Guitar Style Dataset, and the historical GPT dataset pre-media. No Basic Pitch or V6 correctness run is currently authorized.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

Key records:

- hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
- boundary V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
- boundary V2 real result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
- GuitarJam rejection: `docs/checkpoints/SONGSTERR_FRESH_V6_GUITARJAM_PREMEDIA_REJECTION.md`
- URMP/GAPS/EGDB batch: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_URMP_GAPS_EGDB.md`
- AG-PT-set pre-media clearance: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_PREMEDIA_CLEARANCE.md`
- AG-PT-set reference-blind PRE: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`
- AG-PT-set reference-blind result: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_RESULT.md`
- latest replacement-search batch: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_GUITARDUETS_EGSOLO_GUITARSTYLE_GPT.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.
- Never rewrite or soften any frozen historical FAIL/C result.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Consumed real-run authorizations:

- `Please try the run again` -> hardened-V1 EGFxSet run `34938917218`, attempt 1.
- `Lets take what was learned, repair and run again` -> one V2 repair cycle plus one new EGFxSet V2 diagnostic, consumed by run `34940292514`, attempt 1.

There is no remaining authorization for another EGFxSet run, Basic Pitch rerun, V6 correctness run, threshold variation, modified-real-rule execution, AG-PT-set structural re-audit, or candidate-media experiment.

## EGFxSET HISTORY — ALL FROZEN

### Historical all-events smoke

Candidate: EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`, truth string 6 / fret 0 / MIDI 40.

Repaired Basic Pitch run `34936227380` emitted immutable proposals `[40,68]`.

Frozen score:

- `PASS_RUNTIME`
- `FAIL_PITCH`
- `FAIL_POSITION`
- overall `FAIL_NON_AUTHORIZING_SMOKE`

### Hardened V1 real diagnostic

PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`
Result: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_RESULT.md`
Run: `34938917218`

V1 rejected both immutable proposals. MIDI 40 was analyzed with synthetic left zero-padding and failed physical-template plausibility; MIDI 68 failed frozen necessity.

Frozen overall: `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`.

### Boundary qualifier V2

PRE commit: `819d7a9a855d6f067aa40a007fdd0570d231d782`.

V2 prospectively removed fabricated left context from clip-start decisions. Synthetic gates passed ordinary in-clip birth, confidence inversion, clip-start fundamentals, alias rejection, true polyphony, noise rejection, missing-context fail-closed behavior, and physical-position ambiguity.

Real result:

- run `34940292514`
- job `104287207091`
- artifact `10385620104`
- immutable proposals `[40,68]`
- MIDI 40: `rejected`, `BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`, no synthetic pre-context
- MIDI 68: `rejected`, frozen necessity `0.000513675778819313 < 0.01`
- promoted MIDI: `[]`
- overall `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`

The zero-padding boundary defect is fixed. The remaining concrete EGFxSet weakness is the inherited physical harmonic-template plausibility model. Do not lower frozen ratio `0.20`, remove the gate, special-case MIDI 40, or tune from this real observation.

## FROZEN V6 REPLACEMENT-HOLDOUT INGRESS RULE

Before any untouched candidate media/reference payload access, public metadata must establish all of:

1. real human guitar performance suitable for the intended holdout;
2. usable public rights/license for the exact scoring media;
3. synchronized note-event ground truth aligned to the exact performance;
4. reference provenance sufficiently independent of Basic Pitch/V6.

Fail any gate -> `REJECT_PREMEDIA`. Public downloadability alone is not a license grant. A score/source sequence alone is not a timestamped performance reference. No post-access rescue or candidate substitution is allowed.

## CLOSED REPLACEMENT CANDIDATES

### GuitarJam — `REJECT_PREMEDIA`

Real monophonic guitar and usable licensing were established, but no synchronized pre-existing note-event truth aligned to the exact performances was established.

### URMP — `REJECT_PREMEDIA`

No guitar in corpus instrumentation.

### GAPS — `REJECT_PREMEDIA`

Previously frozen licensing/use restrictions plus model-assisted alignment provenance fail ingress. Do not reopen based on later mirrors/wrappers without explicit user authorization.

### EGDB — `REJECT_PREMEDIA`

No usable public dataset license was established in the frozen search.

### Guitar-TECHS — decision C

Closed. Do not rescore or reopen.

### GuitarSet/V3, IDMT/V4, V5/FLGD, GOAT/reference scoring

Closed by scope. Do not use newer search hits or mirrors to reopen them.

## AG-PT-SET — PRE-MEDIA PASS, THEN FROZEN STRUCTURAL C

AG-PT-set was the first current candidate to clear all frozen pre-media gates:

- real human acoustic/electro-acoustic monophonic guitar;
- Zenodo `10.5281/zenodo.10159492`, CC BY 4.0;
- released onset/audio/pitch/string reference fields;
- acceptable independent provenance for ingress.

### Reference-blind PRE

File: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`
PRE commit: `0a84d6be1373d538b251663b1fa7af8f33bbf378`

Only structural/alignment/inventory inspection was authorized. Basic Pitch and V6 correctness were forbidden.

Frozen archive identity:

- `aGPTset_z.zip`
- expected MD5 `1dff8103f9ad6e1a86cee2e5e39cbe87`

Frozen decision rule:

- A: source/timing pairing valid as-is;
- B: only deterministic metadata-implied conversion required;
- C: ambiguous pairing/timing or post-hoc correction required -> reject/do not score.

### Audit execution

Authoritative first-started audit:

- run `35020989444`
- job `104556302921`
- head `1d37950d03e26af6fcdf3a905aa08e2f863ee878`
- artifact `10418038649`
- artifact ZIP SHA-256 `eefea849f7431ffa20262ce5e1b893dd96ae93f2df0d695b59b056c257f495e4`

Accidental duplicate execution:

- run `35021035914`
- job `104556457264`
- head `6125e000a16a0bb44dfa69721f2120d75e8cfc63`
- artifact `10417543492`

The duplicate's inner outputs are byte-identical to the authoritative run and must not be counted as independent validation evidence.

Observed frozen identities/result:

- archive size `6749621615` bytes
- MD5 exact PRE match
- archive SHA-256 `6d03ee80f53e64e703b64f58526b6465264032fcc195aea9ad1058a7ebefba64`
- annotation `aGPTset/metadata/note_labels.csv`
- annotation SHA-256 `75502d20e5149641eb4d3449240413673ace6885a5c822df38760df422e98fa1`
- annotation rows `32592`
- admitted pitched/onset-labeled rows `24180`
- admitted WAVs `0`
- fatal anomalies `24180`
- fatal type `missing_or_ambiguous_audio`
- Basic Pitch runs `0`
- V6 correctness runs `0`

The prospectively frozen exact/suffix resolver could not bind released `audio_file_path` values to unique archive WAV members. Therefore the audit never reached WAV timing/signal alignment. This is a **source-pairing structural C**, not a V6 correctness failure and not a claim that the underlying dataset audio is intrinsically unsynchronized.

Frozen AG-PT-set decision: **C** — `structural timing/source anomaly requires fail-closed rejection`.

Result checkpoint commit: `89ad50b10c37cece15fbcd03db50672bfad8ea92`.

Do not repair the resolver and rerun this closed attempt. A new AG-PT-set structural-binding experiment would require a new prospective PRE plus explicit authorization for the new data access.

## LATEST METADATA-ONLY SEARCH BATCH — ALL REJECTED PRE-MEDIA

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_GUITARDUETS_EGSOLO_GUITARSTYLE_GPT.md`
Checkpoint commit: `66802d4f6537028a7672287b332b26a195ebcb25`

No candidate archive/audio/video/reference payload was opened.

### GuitarDuets — `REJECT_PREMEDIA`

Zenodo `10.5281/zenodo.12802440` describes real and synthesized classical-guitar duets, but note-level MIDI annotations are described for the **synthesized duets**. Exact synchronized note-event truth for the real performances is not established.

### EG-Solo — `REJECT_PREMEDIA`

Public metadata establishes 76 real electric-guitar solo clips / 6,833 labeled note events with MIDI/onset/technique labels, but the exact performance audio comes from popular-rock-song YouTube videos and is not distributed as licensed dataset media. Public YouTube availability is not a usable media license.

### Guitar Style Dataset — `REJECT_PREMEDIA`

Public metadata establishes 549 real electric-guitar recordings and MuseScore exercises, but not a released note-event timeline synchronized to each exact recorded performance. The exercise score cannot be post-hoc aligned and treated as frozen truth.

### Historical Guitar Playing Techniques (GPT) dataset — `REJECT_PREMEDIA`

Literature describes the dataset, but a 2024 guitar-dataset survey reports the public link had been broken for years and its authors' attempts to obtain the data were unsuccessful. No accessible/verifiable immutable candidate payload is established.

## CURRENT SAFE ENGINEERING DIRECTION

Permitted now:

- continue **metadata/license/alignment/provenance-only** search for another untouched real-guitar holdout;
- inspect already-frozen code/artifacts/metadata;
- design synthetic/non-EGFxSet V3 physical-template research without touching closed real media;
- documentation/checkpoint maintenance and non-executing workflow hardening.

Not permitted without new explicit prospective authorization:

- Basic Pitch on AG-PT-set, EGFxSet or a new real candidate;
- any V6 correctness run;
- AG-PT-set resolver repair/re-audit against the real archive;
- EGFxSet retry or modified real rule;
- candidate archive/audio/reference opening after a pre-media rejection;
- Modal/Vercel heavy-GPU/L4 correctness work on closed real media;
- physical procurement/calibration/capture;
- protected-song execution;
- V143/Gomyway or GOAT/reference work.

## FRESH CHAT — EXACT NEXT STEPS

1. Re-fetch live `songsterr-fresh-pipeline-v1` and this checkpoint.
2. Preserve EGFxSet V2 run `34940292514` as frozen FAIL evidence.
3. Preserve AG-PT-set pre-media PASS followed by frozen structural decision C; never count duplicate run `35021035914` as independent evidence.
4. Preserve GuitarJam, URMP, GAPS, EGDB, GuitarDuets, EG-Solo, Guitar Style Dataset and GPT as frozen pre-media rejections.
5. Do not reopen Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, GOAT/reference scoring, V143/Gomyway, duration, protected songs, `main`, Production, reserved GFN splits, or physical calibration/capture.
6. Default next work: continue metadata-only search for an untouched holdout and/or independent synthetic V3 physical-template research.
7. If a new candidate clears **all four** pre-media gates, freeze a candidate-specific one-shot PRE before any media/reference payload access; do not execute it without the required explicit authorization.
8. Keep this checkpoint updated after each meaningful search batch or state transition.

## AUTHORITATIVE ROUTE

The software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
