# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SUCCESSOR INTEGRATION PRE

Status: **PROSPECTIVE / FROZEN ON FIRST COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `00be878018b1e7c36a3284083fd4701902c985f4`

This PRE is created after the frozen V3 synthetic iteration-3 PASS and before any successor integration code is written or executed. It defines a narrow mechanical integration boundary only. It is **not** a new correctness gate, does not advance delivery, and does not authorize real-media/model execution.

## 1. FROZEN INPUT EVIDENCE

The only positive input to this successor design is the frozen synthetic iteration-3 result:

- PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION3.md`, commit `26ac58fe54c179744ef036a9dc4f4a7d69598038`;
- result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION3.md`, commit `e97ab67c9c2794f4a50c5170102d1380484f5fb1`;
- iteration-3 module blob: `39629250c6d141d5cda9e9d7f570580ec725ae42`;
- frozen result: 34 fixtures, three in-process repetitions, deterministic, zero mismatches, `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`.

Iterations 1 and 2 remain permanent FAIL history. The EGFxSet V2 diagnostic remains a frozen non-authorizing FAIL. AG-PT-set remains frozen structural decision C. None of those records may be rewritten or used for threshold tuning.

## 2. PURPOSE

The successor integration, if implemented under this PRE, may only establish that the already-frozen V3 iteration-3 in-memory composite can be wired into a new successor onset-birth research module without changing frozen V6/V2 code or boundary semantics.

It must not claim real-world correctness, calibrated performance, model validation, customer eligibility, or delivery readiness. The authoritative calibrated/holdout route remains unchanged and budget-paused.

## 3. FROZEN/READ-ONLY FILES

The following remain byte-for-byte read-only during this integration line:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py`;
- all V3 iteration PRE/result checkpoints;
- all `.github/workflows/**`;
- `songsterr_pipeline/**`;
- every closed line listed in `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.

The historical V6 `TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN = 0.20` value remains frozen historical evidence. It is not lowered, removed, or edited in V6.

## 4. PROSPECTIVE WRITE BOUNDARY

After this PRE is frozen, successor integration work may create/change only:

- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py` — new successor research module;
- `scripts/songsterr-fresh/test_onset_birth_corroboration_v7_integration.py` — local synthetic/mechanical integration regression only;
- `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_INTEGRATION_RESULT.md` — first-result record;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state transition record only.

No existing V6/V2/V3 implementation file may be edited. Any additional filename requires a new prospective PRE before creation.

## 5. SUCCESSOR INTEGRATION SEMANTICS

The new `onset_birth_corroboration_v7.py` must be a successor research module, not an in-place V6 patch.

Frozen integration order for an ordinary in-clip selected proposal:

1. reuse the frozen V6 onset-innovation construction semantics without changing frame geometry, FFT size, pre/post novelty definition, minimum analysis RMS, minimum innovation norm, playable MIDI range, or exact selected proposal identity;
2. construct the same frozen FFT frequency grid;
3. pass only the in-memory `innovation`, `frequencies`, and `selected_midi` into frozen `physical_template_plausibility_v3_iteration3.evaluate_evidence_significance_composite()`;
4. never promote a V3 iteration-3 failure;
5. map an iteration-3 PASS to a successor research PASS while preserving the iteration-3 diagnostics, including `necessityFraction`, lower-owner diagnostics, and `candidateEvidenceFraction`;
6. preserve fail-closed behavior for malformed/nonfinite/insufficient inputs.

The successor must not add a Basic Pitch confidence term, per-MIDI exception, EGFxSet special case, real-data threshold, dataset-specific branch, learned parameter, or post-result threshold search.

## 6. BOUNDARY SEMANTICS

This PRE does not authorize changing clip-start routing. Frozen `qualify_basic_pitch_note_births_v2.py` remains read-only and therefore no production or real pipeline is switched to V7 under this integration line.

The successor module may expose only an in-memory/local research entry point suitable for deterministic synthetic/mechanical integration tests. It must not expose dataset download, audio-file loading, network, workflow-dispatch, model/Demucs/Basic-Pitch inference, protected-song access, or repository mutation paths.

## 7. MECHANICAL REGRESSION GATES — NOT CORRECTNESS CLAIMS

The first committed V7 implementation/test pair may be executed locally only if all of the following are frozen in code before execution:

1. the exact 34 iteration-3 synthetic fixture expectations remain unchanged and are evaluated through the successor integration path;
2. every inherited iteration-3 PASS remains PASS and every inherited iteration-3 FAIL remains FAIL;
3. the octave-alias lower-owner case still fails through `LOWER_OWNER_EXPLAINS_SELECTED` with MIDI 57 represented among vetoing owners;
4. no iteration-3 failure is promoted by the successor mapping;
5. every successor PASS carries finite `necessityFraction >= 0.01` and finite `candidateEvidenceFraction >= 0.10` from the frozen V3 composite;
6. scale-control outcomes remain unchanged;
7. repeated execution is deterministic;
8. frozen dependency Git blobs remain unchanged;
9. PRE-to-pair compare contains only the two prospectively allowed new Python files;
10. no workflow, network, file-media, model, real-dataset, subprocess, protected-song, GPU/heavy-compute, or closed-line access is imported or executed.

Passing these gates would establish only mechanical successor wiring consistency with the frozen synthetic V3 result. It would not be an additional software-lineage correctness gate and would not authorize real evaluation.

## 8. WORKFLOW ISOLATION

The prior automatic-trigger audit remains applicable because no `.github/workflows` file changed between audit commit `cc924c96abf70b23e79bda60010d6c8466a1d301` and PRE parent `00be878018b1e7c36a3284083fd4701902c985f4`.

Before committing executable successor files, re-check the exact new paths `scripts/songsterr-fresh/onset_birth_corroboration_v7.py` and `scripts/songsterr-fresh/test_onset_birth_corroboration_v7_integration.py` against current automatic workflow path filters. If trigger isolation is not provable, stop and harden the workflow boundary prospectively without dispatching any closed job.

## 9. FIRST-RUN / RESULT POLICY

If successor implementation proceeds:

- commit the first module/test pair before observing its output;
- verify exact Git blob identity in the local execution copy;
- run only the prospectively defined local integration test command once;
- freeze the first result exactly as observed in the dedicated result checkpoint;
- do not tune, rescue-rerun, or modify the first implementation/test pair after observing a mismatch;
- any revision after a failed first result requires a new prospective iteration PRE.

## 10. EXPLICIT PROHIBITIONS

This PRE does **not** authorize:

- editing frozen V6/V2/V3 files;
- Basic Pitch or Demucs/model inference;
- any V6/V7 real correctness run;
- EGFxSet retry or reuse for tuning;
- AG-PT-set re-audit or payload repair;
- any rejected holdout payload access;
- protected-song execution;
- physical calibration/capture;
- heavy GPU workflow;
- `main` or Production changes;
- reserved Guitar Fretboard Notes splits;
- GOAT/reference scoring;
- archived V143/Gomyway.

Archived V143/Gomyway remains untouched unless the user explicitly asks to resume it.

## 11. AUTHORIZATION AFTER THIS PRE

This PRE freezes a safe successor integration design boundary. It does not itself authorize any real/model execution or real-media evaluation. Any later real evaluation requires a separately frozen real-evaluation PRE plus explicit user authorization consistent with the current-state checkpoint.
