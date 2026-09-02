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

## GuitarSet V3/V4 — terminal history

Immutable candidate artifact from original run `33581322528`: manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`; artifact ID `9828683652`; ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

V3 terminal `NO_DEVELOPMENT_SIGNAL`.

V4 discovery selected `H72-D035` on players `02/04`, but frozen one-shot player-05 confirmation failed:
- run `33584451308`, job `100105524472`;
- changed 91 pitches across 60 tracks;
- primary macro delta **-0.0701653918423375 pp**;
- primary micro delta **-0.05407451468121849 pp**;
- strict50 micro delta **-0.0540745146812327 pp**;
- 1 positive / 56 neutral / 3 negative primary-TP tracks;
- terminal `V4_PLAYER05_CONFIRMATION_FAIL`.

Confirmation report SHA256 `3feb63042c670690221901906045520f17faa01d02a461c01b805ea68867d722`; artifact ID `9829578804`; ZIP SHA256 `556d301e3466a9f6064d52ccd3e37410b492fac147e20e7833ed8bde65dff300`.

Terminal checkpoint `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_PLAYER05_CONFIRMATION_FAIL_20260902.md`, creation commit `d008ea75c945bbf050d6af0a136367d2ff730c4a`.

Never rerun/retune V4. Prospective players `00/01/03` were not opened for V4.

## V5 cross-player development — PREREGISTERED / NOT YET SCORED

New methodological boundary: all `02/04/05` are now explicitly **development** for V5. The sole untouched prospective test players remain `00/01/03` and are still sealed.

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V5_GUITARSET_CROSS_PLAYER_DEVELOPMENT_PREREGISTRATION_20260902.md`;
- creation commit `20c96e258653a8dcf65c312cf75ded44511450e6`.

Frozen 48-config, reference-blind family:
- octave-down only (`ordinaryV2Winner = baselinePitch - 12`);
- pitch floors `{72,76,79}`;
- maximum durations `{0.20,0.25,0.30,0.35}` seconds;
- common-frame consensus fixed at `1.00`;
- median-advantage thresholds `{0.05,0.10,0.15,0.20}`.

No amplitude/player/track/style/tempo/pitch-class/reference feature is allowed in the gate.

Frozen development qualification requires:
- event-count identity;
- >=5 changed pitches in each development player;
- combined primary macro and micro gains >0;
- combined strict50 micro non-regression;
- **each** of players `02/04/05` primary micro gain >0;
- each player primary macro and strict50 micro non-regression;
- within each player, negative-primary-TP track count <= positive-primary-TP track count.

Frozen deterministic selection maximizes worst-player primary micro gain, then combined primary micro, combined macro, worst-player strict50 micro, then fewest changes and lexical ID.

Frozen evaluator:
- `validation/open_corpus/evaluate_guitarset_v5_cross_player_development.py`;
- creation commit `a520c8c6c245a49c609264da9de25c5f18deab5b`;
- blob `8a38a0c812fb1979fe01ccad711d3f8e72813d26`.

Static guards:
- workflow creation commit `67a1024cb9df06ef0edcb56cd671a48254183c6e`;
- run `33584773548`, job `100106522779`: **SUCCESS / V5_CROSS_PLAYER_STATIC_PASS**;
- no real references/audio, no Basic Pitch;
- V5 development score calls=0;
- prospective score calls=0;
- V168 score calls=0.

## NEXT SAFE ACTION

1. Run exactly one V5 cross-player development score across all 177 `02/04/05` tracks using the frozen 48-config family.
2. Before references, reverify original candidate artifact identity, manifest hash and all 177 candidate hashes; no audio/Basic Pitch/candidate regeneration.
3. Extract only development JAMS `02/04/05`; assert no `00/01/03` JAMS in the workspace.
4. If no config qualifies, close this V5 family and keep prospective players sealed.
5. If a config qualifies, immediately checkpoint the selected config. **Do not open `00/01/03` yet**; first freeze a separate one-shot prospective evaluation contract and pass/non-regression rule.
6. GOAT remains independent V168 path.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
