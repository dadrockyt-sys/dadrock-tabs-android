# Astra — current handoff

Updated: 2026-09-28 UTC
Branch: `astra-work`
Canonical file: `docs/checkpoints/CURRENT_STATE.md`

Status: **REAL-DOMAIN FAILURE LOCALIZATION COMPLETE — P1 STATE REPRESENTATION FAILURE + P2 ATTACK-DOMAIN MISMATCH FROZEN; P3 SEALED**

## Standing policy

Routine GitHub work and bounded inexpensive synthetic GitHub model runs remain pre-authorized.

P1/P2/P3 real-data access remains a separate boundary.

## Canonical localization run

- run **36392740663**
- job **108832021154**
- head `a5ecdc519b557849ae98825f8c50b219c15527d4`
- workflow **SUCCESS**
- artifact **10957888924**
- digest `sha256:bc766cf7082bbdc92f82dda9818b2981bf329e67b5b80bdd6f84ac8d27fc7f74`
- optimizer steps **0**
- thresholds fixed **0.50 / 0.50**
- threshold search **no**
- model weights changed **no**
- normalization fed to model **no**
- P1 accessed **yes**
- P2 accessed **yes**
- P3 opened **no**

Frozen result:
- `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_RESULT_V1.json`

Analysis:
- `docs/astra/REAL_DOMAIN_FAILURE_LOCALIZATION_ANALYSIS_V1.md`

## P1 localization

Historical V3 baseline:
- exact string/fret top-1 **56.25%**
- pitch-only top-1 **56.25%**
- median absolute semitone error **0**
- median true-state global rank **1**
- top-5 true-class rate **87.5%**

Synthetic candidate:
- exact string/fret top-1 **6.25%**
- pitch-only top-1 **31.25%**
- wrong-string/correct-pitch top-1 **25%**
- median absolute semitone error **11.5**
- median true-state global rank **13.5**
- top-5 true-class rate **31.25%**

Interpretation:
- candidate state/pitch representation is not real-domain compatible;
- not primarily a simple string-assignment swap.

P1 onset:
- baseline threshold crossing within +/-1 frame **100%**
- candidate **18.75%**

## P2 localization

Both models remain onset-limited.

Baseline:
- reference onset probability mean **0.0049**
- max within +/-4 mean **0.0190**
- threshold crossing within +/-4 **0%**

Candidate:
- reference onset probability mean **0.0441**
- max within +/-4 mean **0.0642**
- threshold crossing within +/-4 **0%**

Median local-max offsets are only **0-1 frame**, so a small timing offset does not explain failure.

Attack novelty:
- synthetic k=1 spectral flux mean **26.54**
- P1 **14.42**
- P2 **8.51**

Frame-difference L2 k=1:
- synthetic **2.923**
- P1 **1.972**
- P2 **1.419**

Interpretation:
- P2 attack/capture domain presents substantially weaker novelty;
- shared onset failure is more consistent with attack-domain mismatch than one model's threshold or decoder.

## Do not

- lower thresholds;
- tune on these eight real examples;
- seed/model-pick;
- normalize model inputs post hoc;
- open P3.

## Next design-only proposal

- `docs/astra/P2_ATTACK_PREPARATION_INTEGRITY_AUDIT_PROPOSAL_V1.md`

Purpose:
- distinguish genuinely weak P2 transients from preprocessing/resampling or source-to-prepared timing issues.

**Do not execute yet. Fresh explicit P1/P2 source access authorization is required.**

P3 remains sealed.
