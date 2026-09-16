# PRE — Songsterr Fresh V7 Boundary-Aware One-Shot Real Evaluation

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `785caf6ca33d106dc45290f8e350b30daabed643`
Authority: user instruction `I authorize please continue`

## 1. AUTHORIZED SCOPE

This PRE prospectively freezes exactly one V7 real-media/model-evidence diagnostic after the frozen V7 synthetic/mechanical integration PASS.

The authorization is interpreted narrowly as permission to execute the smallest scientifically comparable V7 diagnostic on the same previously frozen EGFxSet event and immutable prior Basic Pitch proposal artifact. It does **not** authorize a new Basic Pitch inference, threshold tuning, repeated retries, alternate real candidates, official correctness, calibration/holdout work, `main`, Production, customer eligibility, delivery advancement, protected-song work, GOAT/reference scoring, or archived V143/Gomyway.

The historical V1/V2 EGFxSet results remain immutable historical FAILs regardless of this run.

## 2. FROZEN INPUT IDENTITIES

The real diagnostic may use only the same frozen input identities already established by `SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md` and `SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`:

### EGFxSet media

- EGFxSet v1.0 archive member: `Clean.zip#Clean/Bridge/6-0.wav`
- archive source: `https://zenodo.org/records/7044411/files/Clean.zip?download=1`
- archive MD5: `cdb1b401960f56becc8640387910e78a`
- member SHA-256: `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- member bytes: `722976`
- frozen reference identity for this diagnostic only: string 6 / fret 0 / MIDI 40

### Immutable prior model proposals

Basic Pitch must **not** be invoked again. Reuse only:

- prior repaired run: `34936227380`
- artifact ID: `10383413992`
- artifact ZIP SHA-256: `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- `basic-pitch.json` SHA-256: `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256: `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- raw proposal MIDI list exactly `[40,68]`

Any identity mismatch fails closed and stops the diagnostic. No substitute artifact, model rerun, proposal deletion, proposal addition, or proposal relabeling is allowed.

## 3. FROZEN SOFTWARE LINEAGE

Read-only dependencies include:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py`, blob `f9bef389f848c8f003ffa844b1eb2eea5754002d`;
- `scripts/songsterr-fresh/clip_start_pitch_presence_v1.py`, blob `df57fcb808a654856826d2825e39854c9e3acb54`;
- `scripts/songsterr-fresh/test_qualify_basic_pitch_note_births_v2.py`, blob `dbb41317ec985009f0a87c907d2bd703caa12e66`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`, blob `7090e17baff60f91700a760f617e905ff53484ab`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py`, blob `39629250c6d141d5cda9e9d7f570580ec725ae42`;
- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`, blob `6dfadda70db6b902f1dcc4d804f2d66da547314d`;
- `scripts/songsterr-fresh/test_onset_birth_corroboration_v7_integration.py`, blob `a5443cae88f4ba49e5a9712822a5c371b67a1c30`.

Frozen V7 integration result remains `PASS_SYNTHETIC_MECHANICAL_INTEGRATION`, result commit `9f6345e971f36a0def367a70564ba9b86c948e23`. Frozen V3 iteration-3 result remains `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`, result commit `e97ab67c9c2794f4a50c5170102d1380484f5fb1`.

No frozen V2/V6/V3/V7 implementation is edited under this PRE.

## 4. WHY A NEW BOUNDARY ADAPTER IS REQUIRED

The frozen V7 audio entry point was prospectively integrated only for ordinary in-clip proposals using the frozen V6 pre/post onset-innovation geometry. The EGFxSet MIDI-40 proposal begins at approximately 11.6 ms (historically analysis onset sample `512`), earlier than the frozen `3584`-sample genuine-left-context requirement. Calling the ordinary V7 entry point directly would therefore fail for unavailable pre-context and would **not** evaluate the V3 physical-template hypothesis.

The frozen V2 boundary repair already established the correct no-fabrication routing rule: clip-start proposals use exactly `8192` genuine post-onset samples, demean + Hann window, and an `8192`-point real-FFT magnitude spectrum, with no left zero padding and no right padding.

This PRE permits a new V7 **research-only boundary adapter** that preserves that exact V2 one-sided signal construction and applies the already-frozen V7/V3 evidence composite to the resulting nonnegative one-sided spectral evidence vector on the same frozen FFT frequency grid. This is a new research boundary application and therefore must pass the frozen V2 boundary synthetic controls before real media is fetched.

It is not an in-place V2 repair and does not change Production routing.

## 5. PROSPECTIVE WRITE BOUNDARY

After this PRE is frozen, the only new/changeable files for this experiment are:

- `scripts/songsterr-fresh/clip_start_pitch_presence_v7.py` — new one-sided V7 research boundary adapter;
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v7.py` — new V7 research qualifier preserving V2 clip-start/ordinary routing while calling frozen V7 evidence logic;
- `scripts/songsterr-fresh/test_qualify_basic_pitch_note_births_v7.py` — synthetic prerequisite regression using the frozen V2 eight-case fixture logic and V7-specific contract checks;
- `.github/workflows/songsterr-egfxset-v7-real-evaluation-one-shot.yml` — exact one-shot workflow, self-triggered only by a push changing that workflow file on `songsterr-fresh-pipeline-v1`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_RESULT.md` — immutable first-result record;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state-only updates.

Any additional filename or any edit to a frozen implementation requires another prospective PRE before the change.

## 6. FROZEN BOUNDARY-ADAPTER SEMANTICS

### Clip-start proposals

For a proposal with onset earlier than the frozen genuine-left-context requirement:

1. validate selected MIDI as an integer in frozen playable range `40..88`;
2. require the onset sample to be a nonnegative integer;
3. require finite mono in-memory audio;
4. require exactly `8192` genuine post-onset samples beginning at the proposal onset; no left or right padding;
5. demean that frame;
6. require analysis RMS `>= 1e-5`;
7. apply a Hann window and compute an `8192`-point real FFT magnitude spectrum;
8. require the spectrum to be finite, one-dimensional and nonnegative;
9. construct the frozen `44100 Hz / FFT_SIZE 8192` frequency grid;
10. pass only `selected_midi`, this in-memory spectral evidence vector, and the frequency grid into frozen `onset_birth_corroboration_v7.evaluate_in_memory_innovation()`; the function name is historical, but the boundary adapter must explicitly label its input provenance as `clip-start-post-spectrum-evidence-v7` rather than claim it is pre/post onset innovation;
11. never promote a frozen V7/V3 failure;
12. map V7 PASS to `corroborated`; map a finite V7/V3 rejection to `rejected`; reserve `insufficient` for unavailable post context, low/nonfinite audio support, malformed input, or numerical/unavailable evidence before a valid finite V7 decision;
13. preserve V7 diagnostics including `necessityFraction`, `candidateEvidenceFraction`, `credibleLowerOwners`, `vetoingOwners`, and nested `v3Composite` when available;
14. never read Basic Pitch candidate confidence for the decision.

No V7/V3 threshold or constant may be changed. In particular preserve `necessityFraction >= 0.01` and `candidateEvidenceFraction >= 0.10`. The historical V6 `0.20` fundamental ratio remains read-only historical evidence and is not reintroduced as a V7 decision threshold.

### Ordinary in-clip proposals

For proposals with sufficient genuine left context, call the frozen V7 `evaluate_in_memory_audio_event()` with exact selected proposal identity. Do not change V6 frame geometry, onset-innovation construction, FFT size, RMS/innovation minima, playable MIDI range, V3 lower-owner logic, NNLS necessity, or evidence-significance threshold.

Normal-mode V7 PASS maps to `corroborated`. A finite V7/V3 non-PASS decision maps to `rejected`, except missing required audio context or other explicitly unavailable/malformed evidence maps to `insufficient`. The frozen historical low-onset-innovation semantic remains rejection for a fully contextualized proposed new birth.

## 7. SYNTHETIC PREREQUISITE — MUST PASS BEFORE REAL FETCH

The workflow must execute the V7 synthetic boundary regression **before** fetching either the immutable prior Basic Pitch artifact or EGFxSet media.

The V7 regression must reuse, not weaken, the exact eight frozen V2 boundary behavioral expectations:

1. ordinary in-clip E2 birth corroborates and later fifth-harmonic-area MIDI 68 rejects;
2. reversing candidate confidences leaves decisions unchanged;
3. genuine clip-start single notes at MIDI `40`, `45`, `52`, and `68` corroborate with no fabricated pre-context;
4. on clip-start E2-only audio, proposals `[40,52,68]` classify `[corroborated,rejected,rejected]`;
5. genuine clip-start E2 + G#4 polyphony classifies both proposals `corroborated`;
6. noise-only clip-start evidence does not corroborate;
7. unavailable genuine post context is `insufficient`;
8. normal right-edge missing context is `insufficient`.

Additionally the V7 test must fail closed unless:

- qualifier contract/version are the prospectively defined V7 values;
- candidate confidence is not used for decisions;
- clip-start provenance says `syntheticPreContextUsed:false` and `leftBoundaryZeroPaddingSamples:0`;
- V7 dependency contract integrity passes;
- any corroborated row carries finite `necessityFraction >= 0.01` and finite `candidateEvidenceFraction >= 0.10`;
- no corroborated row contains a nonempty `vetoingOwners` list;
- no real corpus, model inference, network, workflow dispatch, protected-song, GPU/heavy compute, or closed-line data is accessed by the synthetic test itself.

If this first frozen synthetic prerequisite fails, the workflow must stop before prior-artifact or EGFxSet download. No real result is produced, no threshold is tuned, and no same-iteration rescue rerun is allowed. Any repair requires a new prospective PRE/iteration and new explicit real-run authorization if a later real execution is desired.

## 8. EXACT ONE-SHOT REAL EXECUTION

Only after the synthetic prerequisite passes, the workflow may:

1. fetch immutable artifact `10383413992` with the repository GitHub token;
2. verify artifact ZIP SHA-256 exactly;
3. extract and verify `basic-pitch.json` SHA-256, note identity and exact raw MIDI proposals `[40,68]`;
4. fetch the exact EGFxSet `Clean.zip` from the frozen Zenodo URL;
5. verify archive MD5, extract only `Clean/Bridge/6-0.wav`, verify member SHA-256 and byte count;
6. run `qualify_basic_pitch_note_births_v7.py` **exactly once** on the exact WAV + immutable proposal JSON;
7. score the frozen diagnostic rule exactly once;
8. upload the qualification/result evidence artifact even if the frozen score fails.

Basic Pitch, Demucs or any other model inference must not run. No reference tab is read by the qualifier. No waveform listening, manual note deletion, candidate substitution, confidence thresholding, threshold search or retry is allowed.

## 9. FROZEN REAL DIAGNOSTIC SCORE

A V7 diagnostic PASS requires all of the following, prospectively:

- every prerequisite step succeeded;
- exact frozen artifact and media identities match;
- raw proposal MIDI list is exactly `[40,68]`;
- exactly two qualification rows exist with exact proposal identity preserved;
- MIDI 40 status is `corroborated` through `clip-start-post-spectrum-evidence-v7`;
- MIDI 40 provenance shows no synthetic pre-context and zero left boundary padding;
- MIDI 40 has finite `necessityFraction >= 0.01` and finite `candidateEvidenceFraction >= 0.10`;
- MIDI 40 has no vetoing lower owner;
- MIDI 68 status is `rejected` through ordinary in-clip V7 onset-birth evidence;
- `insufficientCount == 0`;
- promoted MIDI list derived from corroborated rows is exactly `[40]`;
- rejected preserved MIDI list is exactly `[68]`;
- promoted MIDI 40 has exactly one standard-tuning position: string 6 / fret 0 / reconstructed MIDI 40.

Any other observation is a frozen diagnostic FAIL. The result must preserve detailed V7/V3 diagnostics rather than reinterpret them post hoc.

This score is a non-authoritative diagnostic only. PASS would mean the prospectively frozen V7 research rule handled this one previously frozen event under its fixed inputs; FAIL would identify a remaining frozen limitation. Neither outcome establishes calibrated correctness or general real-world performance.

## 10. WORKFLOW / FIRST-RUN POLICY

The one-shot workflow must be created last, after the PRE and the three new Python files are committed and their exact Git blobs/diff are verified.

Its automatic trigger must be restricted to:

- branch `songsterr-fresh-pipeline-v1`;
- push path `.github/workflows/songsterr-egfxset-v7-real-evaluation-one-shot.yml` only.

Creating that workflow file is the authorized trigger for the single run. Do not manually dispatch it in addition to the push trigger.

The workflow must use Python `3.10.21`, NumPy `1.26.4`, SciPy `1.15.3`, and Node 20, matching the prior V2 diagnostic environment.

The first started run is authoritative. Do not cancel/restart merely to improve an outcome. Do not modify the workflow or support code after seeing a failure and rerun under this same PRE. If infrastructure fails before any frozen evidence is evaluated, record that fact exactly; any retry requires a new prospective authorization decision rather than silently consuming another run.

## 11. RESULT RECORDING

Freeze the first observed result in `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_RESULT.md` with:

- PRE commit;
- support file/workflow commit SHAs and Git blobs;
- run/job/attempt identity;
- exact input/artifact hashes;
- synthetic prerequisite result;
- per-proposal V7 qualification rows and key diagnostics;
- promoted/rejected/insufficient inventory;
- deterministic position result;
- artifact IDs and file hashes;
- frozen overall PASS/FAIL classification;
- explicit statement that no rescue rerun or post-result tuning occurred.

Then update `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.

## 12. AUTHORITY EFFECTS — UNCHANGED REGARDLESS OF RESULT

Keep all global flags unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

This one-shot does not switch any production pipeline to V7 and does not authorize customer-visible output.

## 13. EXPLICIT PROHIBITIONS

Do not under this PRE:

- edit frozen V2/V6/V3/V7 implementations or historical checkpoints;
- invoke Basic Pitch or Demucs/model inference;
- tune any threshold from EGFxSet;
- special-case MIDI 40, MIDI 68, EGFxSet, string 6/fret 0, or observed confidence values inside the algorithm;
- add a learned parameter or dataset-specific branch;
- use alternate media/proposals if an identity fails;
- run a second real attempt under this authorization;
- reopen AG-PT-set or any rejected holdout;
- access protected-song work;
- perform physical calibration/capture;
- run heavy GPU work;
- modify `songsterr_pipeline/**`, `main`, or Production;
- resume GOAT/reference scoring;
- resume archived V143/Gomyway.

Archived V143/Gomyway remains untouched unless the user explicitly asks to resume it.
