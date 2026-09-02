# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is awaiting explicit owner approval/denial.
- No restricted GOAT bytes admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT selection contract and promotion gate unchanged.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate.

Controlled V2 Guitar-TECHS P1/P2 result remains 558/558 when an octave ambiguity is already known. P3 indiscriminate bridge remains terminal `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`.

## V3 GuitarSet — TERMINAL `NO_DEVELOPMENT_SIGNAL`

GuitarSet v1.1.0 split remains:
- development `02/04/05`, 180 nominal / 177 after the three predeclared anomaly exclusions;
- prospective evaluation `00/01/03`, 180 tracks, **still sealed**.

Authoritative V3 development candidates from run `33581322528`, job `100096037798`:
- 29,245 baseline events;
- 10,693 ordinary V2 proposals;
- 10,642 trigger-eligible events;
- manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`, ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

Successful frozen scorer-only runtime recovery:
- run `33582451429`, job `100099402236`: SUCCESS;
- score report SHA256 `80f68643e11644d085674ddbb1771d7bd6502bcc328c94d3cc356aea1a7af057`;
- report artifact ID `9828894162`, ZIP SHA256 `569252da6d45a38e6661a5f26feb1cbbda2c0971c54e979c30470037b2d1087b`.

Baseline development primary macro F1 **80.3621313923964%**, primary micro **76.62482566248256%**, strict50 micro **74.51882845188284%**.

All 8 frozen V3 trigger configs regressed and `qualifiedConfigIds=[]`; `selectedConfig=null`. Least harmful `C100-M020` still lost **1.0012011667825789pp macro**, **1.5306834030683376pp primary micro**, and **1.509762900976284pp strict50 micro** while changing 1620 pitches.

Terminal checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_NO_DEVELOPMENT_SIGNAL_20260902.md`;
- creation commit `cd6e06687d3a5c8f7a0a4c4588ed78f3fd711f3a`.

**Frozen consequence:** do not weaken V3, choose a least-bad config, or run V3 on `00/01/03`. GuitarSet prospective evaluation score calls remain **0**.

## V4 development-only discovery — PREREGISTERED / RUNNING

A distinctly new V4 discovery phase was preregistered before any new per-event reference analysis:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_PREREGISTRATION_20260902.md`;
- creation commit `fc542909f4faa53263c79d519d053450277acffb`.

Frozen V4 partition:
- discovery players: **`02`, `04`** = 117 admissible tracks;
- internal confirmation player: **`05`** = 60 tracks, no V4 per-event reference use until a V4 trigger family/confirmation gate is frozen;
- prospective evaluation players **`00/01/03` remain sealed**.

V4 discovery reuses only the immutable V3 candidate artifact. It performs no audio decoding, Basic Pitch inference, candidate regeneration, or V2/V3 recomputation.

Frozen discovery label: for each trigger-eligible ordinary V2 octave proposal on `02/04`, swap only that one event's pitch to the already-frozen V2 winner, rescore the complete track with the unchanged exact-pitch one-to-one matcher, and label by primary 100ms delta TP (`beneficial` / `neutral` / `harmful`). Strict50 delta TP is secondary.

Allowed trigger-side observables are reference-blind fields already frozen in the candidate artifact: baseline pitch, V2 direction, Basic Pitch amplitude, duration, consensus, median advantage, four per-frame advantages/winners and deterministic summaries. Player may be used only as an analysis grouping column, never as a trigger feature.

Frozen analyzer:
- `validation/open_corpus/analyze_guitarset_v4_discovery.py`;
- creation commit `144c1a801ccbce1832f3d71e785ae512595f54d7`;
- blob `f25706803b5ae0f46be59c95cd3e1485cefd3aba`.

Static guards:
- workflow commit `11ef95aab4f35e658670fb247db8eb624248e1ac`;
- run `33582924789`, job `100100868170`: **SUCCESS / V4_DISCOVERY_STATIC_PASS**;
- no real JAMS, no Basic Pitch/audio, player05ReferenceRead=false, prospective evaluation score calls=0, V168 score calls=0.

Real preregistered discovery:
- workflow creation commit `48d32716fce48556f88c7318366ade373af0faea`;
- run `33582980473`, job `100101041812`;
- current state at this checkpoint: **IN PROGRESS** after candidate identity/hash verification and discovery-reference isolation began/completed; no V4 trigger selection is permitted by this run.

## NEXT SAFE ACTION

1. Check run `33582980473` to completion.
2. If discovery completes, freeze report/row hashes and checkpoint the `02/04` event-class/feature evidence before formulating any V4 trigger family.
3. Do not read player `05` V4 per-event references until a small V4 trigger family, confirmation qualification gate and deterministic selection rule are separately frozen.
4. Do not touch prospective evaluation players `00/01/03`.
5. GOAT approval remains the independent primary V168 path; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
