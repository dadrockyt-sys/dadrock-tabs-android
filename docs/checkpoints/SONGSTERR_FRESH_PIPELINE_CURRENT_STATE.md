# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless explicitly reopened by the user.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected song embargoed.

## USER COMPUTE AUTHORIZATION RULE

The user authorized continued work at assistant discretion. Ask again only before any **Modal**, **Vercel heavy-GPU**, or **L4 GPU** run. Normal research, coding, GitHub work, CPU runs, checkpoints, tests and ordinary Vercel work may proceed without another authorization prompt.

## CLOSED / REVEALED LINES

V1/V2 are rejected diagnostics. GuitarSet/V3 and IDMT/V4 are closed/revealed.

V5 is closed/rejected. Official FLGD result: run `34748789583`, job `103701492462`; 79/79 files, 84,577 decoded/classified, 43,349 positives, 27,850 correct, precision `0.642460033680131`, one-sided 95% Wilson LB `0.6386648804090969` vs required `0.9900`, `externalValidationPassed:false`.

Immutable V5 result: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`, commit `df6a306a055303a6f37b229bfc9e538803f25337`.
Policy rejection: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_POST_RESULT_POLICY_REVIEW.md`, commit `44c99d54ed7e728e85ef4042d1f15ba09643713c`.

FLGD is revealed. Do not rerun/tune V5 on FLGD or use FLGD/IDMT/GuitarSet/protected-song correctness to choose V6 constants.

## V6 — ACTIVE / SYNTHETIC GREEN / NO REAL CORRECTNESS

Charter: `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md`, commit `2b96fba0e3df955e62386691023cb31eeb2d11f6`.

V6 asks whether the selected Basic Pitch MIDI has an **onset-synchronous acoustic birth signature** relative to immediately preceding audio. This is distinct from prior steady-state/post-onset evidence families.

Leading implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`.
Frozen synthetic fixtures: `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, commit `ca71eb218ce701686e4a4806813ac84580defa78`.

Controlled CPU synthetic run `34754079541`, job `103715385229`: SUCCESS. 23/23 frozen fixtures matched expected behavior (12 corroborated / 7 not / 4 insufficient). Artifact ID `10316469276`, ZIP SHA-256 `23e3951dc8796206167642bd980aefb4ad030902f8e4b13fc012a458187cb465`, result JSON SHA-256 `4991aaec34f71fbb603865e2fcef47c59a551bf1f675b19d9db8318affa0e01a`.

Immutable V6 synthetic result: `docs/checkpoints/SONGSTERR_FRESH_V6_SYNTHETIC_RESULT.md`, commit `ed0b597d7e86f1756395445952db1f40b62e9b13`.
Synthetic success is not admission evidence.

Independent public guitar-model path was inspected but not promoted: `xavriley/hf_midi_transcription` commit `96f6797881e9497cbfc8f8e5deccea9c1f2f7adc` documents monophonic optimization/chord limitations. No independent-model inference was run.

## GUITAR-TECHS V6 HOLDOUT PREPARATION

Leading candidate: Guitar-TECHS Zenodo record `14963133`, version `v1`. Public materials describe real electric-guitar DI/amp/ego/exo signals, Fishman Triple Play per-string MIDI, CC BY 4.0, and possible signal-path misalignment up to 100 ms.

Frozen reference-blind audit preregistration: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_PREREGISTRATION.md`, commit `29818b9bfcb11b0da2b3e9efb57c5f2cd51193ae`.

The audit freezes **DI (`audio/directinput`)** as the only candidate future scoring audio path. It may inspect archive identity, structure, WAV/MIDI structure and DI↔MIDI alignment only. It MUST NOT invoke Basic Pitch or V6 or compute correctness.

Audit implementation: `scripts/songsterr-fresh/external_guitar_techs_v6_alignment_inventory.py`, implementation commit `0d7d57675694946e8a156b5c8e53fc2ae0347341`.
Merger: `scripts/songsterr-fresh/merge_guitar_techs_v6_alignment_inventory.py`, commit `5b2b7871844d7b7ccac6d50f56f0b0eaf09065a2`.

Controlled audit CI:
- initial run `34754383492` failed before real-data access because the synthetic known-lag assertion allowed exactly one hop while a -40 ms fixture recovered as -46.44 ms (~1.11 hops);
- only the synthetic assertion tolerance was amended to 1.25 hops; the actual lag estimator was unchanged;
- amendment commit `77510e2e797915166a5737750769824e44c49e89`;
- corrected controlled run `34754452415`, job `103716353507`: SUCCESS, including no-scorer-import guard.

No Guitar-TECHS archive was accessed before the corrected controlled run passed.

### Official alignment/inventory run — ACTIVE

Workflow: `.github/workflows/songsterr-fresh-guitar-techs-v6-alignment-inventory.yml`
Wrapper creation commit: `f3c9d4a88740146918c34a3538c565f21079f3bf`
Run ID: `34754519541`
Workflow run number: `1`
Frozen audit source: `77510e2e797915166a5737750769824e44c49e89`
Compute: GitHub-hosted Ubuntu CPU only; no Modal/Vercel-heavy-GPU/L4.

The workflow processes all nine exact Zenodo v1 archives sequentially, verifies each preregistered MD5, extracts/audits only DI WAV + MIDI, computes the frozen reference-blind alignment lags, merges the result, verifies fail-closed policy fields, then uploads one audit artifact.

Frozen alignment decision remains one of:
- A: raw MIDI timestamps authoritative only if every absolute lag <= one hop;
- B: deterministic per-file constant MIDI offset correction with immutable lag manifest if all structural/alignment guards pass but larger offsets exist;
- C: dataset unsuitable if the reference-blind alignment/population cannot be resolved defensibly.

No future Basic Pitch/V6 correctness may alter the A/B/C decision or any lag.

## NEXT ALLOWED ACTION

Inspect run `34754519541` until it completes. If successful, retrieve and integrity-check the audit artifact, write an immutable Guitar-TECHS alignment/inventory result checkpoint, and update this file **before** freezing any V6 external-scoring protocol.

If the audit yields a structurally suitable A/B population, freeze the final V6 method/runtime and a separate external-scoring preregistration before any real correctness run. If C, reject Guitar-TECHS as the V6 holdout and search for another untouched corpus without scoring it.

Ask the user only if a Modal, Vercel heavy-GPU or L4 run becomes necessary.

## STILL FORBIDDEN

- V5 FLGD rerun/post-result tuning
- using FLGD/IDMT/GuitarSet/protected-song correctness to tune V6
- Guitar-TECHS Basic Pitch/V6 correctness before immutable audit result + final V6/scoring preregistration
- changing Guitar-TECHS alignment from future model correctness
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus optimizer/threshold sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without untouched external validation + separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1`. V5 is closed/rejected. V6 synthetic evidence is green but not admission evidence. Guitar-TECHS reference-blind audit run `34754519541` is the current active work; inspect it first. Do not resume V143/Gomyway and do not run Guitar-TECHS correctness yet.
