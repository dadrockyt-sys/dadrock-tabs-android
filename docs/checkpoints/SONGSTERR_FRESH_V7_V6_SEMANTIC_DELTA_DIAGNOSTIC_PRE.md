# PRE — Songsterr Fresh V7 / Frozen V6 Semantic-Delta Diagnostic V1

Status: **PROSPECTIVE / DIAGNOSTIC-ONLY / FROZEN ON THIS COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`

## 1. Frozen motivation

The frozen dual-view diagnostic result is:

`COMPLETE_SYNTHETIC_DUAL_VIEW_DIAGNOSTIC_NO_DECISION`

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V7_DUAL_VIEW_DIAGNOSTIC_RESULT.md`
Commit: `c5833a75634ad2b2999dac49299deb821886dc27`

It established:

- `selected64_enters_over_existing60`: support-view necessity `0.001749...`, but raw-view necessity against the same support-derived dictionary `0.229332...`; separating support from fit evidence is mechanically useful here;
- `simultaneous_dyad_sel60`: support-view necessity `0.184090...`, dual raw-view necessity `0.148935...`; the false positive is not a sparsified-fit artifact;
- `reattack_m64`: selected support template is `NO_ELIGIBLE_DETUNING_ANCHOR`; the failure is upstream of fitting.

The frozen V6 fixture manifest nevertheless expects dyad selected MIDI60 to reject and reattack MIDI64 to corroborate. Frozen V6 uses a different candidate-template plausibility model before NNLS. This diagnostic measures that exact semantic delta without adopting V6's historical `0.20` gate as a new rule.

## 2. Diagnostic question — no new classifier

For every frozen V6 audio fixture, record side-by-side:

1. frozen V6 raw-innovation selected-template validity/reason and harmonic observations;
2. frozen V6 full classifier/fit diagnostics;
3. frozen iteration-2 peak-band support-view selected-template diagnostics;
4. frozen V3 support-view composite diagnostics;
5. frozen dual-view raw-fit diagnostic metrics from the already-frozen dual-view diagnostic module.

The purpose is to identify which frozen V6 semantic distinguishes the persistent dyad/reattack cases and whether that semantic is independently supported across the remaining controls.

This PRE defines no combined verdict, threshold, promotion/rejection rule, fallback route or real-evaluation rule.

## 3. Frozen population

Use all 23 fixtures from frozen `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json` in manifest order, unchanged.

The manifest's expected classification is reference-only metadata and may not alter computation or process status.

## 4. Required frozen-V6 measurements

For every fully contextualized fixture:

- frozen `_onset_innovation_spectrum()` status, RMS, innovation energy;
- frozen `_candidate_template(selected_midi, raw_innovation, frequencies)`:
  - `valid`;
  - `reason` where invalid;
  - fundamental bin/frequency where present;
  - harmonic bins and observed harmonic innovation where present;
  - fundamental-to-max-harmonic innovation ratio where present;
- frozen `_fit_onset_birth()`:
  - status;
  - passed flag;
  - valid candidate count;
  - feature energy;
  - selected coefficient;
  - necessity fraction;
  - historical fundamental ratio diagnostic;
- frozen `classify_audio_event()` classification/reason as a namespaced historical-component output only.

No frozen V6 output is promoted to a new V7 decision in this diagnostic.

## 5. Required V3 / dual-view comparison measurements

Using frozen bridge V2 and frozen diagnostic V1 unchanged, record:

- support selected-template valid/status;
- selected support cents;
- supported harmonic count / weighted coverage where available;
- support valid candidate count;
- frozen support-view V3 composite status/passed flag;
- support-view necessity where exposed;
- support candidate-evidence fraction where available;
- support credible/veto lower-owner MIDIs;
- dual-view fit availability;
- dual-view selected coefficient / raw feature energy / raw necessity fraction where available.

No new comparison threshold is defined.

## 6. Key diagnostic cases to identify, not score

The output must clearly include the following existing fixtures, without special-case computation:

- `selected64_enters_over_existing60`;
- `simultaneous_dyad_sel60`;
- `simultaneous_dyad_sel64`;
- `simultaneous_triad_sel60`;
- `reattack_m64`;
- `clean_low_m40`;
- both octave alias controls;
- `weak_selected64_under60`;
- `unrelated_transient_only_sel64`.

These names are for result readability only. The diagnostic implementation must iterate the manifest generically and contain no branch on fixture ID.

## 7. Mechanical invariants

- all frozen dependency contracts/blobs remain exact;
- all 23 rows are produced in manifest order;
- three in-process repetitions are canonical-JSON deterministic;
- no final dual-view/V7 decision is defined;
- expected classification is not used for computation;
- all numeric values are finite where available;
- insufficient/context rows remain fail-closed without fabricated evidence;
- diagnostic code performs no network/model/GPU/real-media/repository mutation;
- untouched V3 iteration-3 suite remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

## 8. Frozen/read-only files

Read-only throughout this diagnostic:

- frozen V6 module and fixture manifest;
- all frozen V3 modules/tests;
- frozen V7 successor module;
- bridge iteration-1 and iteration-2 files;
- frozen dual-view diagnostic module/test;
- all prior PRE/result checkpoints/workflows;
- `songsterr_pipeline/**`;
- `main`, Production, closed lines and archived V143/Gomyway.

The historical V6 `TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN = 0.20` remains historical/read-only and is **not** adopted as a V7 threshold under this PRE.

## 9. Prospective write boundary

May create/change only:

- `scripts/songsterr-fresh/v7_v6_semantic_delta_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_v6_semantic_delta_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-v6-semantic-delta-diagnostic-one-shot.yml` if a runner is needed;
- `docs/checkpoints/SONGSTERR_FRESH_V7_V6_SEMANTIC_DELTA_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires another prospective PRE.

## 10. First-run policy

Commit the diagnostic pair before output, verify exact PRE→pair diff/blobs/static isolation, then execute exactly once through a self-scoped synthetic-only workflow if required, with the untouched V3 regression in the same attempt. Freeze the first result. No diagnostic rescue rerun or post-result metric selection.

Any later composition rule must be defined in a new prospective PRE after this result is frozen.

## 11. Explicit prohibitions

No EGFxSet or other real media, no prior Basic Pitch artifact, no Basic Pitch/Demucs/model inference, no real correctness run, no historical V6 threshold adoption/change, no threshold/radius/width search, no fixture-ID branch, no AG-PT/rejected holdout, no protected song, no physical capture/calibration, no `songsterr_pipeline/**`, no `main`/Production, no GOAT/reference, no reserved GFN, no archived V143/Gomyway.

## 12. Authority after result

Measurement only. The diagnostic result will not itself authorize a successor classifier or real/model execution.