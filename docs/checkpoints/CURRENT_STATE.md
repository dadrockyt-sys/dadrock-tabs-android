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

Preregistered discovery players `02/04` only; player `05` reserved for later confirmation; `00/01/03` sealed.

Discovery run `33582980473`, job `100101041812`: SUCCESS.

Frozen outputs:
- 7,518 octave-proposal events across 117 tracks;
- report SHA256 `5250a27c0249b019e2f080a2ef754290d31ce8d3ff0a66779c51b0b7cfbfb509`;
- labeled rows SHA256 `a8d0852333a4f277b180dc1585b09b304d441171ef0b252c7c80b588d1411b9b`;
- artifact ID `9829078706`, ZIP SHA256 `2f7353b3bd82cd3d0dc5db08bcc0490656defb956e55c1a7da3cd6a0f5b4eff1`.

Primary classes: beneficial 119 (**1.5828677839851024%**), neutral 2669 (**35.50146315509444%**), harmful 4730 (**62.91566906092046%**). Octave-up is especially harmful; octave-down remains mostly harmful.

Result checkpoint `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_RESULT_20260902.md`, creation commit `cbc1e4c3e7c67e668519c70b6b94c81aa17fb699`.

## V4 conservative discovery family — FROZEN BEFORE EXACT FAMILY SCORE

Exploratory discovery evidence identified one conservative, physically interpretable pocket: high-register, short-duration **octave-down** proposals.

Family preregistration:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_PREREGISTRATION_20260902.md`;
- creation commit `b47a7e7a19ac865366295dfed7c5b3d7b7b00334`.

Every config requires frozen V2 direction down by exactly 12 semitones, baseline MIDI pitch >=72, and duration at/below the config threshold:
- `H72-D025` <=0.25 s;
- `H72-D030` <=0.30 s;
- `H72-D035` <=0.35 s.

Frozen reference-blind selected-event counts from candidate features: 107 / 137 / 157 respectively. `H72-D035` discovery one-event labels were 11 beneficial, 146 neutral, 0 harmful; player `02` net +1, player `04` net +10; strict50 net +12.

Exact multi-event discovery-family evaluator:
- `validation/open_corpus/evaluate_guitarset_v4_discovery_family.py`;
- creation commit `95cd1a88ed1ef2a7a7bc1d96bc30194ba58e7c21`;
- blob `254b495c55149725dae5795b83278787b4930869`.

Static guards workflow creation commit `c021cd4410a06e6d3497c062a3db2ec264bf38be`; run `33583946815`, job `100104012439`: **SUCCESS / V4_DISCOVERY_FAMILY_STATIC_PASS**. No real JAMS/audio, no Basic Pitch, player05ReferenceRead=false, confirmation score calls=0, prospective evaluation score calls=0, V168 score calls=0.

Frozen exact discovery-family qualification requires: event-count identity; strictly positive primary macro and combined micro gains; nonnegative player-02/player-04 primary micro deltas; nonnegative strict50 combined micro delta; and **zero discovery tracks with negative primary TP delta**. Deterministic selection is highest primary combined micro gain, then macro, then strict50 micro, then fewest changes, then lexical ID.

No exact family score has run yet. Player `05` remains unread for V4 references.

## NEXT SAFE ACTION

1. Run exactly one exact multi-event V4 family score on discovery players `02/04` only using the frozen evaluator/family and immutable candidate artifact.
2. If no config qualifies, close V4 family and keep player `05` unread.
3. If one config is selected, immediately checkpoint its exact discovery score and then freeze a separate one-shot player-`05` confirmation scorer/gate **before** any player-05 V4 reference use.
4. Do not touch prospective evaluation players `00/01/03` unless a later frozen player-05 confirmation passes.
5. GOAT approval remains the independent primary V168 path; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
