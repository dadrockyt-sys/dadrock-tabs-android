# Songsterr Fresh — Independent Corroboration V1 Authorized-Song Result

Recorded: 2026-09-11 America/Toronto

Status: **RESEARCH RESULT ONLY / NON-PROMOTIONAL**

## Execution identity

- Policy: `POLICY_C_S_CODESPACES_SESSION_AUTHORITY`
- Authority epoch: `62a82204-e0cc-4daa-8022-93f73352310f`
- Qualified source commit: `e2efb6392d27edfb37cbb19a2071e5e13fdcb039`
- Session fingerprint SHA-256: `b5ba8ddf3faf2c5f4f948e922e5e29a490ab7650397dee962874852d86ebe887`
- Qualified event count: `1140`
- Session verified before and after research: `true`

## Frozen method boundary

The authorized-song evaluator was `scripts/songsterr-fresh/independent_pitch_corroboration_v1.py` as present in the qualified source commit above. Its method was frozen and controlled-fixture CI was green before this authorized-song execution.

The first attempt to invoke the session-bound wrapper failed before evaluator execution because the wrapper incorrectly looked for `modelValidationComplete` and `customerEligibleEvents` at the top level of the Policy C-S qualification object instead of under `policyBoundary`. That parser-only bug did not alter the evaluator, model outputs, qualification, or research method. The wrapper was corrected later and CI-proved against the actual qualification schema; the corrected wrapper was downloaded to `/tmp` and used without pulling or modifying the qualified repository source.

## Result

Classification counts across all 1,140 qualified events:

- `independently-corroborated-candidate`: **471**
- `not-independently-corroborated`: **667**
- `insufficient-evidence`: **2**

These labels mean only what the preregistered research contract defines. `independently-corroborated-candidate` means the selected MIDI was the unique best candidate, by more than the frozen numerical tie tolerance, in both the fixed spectral-harmonic channel and the fixed time-domain periodicity channel against the fixed competitor set. It is not yet a customer-eligibility decision.

## Policy boundary

The run completed with:

- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`

No reference tab, professional scorer, GOAT data, archived V143 scorer, Basic Pitch activation/decision-surface values, Basic Pitch note-span amplitude, or decoded note ends were used by Independent Corroboration V1.

## Required next review

The preregistration explicitly requires a separate policy review before any customer-eligible subset can be authorized. Aggregate counts alone are insufficient for that review. Before any promotion decision, inspect at minimum the two previously identified stress-test events (MIDI 55 near 46.2024095 s and MIDI 64 near 79.6261406 s) under this frozen method and evaluate whether the contract has enough external/controlled validity to support admission beyond research labeling.

Until that review completes, duration research remains paused and customer delivery does not advance.
