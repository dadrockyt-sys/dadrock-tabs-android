# Songsterr Fresh — FLGD V5 Post-Result Policy Review

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **V5 ADMISSION REJECTED / FAIL-CLOSED**

## Authority and ordering

This review occurs only after the immutable official result was recorded in:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`
commit `df6a306a055303a6f37b229bfc9e538803f25337`.

It applies the frozen policy and scoring gates from:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`
- `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`
- `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`.

This review does not modify the V5 method, Basic Pitch settings, matching semantics, tolerances, gates, files, strata or holdout population.

## Validity of the revealed result

The official FLGD V5 execution is accepted as a valid completed external-validation result, not an infrastructure failure:
- workflow run `34748789583`, job `103701492462`: SUCCESS;
- all 79 performances completed;
- decoded/classified events `84,577 / 84,577`;
- event-preservation gate `true`;
- population-completeness gate `true`;
- identity/runtime guards `true`;
- fail-closed policy-boundary guard `true`;
- reference-blind phase 1 completed all 79 performances before scoring;
- official result identity guard passed;
- result JSON SHA-256 `a79a09a695142ccd8c68d7d04089bb0d3ec675c11c6a39167f1e1cd0740b9c04`;
- artifact ID `10316047064`, archive SHA-256 `04bf94764c38346298f78d04ee8419f1f663091cc8abe31ee827f4c54df42fb7`.

Therefore the FLGD holdout is revealed and may not be rerun under this preregistration to seek a better result.

## Frozen mandatory-gate evaluation

The frozen preregistration requires every mandatory gate to pass.

Observed pooled result:
- V5-positive events: `43,349`;
- positive correct: `27,850`;
- point precision: `0.642460033680131`;
- one-sided 95% Wilson lower bound: `0.6386648804090969`;
- required pooled Wilson lower bound: `>= 0.9900`.

Gate outcomes:
- population completeness: PASS;
- event preservation: PASS;
- minimum evidence volume >=1,000 positives: PASS;
- pooled Wilson lower bound >=0.9900: **FAIL**;
- split robustness >=0.9500 where >=100 positives: **FAIL** for train, validate and test;
- guitar-type robustness >=0.9500 where >=100 positives: **FAIL** for nylon, electric, acoustic and electric-band;
- identity/runtime guards: PASS;
- policy boundary: PASS.

The harness result reports:
- `allMandatoryGatesPassed:false`;
- `externalValidationPassed:false`.

No diagnostic field may override a failed admission gate.

## Policy decision

**V5 is rejected for model-evidence admission.**

The official external validation did not meet the frozen 0.9900 pooled Wilson-lower-bound requirement and did not meet the required split or guitar-type robustness bars. Because all mandatory gates were preregistered as conjunctive, V5 cannot be approved for customer admission or delivery advancement.

This decision is final for the V5/FLGD preregistration. The failed result must not be repaired by post-hoc threshold changes, Basic Pitch changes, matching changes, file/stratum exclusions, alternate confidence intervals or FLGD reruns.

## Authority after review

The following remain unchanged and fail-closed:
- `modelValidationComplete:false`;
- customer-eligible events: `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- protected song remains embargoed;
- Policy C remains `UNENROLLED`;
- no Production change is authorized;
- no `/ai-tab` customer admission change is authorized.

V5's reference-blind classifier may remain preserved as historical research code/artifact, but it has no admission authority.

## Research-contamination boundary after result

FLGD is now a revealed V5 correctness corpus. It is no longer eligible as an untouched admission holdout for a successor method whose design is influenced by this result.

Do not:
- rerun FLGD V5 to seek a better result;
- tune V5 constants or thresholds from FLGD correctness;
- alter Basic Pitch settings under the V5 preregistration;
- change matching tolerances/gates after the result;
- exclude FLGD rows, files, splits or guitar types post hoc;
- reopen GuitarSet/V3 or IDMT/V4 as untouched holdouts;
- use protected-song outcomes to develop or validate a successor admission method;
- resume archived V143/Gomyway / GOAT/reference scoring, duration research or protected-song execution without explicit user authorization.

## Successor boundary

No successor method is authorized by this policy review itself.

If the user explicitly authorizes a successor research line, it must be treated as a new method rather than a V5 result-seeking retune. Any future admission claim requires a new preregistration and a genuinely untouched external holdout selected before correctness is observed. Previously revealed FLGD/GuitarSet/IDMT correctness may be historical diagnostics only, subject to the successor preregistration's contamination rules.

## Final status

V5 external validation: **FAILED**.
V5 admission: **REJECTED**.
Customer/model authority: **UNCHANGED / FALSE / ZERO**.
Protected song: **EMBARGOED**.
Duration authority: **PAUSED / UNCHANGED**.
Archived V143/Gomyway: **CLOSED**.

Next action: no further research execution until the user explicitly authorizes a new successor scope or another currently closed scope.
