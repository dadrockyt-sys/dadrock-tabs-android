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

GuitarSet v1.1.0 split remains development `02/04/05` (177 after exclusions) vs prospective evaluation `00/01/03` (180, still sealed).

Authoritative V3 candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`; artifact ID `9828683652`, ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

Frozen scorer recovery run `33582451429`, job `100099402236`: SUCCESS. Baseline primary macro F1 **80.3621313923964%**, primary micro **76.62482566248256%**, strict50 micro **74.51882845188284%**. All 8 V3 configs regressed; terminal `NO_DEVELOPMENT_SIGNAL`. Never run V3 on `00/01/03`.

## V4 discovery — COMPLETED / FROZEN

Discovery players `02/04` only; player `05` reserved for confirmation; `00/01/03` prospective sealed.

Discovery run `33582980473`, job `100101041812`: SUCCESS. Frozen output: 7,518 proposal events across 117 tracks; report SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`; labeled rows SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`; artifact ID `9829078706`, ZIP SHA256 `2f7353b3bd82cd3d0dc5db08bcc0490656defb956e55c1a7da3cd6a0f5b4eff1`.

Primary discovery labels: 119 beneficial (1.5828677839851024%), 2669 neutral (35.50146315509444%), 4730 harmful (62.91566906092046%).

## V4 conservative discovery family — `H72-D035` SELECTED

Family preregistration `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_PREREGISTRATION_20260902.md`, creation commit `b47a7e7a19ac865366295dfed7c5b3d7b7b00334`.

Frozen family:
- `H72-D025`: ordinary V2 octave-down only, baseline MIDI >=72, duration <=0.25 s;
- `H72-D030`: same, duration <=0.30 s;
- `H72-D035`: same, duration <=0.35 s.

Evaluator blob `254b495c55149725dae5795b83278787b4930869`. Static run `33583946815`, job `100104012439`: SUCCESS.

Exact family score:
- workflow creation commit `a69788be8498b72224e8d15d99c193016280bb70`;
- run `33584036171`, job `100104285213`: **SUCCESS**;
- exact family score calls = **1**;
- all three configs qualified under the frozen gate;
- frozen deterministic selection chose **`H72-D035`**.

Discovery baseline primary macro F1 **79.23291495571898%**, primary combined micro F1 **75.48820336017702%**.

Selected `H72-D035` changed **157** pitches and achieved:
- primary combined micro gain **+0.05660328813645776 pp**;
- primary macro gain **+0.07533076559106178 pp**;
- player `02` primary micro **+0.010499238805181221 pp**;
- player `04` primary micro **+0.10091835704913876 pp**;
- strict50 combined micro **+0.061749041603405885 pp**;
- negative-primary-TP discovery tracks: **0**;
- positive-primary-TP discovery tracks: **8**.

Frozen report identities:
- score SHA256 `ea8a15ad7d9bb436a3c7108e1cfe67231ac5d2dadf42580abdcc2832ed3339bf`;
- artifact ID `9829448816`;
- artifact ZIP SHA256 `a34320aa04467fd9ca73736e63bb93a603c02b9954c04ebf771fd1eb2bf83cf6`.

Dedicated result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_SELECTED_20260902.md`;
- creation commit `2dfb5e5a5f3b1ecb7195330de012a4c34a8df033`.

Only `H72-D035` may proceed to confirmation. `H72-D025` and `H72-D030` are closed for confirmation. Player `05` V4 referenceRead=false; player-05 confirmation score calls=0. GuitarSet prospective score calls=0. V168 score calls=0.

## NEXT SAFE ACTION

1. Before reading any player-`05` V4 reference, freeze a separate one-shot confirmation contract and scorer for **only `H72-D035`**.
2. Confirmation gate must be fixed before the run and fail closed without threshold tuning. Recommended frozen conditions: event-count identity; primary macro gain >0; primary combined micro gain >0; strict50 combined micro non-regression; no player-05 track primary TP loss.
3. Run static/synthetic guards first. Save CURRENT_STATE again before any real player-05 reference use.
4. Then run exactly one player-05 confirmation. If the scientific gate fails, close V4 without weakening it. If it passes, checkpoint before designing any prospective `00/01/03` workflow.
5. Prospective players `00/01/03` remain sealed now. GOAT remains the independent primary V168 path.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
