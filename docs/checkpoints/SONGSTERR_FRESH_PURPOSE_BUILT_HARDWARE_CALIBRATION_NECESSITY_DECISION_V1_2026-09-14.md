# Songsterr Fresh — Purpose-Built Hardware / Calibration Necessity Decision V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **PROSPECTIVE DECISION / NO HOLDOUT CAPTURE AUTHORITY**

## Decision

`REAL_REFERENCE_HARDWARE_REQUIRED: true`

`NON_HOLDOUT_CALIBRATION_REQUIRED: true`

`IMMEDIATE_PURCHASE_REQUIRED: false`

`IMMEDIATE_PERFORMER_OR_VENDOR_CONTACT_REQUIRED: false`

`REAL_HOLDOUT_RECORDING_AUTHORIZED: false`

The purpose-built route has now exhausted the part of the reference-validation problem that can be established by paper contracts, synthetic fixtures, and ordinary GitHub CPU alone. A real physical reference implementation and a strictly non-holdout calibration phase are objectively necessary before a future untouched real-guitar population can exist. However, procurement or contact is not yet the next irreversible action: first freeze a hardware-neutral document/bench qualification gate and screen candidate architectures against it.

## Frozen authority considered

- Expanded design: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`, commit `e37d2b4662db949157d2cf4797370f05648b6940`.
- Physical semantics V1: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`, commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`.
- Capture-QA / structural gate matrix V1: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`, commit `2b191b39f2f1c19564f1353381779acbc96fbeda`.
- Capture-manifest V2.1 synthetic CI PASS: run `34908936464`, job `104191861049`.
- Reference-blind structural-audit V1 preregistration: commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`.
- Reference-blind structural-audit V1 synthetic CI PASS: integration head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`, run `34912172056`, job `104201857367`.

## Why real hardware is now objectively necessary

The frozen physical-reference semantics require evidence that software-only/synthetic work cannot create or prove:

1. **Physical string + fret/contact identity.** A qualifying system must establish nominal pitch identity from physical string/fret state rather than from evaluated DI or a pitch-transcription model.
2. **Independent event-birth/rearticulation evidence.** Repeated same-string/same-fret attacks and repeated open-string attacks require a physical birth/excitation signal separate from pitch state.
3. **Real hardware clock/sync behavior.** The frozen structural audit requires a hardware/reference timing declaration and clock/sync proof bounded at `0.025 s`; real drift, jitter, missing markers, and synchronization behavior cannot be inferred from synthetic JSON.
4. **Raw sensor health behavior.** Dropout, saturation, stuck state, ambiguity and configuration identity are physical failure modes that need a real implementation before acquisition-QA thresholds can be defensibly frozen.
5. **Technique capability.** A future plan must know which physical technique classes can be established independently (or prospectively excluded) before holdout capture. This is an empirical capability question for the chosen reference topology.
6. **Calibration artifacts.** The frozen design requires real, immutable calibration IDs/hashes/configuration identities bound into every future holdout take. Synthetic fixtures cannot substitute for calibration of a physical system.

Therefore a real reference apparatus is not optional if the purpose-built route is to progress beyond design/synthetic verification.

## Why immediate purchase/contact is not yet necessary

The design is explicitly hardware-neutral and still leaves sensor class/topology, excitation mechanism and sync implementation unresolved. Purchasing before a frozen acceptance gate would let vendor/device limitations silently determine truth semantics. That reverses the intended order.

Before spending or vendor/performer contact, the project can still make meaningful progress with zero holdout exposure by:

- freezing hardware-neutral documentary acceptance criteria;
- freezing a non-holdout bench/calibration test matrix;
- screening public device documentation against those criteria;
- identifying which requirements truly require a purchased bench sample versus can be rejected from documentation alone;
- defining the minimum architecture to purchase/build if no off-the-shelf product qualifies.

Only after that screen should a specific purchase/contact be classified as objectively necessary.

## Evidence classes that remain prospective

### Can still be resolved without real hardware

- public specification / raw-data-access screen;
- candidate architecture comparison;
- required signal/channel inventory;
- immutable file/schema/hash format;
- bench test procedure;
- calibration-versus-holdout separation procedure;
- candidate technique capability declaration template;
- acquisition-QA code/version design after empirical limits exist.

### Requires a real bench implementation

- actual string/fret discrimination;
- same-pitch reattack discrimination;
- actual clock timestamp error, drift and jitter;
- actual dropout/saturation/stuck-state behavior;
- real configuration/firmware/calibration binding;
- empirical thresholds/hysteresis/debounce chosen from NON-HOLDOUT calibration only;
- empirical capability for planned technique classes;
- deterministic regeneration from real raw sensor logs.

### Still forbidden at the bench stage

- admitted holdout performances;
- future holdout correctness;
- Basic Pitch/V6 feedback for calibration decisions;
- evaluated-holdout DI as truth/alignment evidence;
- model-informed retakes;
- post-hoc repair of reference events;
- changing the frozen `0.025 s` structural timing bound;
- reopening archived V143/Gomyway, Guitar-TECHS rescue or GOAT/reference scoring.

## State transition

The program may advance from pure `DESIGN_ONLY` documentation into **hardware-neutral qualification planning**, but not yet into holdout capture.

The next prospective gate is `REFERENCE_HARDWARE_BENCH_QUALIFICATION_PREREGISTERED`. Only after that gate is frozen may current product/architecture screening determine whether procurement/contact is necessary.

Downstream authorization remains unchanged:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
