# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is awaiting explicit owner approval/denial.
- No restricted GOAT bytes admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT selection contract and promotion gate unchanged.
- GOAT pre-access static run `33569762190`, job `100060930936`: SUCCESS.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate. Dedicated checkpoint commit `bfd8b2e1064c2025c2edc142589fbbafa0ef464b`.

## Open-corpus lane — V168 isolated

Frozen V2 evaluator blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`; helper blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`. Controlled Guitar-TECHS P1/P2 V2 result: **558/558 = 100%**; result checkpoint commit `38df953a637c12359a844b239bce08897c710c32`.

P3 run `33578675945` is terminal scientific **`REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`**: event count 4693 preserved, 1121 changed pitches = 23.88663967611336%; primary macro **60.576880733206515% -> 51.95250763325269%**, delta **-8.624373099953829pp**. Never mine P3 per-event outcomes for V3. Frozen aggregate lesson only: V2 needs a conservative trigger.

## V3 GuitarSet provenance — PASS, prospective evaluation sealed

GuitarSet v1.1.0 metadata-only verification run `33579938898`, job `100091870033`: SUCCESS.
- `audio_mono-mic.zip`: SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`.
- `annotation.zip`: SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.
- exact mic/JAMS pairing: 360 tracks, 60/player.
- development players `02/04/05`: 180 nominal; sealed evaluation players `00/01/03`: 180.
- excluded development anomalies: `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`.

V3 trigger/scorer preregistration and static guards remain frozen. Trigger family: consensus `{0.75,1.00}` × median advantage `{0.05,0.10,0.15,0.20}`. Candidate qualification: event identity, >=+0.25pp primary macro gain, primary combined micro non-regression, each-player primary micro delta >=-0.10pp, strict50 combined micro non-regression; among qualifiers select fewest changed pitches first.

Frozen code:
- V3 trigger blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`;
- development candidate generator blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`;
- development scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`.

Static guard run `33581122972`, job `100095439483`: SUCCESS.

## V3 development run — CANDIDATES FROZEN; SCORER RECOVERY REQUIRED

Original workflow head `f494e5b2f586ec335b16dcabce687e63bb1f88fb`, run `33581322528`.

### Job A — SUCCESS / authoritative frozen candidates

Job `100096037798` completed SUCCESS using CPU/TFLite only.

Exactly **177** preregistered development tracks were processed (`02`=59, `04`=58, `05`=60); evaluation players `00/01/03` and excluded anomalies were absent.

Frozen candidate summary:
- baseline events: **29,245**;
- ordinary V2 proposal events: **10,693**;
- trigger-eligible events: **10,642**;
- changed pitches: `C075-M005` 5869, `C075-M010` 4012, `C075-M015` 2685, `C075-M020` 1732, `C100-M005` 4881, `C100-M010` 3546, `C100-M015` 2457, `C100-M020` 1620;
- candidate freeze manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`, name `guitarset-v3-development-frozen-candidates`, ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

The candidate artifact is authoritative. **Do not rerun candidate generation.** At freeze: referenceRead=false; development JAMS note events=0; prospective evaluation processed=false; prospective evaluation score calls=0; V168 score calls=0.

### Job B — MECHANICAL PRE-REFERENCE FAILURE

Job `100097954531` failed before any reference download or scoring. Candidate artifact download and digest verification succeeded; the failure was `sha256sum -c candidate-manifest-sha256.txt` because that receipt contains Job A's absolute temporary path, which does not exist in Job B.

This is a path-serialization error, **not a scientific failure and not a candidate hash mismatch**. JAMS reference download, parsing and scoring were skipped. No development classification exists yet.

Dedicated recovery checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_SCORER_PATH_RECOVERY_20260902.md`
- creation commit `63de07c41db5322b5e0330339552f14dfc677c78`.

## NEXT SAFE ACTION

1. Add a scorer-only recovery workflow; never rerun Job A.
2. Bind original run `33581322528`, artifact ID `9828683652`, artifact ZIP digest `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`, manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`, and frozen scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`.
3. Before any reference download, verify the local manifest directly plus all 177 per-file hashes, no audio/JAMS/ZIP, no evaluation candidates, and no Basic Pitch runtime.
4. Only after those checks pass, download/verify `annotation.zip`, extract only the 177 development JAMS files, score unchanged candidates with the unchanged scorer and selection rule, then checkpoint the resulting `V3_DEVELOPMENT_TRIGGER_SELECTED` or `NO_DEVELOPMENT_SIGNAL` status.
5. Players `00/01/03` remain sealed until development classification and any required final prospective-evaluation preregistration are frozen.

GOAT approval remains independent; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
