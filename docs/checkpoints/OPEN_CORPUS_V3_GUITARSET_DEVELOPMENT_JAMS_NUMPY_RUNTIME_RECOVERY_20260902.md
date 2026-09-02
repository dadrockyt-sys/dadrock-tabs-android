# Open-Corpus V3 GuitarSet Development Scorer — JAMS/NumPy Runtime Recovery

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Classification

**MECHANICAL REFERENCE-PARSER IMPORT FAILURE / SCIENTIFIC RESULT STILL UNOBSERVED.**

This follows the path-only recovery checkpoint `OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_SCORER_PATH_RECOVERY_20260902.md` and does not change any scientific rule.

Recovery workflow commit `b5577db4bb9f929d6307b303f78188adf14dd730` launched Actions run `33582237435`, job `100098746109`.

## What passed before the failure

The scorer-only recovery successfully verified all frozen identities before references:
- original candidate run `33581322528`;
- original head `f494e5b2f586ec335b16dcabce687e63bb1f88fb`;
- candidate artifact ID `9828683652`;
- candidate artifact digest `sha256:1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- frozen scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`;
- frozen trigger blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`;
- frozen candidate generator blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`.

It downloaded the original artifact, reverified the manifest directly, and rehashed all **177** candidate JSON files successfully before any reference download. No Basic Pitch runtime was present and no candidate was regenerated.

The reference-selection step then:
- downloaded `annotation.zip`;
- passed official MD5 and frozen SHA256 verification;
- extracted exactly 177 development JAMS files (`02`=59, `04`=58, `05`=60);
- extracted no sealed evaluation players `00/01/03`;
- extracted none of the three preregistered anomaly files;
- deleted the annotation ZIP before scoring.

## Exact failure

The unchanged frozen scorer started, entered `load_reference_events`, and failed on the first lazy `import jams` before `jams.load(...)` could execute.

Installed by the workflow:
- `jams==0.3.4`;
- dependency resolver selected `numpy==2.2.6`.

JAMS 0.3.4 imports `np.float_` in `jams/schema.py`. NumPy 2.x removed that attribute. Exact terminal error:

`AttributeError: np.float_ was removed in the NumPy 2.0 release. Use np.float64 instead.`

This is a runtime dependency incompatibility, not a reference-data, candidate, scorer, matching, threshold, or selection-rule outcome.

The failure occurred during Python module import, before the first `jams.load` call completed. Therefore:
- development JAMS files extracted: **177**;
- development JAMS note events interpreted/read by the scorer: **0**;
- development score calls completed: **0**;
- no baseline/config metrics were produced;
- no config qualification was evaluated;
- scientific classification remains **NOT YET OBSERVED**;
- prospective evaluation players `00/01/03` remain unprocessed and unscored;
- V168 prospective reference-facing score calls remain **0**.

The workflow cleanup removed candidate/reference files after failure; no score artifact was produced.

## Frozen minimal recovery

A second scorer-only recovery is permitted with exactly one mechanical runtime change:

**Pin NumPy to `1.26.4` while retaining `jams==0.3.4`.**

Rationale: NumPy 1.26.4 retains `np.float_` and was already used successfully in the V3 static/self-test environment. This pin changes only dependency compatibility; it does not alter the frozen JAMS parser semantics in `score_guitarset_v3_development_candidates.py`.

No other dependency, parser, scientific code, candidate payload, trigger configuration, threshold, matching tolerance, development split, anomaly exclusion, or selection rule may change in this recovery unless a new mechanical failure is separately checkpointed before correction.

The next recovery must again reuse the original frozen candidate artifact, reverify all hashes before references, use no Basic Pitch/audio/candidate generation, and process only the same 177 development JAMS files.

## Evaluation / V168 boundary

Prospective GuitarSet evaluation players `00/01/03` remain sealed. V168 remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; GOAT access remains pending. `main` / Production remain untouched. GPU/CUDA/Modal remain unauthorized.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
