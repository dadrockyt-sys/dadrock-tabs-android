# RESULT — Songsterr Fresh Boundary Qualifier V2 One-Shot

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Lets take what was learned, repair and run again`
PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
PRE commit: `819d7a9a855d6f067aa40a007fdd0570d231d782`

## Scope / authority consumed

This result records the one prospectively frozen boundary-aware repair cycle and exactly one authorized real EGFxSet V2 diagnostic. The one real V2 authorization is now consumed by run `34940292514`, attempt 1. No retry, threshold variation, alternate candidate, Basic Pitch inference, or post-hoc rule change is authorized by the same instruction.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Historical all-events and hardened-V1 diagnostic results remain immutable FAILs.

## Frozen V2 implementation exercised

The V2 repair separated qualification into two prospectively frozen modes:

1. normal in-clip events with enough genuine left context use the existing V6 complex-harmonic onset-birth classifier unchanged;
2. clip-start events use `clip-start-post-spectrum-harmonic-necessity-v1` over genuine post-onset audio only, with no synthetic pre-context.

Relevant implementation commits:

- boundary physical-presence classifier: `e24aea935058281c5d75b3a700759e055607e735`
- V2 wrapper: `eeed1e8b11a53bfc4e69967de0ad49d0655867ed`
- V2 exact-identity builder: `5ff87dbf962acc3dad1d474da013299019bb6f03`
- V2 adapter bridge: `ead4f6c88c4a0337621cb7cfa0072ab540031fe3`
- DSP synthetic tests: `8842c2cb9b4702de2bbcd25145c864c82447fc7e`
- builder fail-closed tests: `f7ff6e7b2b1a242a2f513d0b4022d6069cc88eb4`
- workflow execution commit: `02414c689b4210771c0f454acc36b86d41e0aafe`

No V6 normal-mode DSP constant was changed. Basic Pitch candidate confidence remained diagnostic-only.

## Synthetic prerequisite gates — PASS

Before the real media was fetched, the same workflow completed all prospective prerequisite gates successfully under Python `3.10.21`, NumPy `1.26.4`, SciPy `1.15.3`, and Node 20.

V2 structural/fail-closed gate:

- contract `songsterr-fresh-model-note-qualification-v2-builder-test`
- `PASS`
- 4 cases
- expected synthetic promotion `[40]`
- missing population, identity mismatch, and confidence-owned decision cases fail closed.

V2 boundary DSP gate:

- contract `songsterr-fresh-independent-note-qualification-v2-test`
- `PASS`
- 8 cases
- normal true birth / later harmonic: `[corroborated, rejected]`
- confidence inversion leaves decisions unchanged
- genuine clip-start single notes at MIDI `40`, `45`, `52`, and `68` all corroborate
- on clip-start E2-only audio, `[40,52,68]` proposals classify `[corroborated,rejected,rejected]`
- genuine clip-start E2 + G#4 polyphony classifies `[corroborated,corroborated]`
- noise does not corroborate
- missing real post-context remains `insufficient`
- synthetic pre-context is never used.

Physical-position ambiguity regression also passed.

Therefore the prospectively frozen gate legitimately allowed the one real-media diagnostic to proceed.

## Immutable real inputs

Dataset member:

- EGFxSet v1.0
- `Clean.zip#Clean/Bridge/6-0.wav`
- archive MD5 `cdb1b401960f56becc8640387910e78a`
- member bytes `722976`
- member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`

Immutable prior Basic Pitch proposal artifact:

- source run `34936227380`
- artifact `10383413992`
- artifact ZIP SHA-256 `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256 `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- raw proposal MIDI list exactly `[40,68]`

Basic Pitch was **not invoked** by the V2 run.

## Execution identity

Workflow:
`.github/workflows/songsterr-egfxset-boundary-v2-one-shot.yml`

Run:

- run `34940292514`
- job `104287207091`
- attempt `1`
- workflow conclusion `failure` because the prospectively frozen final score failed
- every processing stage before the score step completed successfully.

Successful stages included:

- dependency/version gate
- V2 structural synthetic gate
- V2 boundary DSP synthetic gate
- physical-position regression
- immutable prior model artifact verification
- exact EGFxSet archive/member verification
- carrier context build
- V2 qualifier execution exactly once
- V2 evidence build exactly once
- V2 adapter/evaluator exactly once
- immutable artifact upload.

## Immutable result artifact

Artifact:

- ID `10385620104`
- name `songsterr-egfxset-boundary-v2-one-shot`
- size `11816` bytes
- artifact ZIP SHA-256 `f7a48267c299eaf3bba564c05913c95d41d07026ebf4245e9b40762274202948`

Captured file SHA-256 identities:

- `result-v2.json`: `1416df0edbc9d1b534ac2c4727526ebcf52227327caace10d744ada64236a6cf`
- `qualification-v2.json`: `7d9354196d6bcb12c48f22e003f7d0f7ff9e46d429245319a016722ef3257eda`
- `qualified-evidence-v2.json`: `83fc1f197842c97794a34fcb3fd2ab4985a5b4849271d6f4b1654b307af347d8`
- `adapted-evidence-v2.json`: `e1de6cd744d1b66208931601d63df4d723c819465c52f902b5743b19d71f0c80`
- `context.json`: `a9ef99bb7e580abda9006dbe4ff2fdf31510773498dc5e449c6d6839a7b1768f`
- `duration.json`: `bef1b4c35c25acaf3dcdd77dafa41fd9298b758d37268bbbffce853e52b6b180`
- `basic-pitch.json`: `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`

## Observed qualification rows

### MIDI 40 — genuine expected E2 proposal

- note ID `basic-pitch-note-000000`
- start `0.011609977324263039 s`
- V2 mode `clip-start-one-sided-pitch-presence`
- method `clip-start-post-spectrum-harmonic-necessity-v1`
- status `rejected`
- classification `not-onset-birth-corroborated`
- reason `BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`
- original analysis onset sample `512`
- clip-start post window `8192` samples
- left zero padding `0`
- `syntheticPreContextUsed:false`
- analysis RMS `0.2769195787794421`
- selected coefficient `0.0`
- necessity fraction `0.0`
- no dominant lower harmonic owner was implicated
- Basic Pitch candidate confidence was not read for the decision.

Because the selected MIDI-40 template failed the inherited physical-template plausibility gate, the one-sided classifier stopped before its NNLS feature/necessity stage. The wrapper did not persist the underlying template-ratio value itself, so this result must not invent or infer that numeric ratio after the fact.

### MIDI 68 — extra proposal

- note ID `basic-pitch-note-000001`
- start `0.3599092970521542 s`
- V2 mode `normal-in-clip-onset-birth`
- unchanged V6 normal method
- status `rejected`
- reason `OK`
- analysis RMS `0.22146136772942196`
- innovation energy `3.007380617012349`
- feature energy `2.4146259263190646`
- selected coefficient `0.06436904984371984`
- necessity fraction `0.000513675778819313`, below the frozen `0.01` necessity minimum
- candidate confidence was not read for the decision.

Thus the original extra-note weakness remains successfully controlled: MIDI 68 does not promote.

## Promotion / deterministic result

Observed:

- raw proposals `[40,68]`
- statuses `{40: rejected, 68: rejected}`
- insufficient count `0`
- promoted MIDI list `[]`
- rejected-preserved MIDI list `[40,68]`
- unresolved onset count `0`
- promoted positions `[]`.

Evaluator failure reasons include:

- `MODEL_EVIDENCE_VALIDATION_PENDING`
- `DURATION_EVIDENCE_INCOMPLETE`
- `NO_PROMOTED_NOTE_EVENTS`.

## Frozen V2 score

- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`

This result is frozen exactly as observed.

## What was learned

The clip-start zero-padding defect was genuinely repaired: the real V2 run used zero fabricated pre-context and the synthetic boundary suite passed broad true-note, harmonic-alias, polyphony, noise, and missing-context cases.

The remaining concrete weakness moved one layer deeper: the inherited physical harmonic-template plausibility assumption is too restrictive for this real electric-guitar E2 timbre in the one-sided clip-start spectrum. It rejects the expected fundamental before NNLS necessity can be evaluated, while the later MIDI-68 false proposal remains correctly rejected by the normal onset-birth path.

This is evidence of a **timbre/template-model generalization weakness**, not another clip-boundary-context failure.

Do not lower the `0.20` physical-template ratio, remove the physical gate, special-case MIDI 40, or otherwise tune the V2 algorithm from this EGFxSet observation under the consumed authorization. Do not rerun this file under a modified rule without a new prospective authorization.

## Safe next engineering direction

Non-execution/root-cause analysis may inspect the frozen code, synthetic fixtures, and captured metadata. A future repair should be designed prospectively against independent synthetic/non-EGFxSet timbre variation, for example by replacing the single fundamental-to-max-harmonic plausibility rule with a timbre-robust multi-harmonic template criterion while preserving harmonic-alias rejection and real-polyphony recovery.

Any such V3 rule must be frozen and pass broad synthetic/non-EGFxSet tests before any further EGFxSet real-media execution. A new real run requires new explicit user authorization.
