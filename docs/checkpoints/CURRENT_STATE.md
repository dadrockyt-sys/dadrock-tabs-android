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

## GuitarSet immutable candidate source

Original V3 candidate artifact remains the only frozen prediction/evidence source used by V3/V4/V5:

- original run `33581322528`;
- manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`;
- ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

Prospective GuitarSet players `00/01/03` remain sealed and have never been opened for V4 or V5.

## GuitarSet V3/V4 — terminal history

V3 terminal `NO_DEVELOPMENT_SIGNAL`.

V4 discovery selected `H72-D035` on players `02/04`, but frozen one-shot player-05 confirmation failed:

- run `33584451308`, job `100105524472`;
- 91 changed pitches across 60 tracks;
- primary macro **-0.0701653918423375 pp**;
- primary micro **-0.05407451468121849 pp**;
- strict50 micro **-0.0540745146812327 pp**;
- 1 positive / 56 neutral / 3 negative primary-TP tracks;
- terminal `V4_PLAYER05_CONFIRMATION_FAIL`.

Confirmation report SHA256 `3feb63042c670690221901906045520f17faa01d02a461c01b805ea68867d722`; artifact ID `9829578804`; ZIP SHA256 `556d301e3466a9f6064d52ccd3e37410b492fac147e20e7833ed8bde65dff300`.

Never rerun/retune V4.

## GuitarSet V5 cross-player development — TERMINAL `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`

All `02/04/05` were explicitly development for V5; `00/01/03` stayed sealed.

Frozen family: 48 reference-blind octave-down configs over pitch floor `{72,76,79}`, max duration `{0.20,0.25,0.30,0.35}`, consensus `1.00`, median advantage `{0.05,0.10,0.15,0.20}`.

Run `33584851641`, job `100106765017`: **SUCCESS**.

- 177 development tracks (`02=59`, `04=58`, `05=60`);
- 28,115 reference events;
- baseline primary macro F1 **80.3621313923964%**;
- baseline primary micro F1 **76.62482566248256%**;
- 48 configs scored;
- **0 configs qualified**;
- selected config = `null`;
- status `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`.

Result report SHA256 `445a79dba3992c0989f244046eca4d0fc855c3aff8d6f2e043054f3a04c87dda`; artifact ID `9829749729`; ZIP SHA256 `018a9bdcce7cbd2b58e6f2dce13a168c335d69b6649d34fa7c299aeb1e9326c2`.

Descriptive near-signal only: `P79-D035-M005` had combined primary micro **+0.020921 pp** and macro **+0.022795 pp**, but player `02` changed only 2 pitches and had exactly `0.000000 pp` primary-micro gain. It therefore failed the frozen >=5-changes/player and strictly-positive-every-player requirements. This does not authorize retuning.

Terminal result checkpoint `docs/checkpoints/OPEN_CORPUS_V5_GUITARSET_CROSS_PLAYER_DEVELOPMENT_RESULT_20260902.md`, creation commit `a338fbfcf51c871608af83fc470e09dd9b41c7ca`.

V5 development score calls = **1 / terminal for this family**. V5 prospective evaluation processed=false; prospective score calls=0. Never rerun or retune this V5 family.

## NEXT SAFE ACTION

1. Before any hypothetical V6, freeze a deliberate GuitarSet development stop/hold boundary to prevent repeated threshold mining on the same `02/04/05` references.
2. Keep prospective players `00/01/03` sealed; do not use them merely because V5 failed.
3. Only reopen GuitarSet development if there is a genuinely new, independently motivated, preregistered hypothesis that is not a threshold rescue derived from V5 outcomes.
4. GOAT approval remains the independent primary V168 path; on approval follow the already-frozen GOAT admission and deterministic selection sequence before any candidate/scorer arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
