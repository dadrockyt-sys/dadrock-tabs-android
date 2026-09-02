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

Development players `02/04/05`; prospective evaluation players `00/01/03` remain sealed. Frozen V3 scorer run `33582451429`, job `100099402236`: SUCCESS and terminal `NO_DEVELOPMENT_SIGNAL`. Never run V3 on `00/01/03`.

Immutable candidate artifact:
- original run `33581322528`;
- manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`;
- ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

## V4 GuitarSet — CLOSED / TERMINAL

Discovery players `02/04` only identified a conservative high-register short-duration octave-down family. Exact discovery-family scoring selected `H72-D035` under the frozen gate:
- discovery-family run `33584036171`, job `100104285213`: SUCCESS;
- selected discovery gains: primary combined micro +0.05660328813645776 pp; primary macro +0.07533076559106178 pp; strict50 micro +0.061749041603405885 pp; 0 negative-primary-TP discovery tracks.

Selected result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_DISCOVERY_FAMILY_SELECTED_20260902.md`;
- creation commit `2dfb5e5a5f3b1ecb7195330de012a4c34a8df033`.

### One-shot player-05 confirmation — FAIL

Frozen confirmation preregistration:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_PLAYER05_CONFIRMATION_PREREGISTRATION_20260902.md`;
- creation commit `3759e73563c5fc93f67407e5e3f9ea37a4e3d584`.

Frozen scorer blob `794011aa78524226ec47e74ca8dd91008eef629a`. Static run `33584362102`, job `100105263075`: SUCCESS.

Real one-shot confirmation:
- workflow creation commit `ae536a761e388e902dbacb0f740305517a81f2a7`;
- run `33584451308`, job `100105524472`: **SUCCESS mechanically, scientific `V4_PLAYER05_CONFIRMATION_FAIL`**;
- player05ReferenceRead=true;
- player05ConfirmationScoreCalls=1;
- 60 tracks, 8715 reference events, 9778 baseline predicted events;
- `H72-D035` changed 91 pitches;
- event-count identity=true.

Primary baseline: TP 7306, macro F1 **82.56410344391738%**, micro F1 **79.01368085221435%**.

Primary `H72-D035`: TP 7301, macro F1 **82.49393805207504%**, micro F1 **78.95960633753313%**.

Confirmation deltas:
- primary TP **-5**;
- primary macro **-0.0701653918423375 pp**;
- primary combined micro **-0.05407451468121849 pp**;
- strict50 combined micro **-0.0540745146812327 pp**.

Track direction counts: 1 positive, 56 neutral, 3 negative. Frozen no-track-loss condition failed, as did all three metric gain/non-regression conditions. Qualification=false.

Frozen report identities:
- report SHA256 `3feb63042c670690221901906045520f17faa01d02a461c01b805ea68867d722`;
- artifact ID `9829578804`;
- artifact ZIP SHA256 `556d301e3466a9f6064d52ccd3e37410b492fac147e20e7833ed8bde65dff300`.

Terminal checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_PLAYER05_CONFIRMATION_FAIL_20260902.md`;
- creation commit `d008ea75c945bbf050d6af0a136367d2ff730c4a`.

**Frozen consequence:** never rerun confirmation, weaken the V4 gate, try another V4 family member on player05, or open prospective `00/01/03` for V4.

GuitarSet prospective evaluation processed=false; prospective score calls=0. V168 reference-facing score calls=0.

## NEXT SAFE ACTION

1. Treat V4 as closed. Do not mine player-05 outcomes to retune V4.
2. If continuing open-corpus research, open a clearly named **V5 development phase** that explicitly reclassifies all `02/04/05` as development and preserves `00/01/03` as the untouched sole prospective test set.
3. Before mining player-05 event-level outcomes for V5, freeze a new development protocol. A robust option is player-stratified/leave-one-player-out development requiring candidate behavior to replicate across all three development players rather than relying on a single confirmation player.
4. No prospective `00/01/03` reference use until a V5 rule is completely frozen, including one-shot prospective gate and fail-closed behavior.
5. GOAT approval remains the independent primary V168 path; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
