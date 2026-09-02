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

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate.

P3 Guitar-TECHS reference-blind octave bridge remains terminal scientific `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`; never mine P3 per-event outcomes for V3. Frozen aggregate lesson only: V2 needs a conservative intervention trigger.

## V3 GuitarSet — provenance frozen, prospective evaluation sealed

GuitarSet v1.1.0 archive identities:
- `audio_mono-mic.zip` SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`;
- `annotation.zip` SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.

Exact mic/JAMS pairing: 360 tracks. Development players `02/04/05`: 180 nominal; evaluation players `00/01/03`: 180 and still sealed. Development objective excludes `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`, leaving exactly 177 tracks.

Frozen V3 code:
- trigger blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`;
- development candidate generator blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`;
- development scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`.

Frozen trigger family: consensus `{0.75,1.00}` × median advantage `{0.05,0.10,0.15,0.20}`. Qualification remains event identity, >=+0.25pp primary macro gain, primary combined micro non-regression, each-player primary micro delta >=-0.10pp, strict50 combined micro non-regression; among qualifiers select fewest changed pitches first.

## V3 development candidates — FROZEN / AUTHORITATIVE

Original run `33581322528`, Job A `100096037798`: SUCCESS.

Exactly 177 admissible development microphone tracks processed on CPU/TFLite only. Frozen candidate summary:
- baseline events: **29,245**;
- ordinary V2 proposal events: **10,693**;
- trigger-eligible events: **10,642**;
- changed pitches: `C075-M005` 5869, `C075-M010` 4012, `C075-M015` 2685, `C075-M020` 1732, `C100-M005` 4881, `C100-M010` 3546, `C100-M015` 2457, `C100-M020` 1620;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`, ZIP digest `sha256:1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

**Never regenerate these candidates for this development study.**

## V3 scorer recovery status — scientific result still unobserved

### Original scorer job

Run `33581322528`, Job B `100097954531`: mechanical pre-reference failure because `candidate-manifest-sha256.txt` stored Job A's absolute temporary path. No JAMS reference download or scoring occurred.

Recovery checkpoint commit `63de07c41db5322b5e0330339552f14dfc677c78`.

### Scorer path recovery

Recovery workflow commit `b5577db4bb9f929d6307b303f78188adf14dd730`; run `33582237435`, job `100098746109`.

Before references it successfully:
- bound original run/head/artifact ID/name/digest;
- downloaded the original artifact only;
- directly verified manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- rehashed all 177 candidate JSONs successfully;
- proved no WAV/JAMS/ZIP in the candidate artifact, no evaluation candidates, no Basic Pitch runtime, and candidateRegenerated=false.

It then verified `annotation.zip` and extracted exactly the same 177 development JAMS files (`02`=59, `04`=58, `05`=60), with no `00/01/03` and no excluded anomalies.

Scoring failed mechanically on the first lazy `import jams`: `jams==0.3.4` pulled `numpy==2.2.6`, but JAMS 0.3.4 uses `np.float_`, removed in NumPy 2.x. Failure occurred before `jams.load` completed and before any note event was interpreted.

Therefore now:
- development reference JAMS files were mechanically extracted in the failed recovery run;
- development JAMS note events interpreted/read by scorer: **0**;
- completed development score calls: **0**;
- baseline/config metrics: **none**;
- scientific V3 development status: **NOT YET OBSERVED**;
- prospective evaluation processed=false; prospective evaluation score calls=0;
- V168 prospective reference-facing score calls=0.

Dedicated runtime checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_DEVELOPMENT_JAMS_NUMPY_RUNTIME_RECOVERY_20260902.md`
- creation commit `b8933a36b6cea21e00c8c247f906b7c7e5ed5c58`.

## NEXT SAFE ACTION

1. Make exactly one mechanical recovery change: pin `numpy==1.26.4` with unchanged `jams==0.3.4` in the scorer-only recovery workflow. NumPy 1.26.4 retains `np.float_` and was already used in the V3 static environment.
2. Do not change scorer code, trigger, candidates, thresholds, matching, split, anomaly exclusions, or selection rule.
3. Reuse and reverify the original frozen candidate artifact and all 177 per-file hashes before references.
4. Process only the same 177 development JAMS files; no evaluation players.
5. If scoring completes, immediately checkpoint the frozen scientific classification (`V3_DEVELOPMENT_TRIGGER_SELECTED` or `NO_DEVELOPMENT_SIGNAL`) before any prospective-evaluation work.
6. If another mechanical runtime failure occurs before metrics are produced, fail closed and checkpoint it before any correction.

GOAT approval remains independent; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
