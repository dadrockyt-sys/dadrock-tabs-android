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

## V4 development-only discovery — COMPLETED / FROZEN

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_PREREGISTRATION_20260902.md`;
- creation commit `fc542909f4faa53263c79d519d053450277acffb`.

Frozen partition:
- discovery `02/04`: 117 tracks;
- internal confirmation `05`: 60 tracks, **still unread for V4 per-event labels**;
- prospective evaluation `00/01/03`: **still sealed**.

Frozen analyzer blob `f25706803b5ae0f46be59c95cd3e1485cefd3aba`. Static run `33582924789`, job `100100868170`: SUCCESS.

Real discovery run `33582980473`, job `100101041812`: **SUCCESS**.

Frozen outputs:
- 7,518 trigger-eligible ordinary-V2 octave proposals across 117 tracks;
- report SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`;
- labeled rows SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`;
- artifact ID `9829078706`, ZIP SHA256 `2f7353b3bd82cd3d0dc5db08bcc0490656defb956e55c1a7da3cd6a0f5b4eff1`.

Primary 100 ms event classes:
- beneficial 119 / 7,518 = **1.5828677839851024%**;
- neutral 2,669 / 7,518 = **35.50146315509444%**;
- harmful 4,730 / 7,518 = **62.91566906092046%**.

By direction:
- octave-up: 9 beneficial / 2,113 (**0.4259346900141978%**), 1,535 harmful (**72.64552768575486%**);
- octave-down: 110 beneficial / 5,405 (**2.0351526364477337%**), 3,195 harmful (**59.11193339500463%**).

By player:
- `02`: 60 beneficial / 4,221 (**1.4214641080312722%**), 2,844 harmful (**67.37739872068231%**);
- `04`: 59 beneficial / 3,297 (**1.789505611161662%**), 1,886 harmful (**57.203518350015166%**).

Dedicated result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_RESULT_20260902.md`;
- creation commit `cbc1e4c3e7c67e668519c70b6b94c81aa17fb699`.

No V4 trigger has been selected. Player `05` referenceRead=false / perEventLabelsComputed=false. Prospective evaluation score calls=0. V168 score calls=0.

## NEXT SAFE ACTION

1. Analyze only the already-frozen `02/04` labeled discovery rows using the preregistered reference-blind feature set; checkpoint the feature-level findings.
2. Formulate at most a small interpretable V4 candidate family with exact thresholds from discovery only.
3. Before any player `05` reference use, separately freeze the V4 candidate family, one-shot confirmation scorer, confirmation qualification gate, and deterministic selection rule.
4. Do not touch prospective evaluation players `00/01/03` unless a V4 design later passes the frozen player-05 confirmation gate.
5. GOAT approval remains the independent primary V168 path; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
