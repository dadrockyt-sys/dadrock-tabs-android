# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SUCCESSOR INTEGRATION RESULT

Status: **PASS_SYNTHETIC_MECHANICAL_INTEGRATION**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Prospective PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_INTEGRATION_PRE.md`
PRE commit: `638b045aea5a9fc66cee30c78772e792b38b8c79`
Workflow-isolation state commit: `d45f0ed194ed53a08c0ec17b257c10a262361108`
V7 module commit: `a2d312aa1dfd86be617fba35724de8aa1fba40d6`
Complete first V7 implementation/test pair head: `efca69ff4f045214eec629ad94596434039f02b9`

This checkpoint freezes the first and only local synthetic/mechanical execution of the first committed V7 successor integration pair. It is not a real-media correctness result, model validation result, calibrated result, holdout result, customer-eligibility result, or delivery authorization.

## 1. EXACT COMMITTED BLOBS EXECUTED

The local execution copy was verified by Git blob SHA-1 before execution:

- frozen V6 `onset_birth_corroboration_v6.py`: `2b18ef0ee710a6ad5ecb27253b977495db7d6534`
- frozen V3 iteration-1 base `physical_template_plausibility_v3.py`: `45b8f3b66df7500824071489205a732dfe05d759`
- frozen V3 iteration-2 wrapper: `7090e17baff60f91700a760f617e905ff53484ab`
- frozen V3 iteration-3 wrapper: `39629250c6d141d5cda9e9d7f570580ec725ae42`
- frozen iteration-2 fixture harness: `eefe00346a94e8f0ed433ac916352a4b2e9331c5`
- frozen iteration-3 fixture harness: `76455337bd17a952dd36c1dabd03ce741e806b07`
- new V7 successor module `onset_birth_corroboration_v7.py`: `6dfadda70db6b902f1dcc4d804f2d66da547314d`
- new V7 integration regression `test_onset_birth_corroboration_v7_integration.py`: `a5443cae88f4ba49e5a9712822a5c371b67a1c30`

All eight local files matched their exact Git blobs before the first run.

## 2. EXECUTABLE-DIFF BOUNDARY

The exact executable delta from the recorded post-audit state `d45f0ed194ed53a08c0ec17b257c10a262361108` to pair head `efca69ff4f045214eec629ad94596434039f02b9` contains exactly two files:

- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`
- `scripts/songsterr-fresh/test_onset_birth_corroboration_v7_integration.py`

No frozen V6/V2/V3 implementation file and no workflow file changed in that executable delta.

The literal PRE-to-pair history also contains the prospectively allowed current-state documentation update used to record the required exact-path workflow audit. No executable file other than the two V7 files was added or modified after that audit baseline.

## 3. WORKFLOW / I-O ISOLATION BEFORE EXECUTION

Before the pair was created, exact-path workflow isolation was re-verified and recorded in `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`:

- no `.github/workflows/**` file changed from the previously audited baseline through the V7 pre-code state;
- the unchanged audit had already established path-filtered automatic pushes and no catch-all `scripts/songsterr-fresh/**` automatic push path;
- exact workflow/code searches found no `onset_birth_corroboration` workflow-path reference;
- neither proposed V7 filename matched an audited automatic workflow path.

A final static scan of the exact new pair before execution found no file/network/process/model imports or direct `open`/dynamic-execution calls in the V7 module or integration test. The frozen V6 module contains a pre-existing dormant manifest `read_text()` self-test path, but that path was not reachable from or invoked by the V7 integration command. No network, workflow, dataset, model, subprocess, protected-song, or repository mutation path was executed.

## 4. FIRST AND ONLY EXECUTION

Only this prospectively defined local command was executed once:

`python3 test_onset_birth_corroboration_v7_integration.py`

Canonical first-run summary:

```json
{"compositeFixtureCount":33,"contract":"songsterr-fresh-v7-successor-integration-synthetic-test-v1","deterministic":true,"directTemplateFixtureCount":1,"fixtureCount":34,"mechanicalCheckCount":4,"mismatchCount":0,"mismatches":[],"repetitions":3,"result":"PASS"}
```

Process exit: `0`.

No rescue rerun, threshold change, fixture change, expectation change, code change, or post-result tuning occurred.

## 5. FROZEN OBSERVATIONS

The 34 frozen iteration-3 fixture expectations were preserved unchanged.

- 33 composite fixtures were routed through the V7 successor mapping to frozen V3 iteration 3.
- The remaining one fixture, `input_fewer_than_three_available_harmonics`, is the frozen iteration-3 suite's direct-template structural control rather than a selected-proposal composite. It remained byte-for-byte sourced from the frozen harness and retained its expected `FEWER_THAN_THREE_AVAILABLE_HARMONICS` result. It does not call V7 because the frozen fixture directly exercises the base anchor helper at MIDI 120, outside the selected-proposal V7 playable-range contract.
- This distinction was frozen in the committed first test before execution; no fixture or expectation was changed after the result.

The four prospectively committed mechanical checks all passed:

1. frozen V6/V3 dependency contracts and constants matched;
2. the V7 frequency grid matched the frozen V6/V3 `44100 / 8192` grid;
3. boolean MIDI input failed closed;
4. missing V6 pre/post audio context failed closed with `REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO`.

The octave-alias lower-owner case remained a failure through `LOWER_OWNER_EXPLAINS_SELECTED`, with MIDI 57 present among vetoing owners. No frozen V3 failure was promoted. Every successor PASS carried finite `necessityFraction >= 0.01` and finite `candidateEvidenceFraction >= 0.10`, with no vetoing lower owner. The three iteration-3 scale-control outcomes remained unchanged.

## 6. RESULT INTERPRETATION

Frozen result: **PASS_SYNTHETIC_MECHANICAL_INTEGRATION**.

This establishes only that the new V7 in-memory successor mapping is mechanically consistent with the frozen V3 iteration-3 synthetic evidence and the frozen V6 onset-innovation geometry under the committed local regression.

It does **not** establish:

- real-media correctness;
- model correctness or Basic Pitch validation;
- calibrated physical performance;
- holdout validity;
- EGFxSet repair;
- AG-PT-set repair;
- threshold generalization;
- customer eligibility;
- delivery readiness.

## 7. AUTHORIZATION BOUNDARY AFTER THIS RESULT

No real/model evaluation is authorized by this PASS. Frozen V6/V2 remain unchanged. No production route was switched to V7.

Any real-media/model evaluation requires a separately frozen real-evaluation PRE plus new explicit user authorization. Until then, permitted work remains documentation/design/local static reasoning that does not access real candidate payloads or invoke Basic Pitch/Demucs/model inference.

Archived V143/Gomyway remains untouched and must not be resumed unless the user explicitly asks.