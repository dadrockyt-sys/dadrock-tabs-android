# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless the user explicitly reopens them.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`.
- Protected song remains embargoed. No Production or customer-admission change is authorized.

## USER COMPUTE AUTHORIZATION RULE — 2026-09-13

The user authorized continued work at assistant discretion and requested a new authorization prompt only before:
- any **Modal** run;
- any **Vercel heavy-GPU** run;
- any **L4 GPU** run.

Normal research, coding, GitHub work, CPU runs, checkpoints, tests and ordinary Vercel work may proceed without another authorization prompt, subject to the scientific/policy boundaries here.

## CLOSED / REVEALED LINES

V1/V2 are rejected research diagnostics. GuitarSet/V3 and IDMT/V4 are closed/revealed and cannot be untouched successor holdouts.

V5 is closed and rejected. Official FLGD result:
- run `34748789583`, job `103701492462`
- immutable result `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`
- result commit `df6a306a055303a6f37b229bfc9e538803f25337`
- 79/79 files; 84,577 decoded/classified; 43,349 positives; 27,850 correct
- precision `0.642460033680131`; one-sided 95% Wilson LB `0.6386648804090969` vs required `0.9900`
- `externalValidationPassed:false`.

V5 policy review: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_POST_RESULT_POLICY_REVIEW.md`, commit `44c99d54ed7e728e85ef4042d1f15ba09643713c`.
Decision: **V5 ADMISSION REJECTED / FAIL-CLOSED**.

FLGD is revealed. Do not rerun/tune V5 on FLGD. Do not use FLGD/IDMT/GuitarSet correctness or protected-song outcomes to choose V6 constants.

## V6 — ACTIVE SUCCESSOR / SYNTHETIC GREEN / NO REAL CORRECTNESS YET

Research charter: `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md`, commit `2b96fba0e3df955e62386691023cb31eeb2d11f6`.

Scientific question: does the selected Basic Pitch MIDI show an **onset-synchronous acoustic birth signature**—candidate-specific complex/harmonic innovation appearing at the decoded onset relative to immediately preceding audio?

This is distinct from V1/V2/V4/V5 post-onset steady-state scoring and is not a V5 threshold rescue.

### Candidate family A — current leading method

Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`.

Frozen-before-implementation synthetic fixtures: `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, commit `ca71eb218ce701686e4a4806813ac84580defa78`.

Current synthetic constants:
- mono 44.1 kHz
- 2,048-sample complex STFT frame; 256-sample hop; FFT 8,192
- frame-end offsets -1536..+1536 samples in 256-sample steps
- post-onset innovation horizon +1024 samples
- up to 6 harmonics
- minimum analysis RMS `1e-5`
- minimum innovation energy `1e-6`
- valid-template fundamental/max-harmonic onset-innovation ratio `0.20`
- selected-template onset-innovation necessity fraction `0.01`
- deterministic SciPy NNLS polyphonic explanation
- event identity/MIDI preserved exactly.

The method has **no standalone real-corpus mode**.

### Controlled V6 synthetic CI — GREEN

Workflow: `.github/workflows/songsterr-fresh-v6-synthetic-ci.yml`, source commit `45328f1d07644eef62f8fa7ab5b22f798f65fa20`.

Official controlled CPU run:
- run `34754079541`
- job `103715385229`
- conclusion `success`
- Ubuntu 24.04 / Python 3.10 / NumPy 1.26.4 / SciPy 1.15.3
- GPU disabled; no Modal/Vercel-heavy-GPU/L4.

Immutable synthetic result record: `docs/checkpoints/SONGSTERR_FRESH_V6_SYNTHETIC_RESULT.md`, commit `ed0b597d7e86f1756395445952db1f40b62e9b13`.

Artifact:
- name `songsterr-fresh-v6-synthetic-result`
- ID `10316469276`
- ZIP SHA-256 `23e3951dc8796206167642bd980aefb4ad030902f8e4b13fc012a458187cb465`
- result JSON SHA-256 `4991aaec34f71fbb603865e2fcef47c59a551bf1f675b19d9db8318affa0e01a`.

Frozen fixture outcome: 23/23 matched expected behavior:
- corroborated `12`
- not corroborated `7`
- insufficient `4`.

Policy boundary stayed false/zero and `realCorpusEvaluated:false`.

Synthetic success is **not** admission evidence.

### Candidate family B — not promoted

The public `xavriley/hf_midi_transcription` wrapper was inspected at code commit `96f6797881e9497cbfc8f8e5deccea9c1f2f7adc`. Its documentation describes the available models as optimized for monophonic performance and lists chords as a limitation. Therefore it is not currently promoted into V6's core polyphonic admission method. No model inference was run.

## EXTERNAL HOLDOUT SEARCH — METADATA ONLY

No V6 real correctness holdout is frozen yet.

### Guitar-TECHS — leading candidate

Public materials describe real electric-guitar performances, three professional players, varied gear/rooms, DI + amp-mic + ego/exo signals, per-string Fishman Triple Play MIDI, and CC BY 4.0 licensing.

Blocking issue: published materials warn some signal paths may exhibit up to 100 ms temporal misalignment. Therefore **no scoring is allowed yet**.

Before correctness, run a separate reference-blind inventory/alignment audit that freezes:
- exact dataset/version/file identities;
- authoritative audio path;
- MIDI structure/event semantics;
- deterministic audio/MIDI alignment semantics/correction without using Basic Pitch/V6 correctness;
- population and strata definitions;
- license/attribution requirements.

GuitarDuets is not preferred because note-level MIDI is described for its synthesized subset. GAPS is not adopted because public licensing statements conflict across distribution surfaces and it is unsuitable if the GAPS model were used.

## NEXT ALLOWED ACTION

Proceed now with a **Guitar-TECHS metadata/reference-blind alignment-semantics audit preregistration and inventory**. Do not score Basic Pitch or V6 correctness.

After that, if Guitar-TECHS is structurally suitable, freeze one final V6 method/runtime and a separate external scoring protocol before any correctness run.

Ask the user before any Modal, Vercel heavy-GPU or L4 run.

## STILL FORBIDDEN

- V5 FLGD rerun/post-result tuning
- using FLGD/IDMT/GuitarSet correctness to tune V6
- Guitar-TECHS correctness scoring before frozen alignment/inventory + scoring preregistration
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus threshold/optimizer sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without untouched external validation + separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue from this file on `songsterr-fresh-pipeline-v1`.

V5 is closed/rejected. V6 onset-birth synthetic contract is green and immutable at `ed0b597d7e86f1756395445952db1f40b62e9b13`; no real correctness has been run.

Next: preregister and execute a metadata/reference-blind Guitar-TECHS inventory/alignment audit only. Keep FLGD/IDMT/GuitarSet correctness closed; do not resume V143/Gomyway; ask only before Modal/Vercel-heavy-GPU/L4 runs.
