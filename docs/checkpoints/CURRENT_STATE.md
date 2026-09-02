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

P3 Guitar-TECHS bridge remains terminal `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL`; never mine it for V3. Controlled V2 P1/P2 result remains 558/558 correct when the octave ambiguity is already known.

## V3 GuitarSet provenance / split

Frozen GuitarSet v1.1.0 identities:
- `audio_mono-mic.zip` SHA256 `237cdc58353d25c3c9683f4565a0f1cf2db30a9051abca545a919f8f1296dc28`;
- `annotation.zip` SHA256 `8daa02e6417ccca1685feb44b135e95928ad7037e5032ecb326b5791856fda99`.

Exact mic/JAMS pairing: 360 tracks. Development players `02/04/05`: 180 nominal; evaluation players `00/01/03`: 180 and still sealed. Development objective excludes `04_BN3-154-E_comp`, `04_Jazz1-200-B_comp`, `02_Funk2-119-G_comp`, leaving exactly 177 tracks.

Frozen V3 code:
- trigger blob `14ddd15fc29bfe947a4e3ce12050b10f43d2435f`;
- development candidate generator blob `61068cee19132c40f3d0b15231d64ea3d428e1ca`;
- development scorer blob `19ef54155735a6ac1e65441250b47d1572ac0380`.

Frozen trigger family: consensus `{0.75,1.00}` × median advantage `{0.05,0.10,0.15,0.20}`. Qualification: event identity, >=+0.25pp primary macro gain, primary combined micro non-regression, each-player primary micro delta >=-0.10pp, strict50 combined micro non-regression; among qualifiers select fewest changed pitches first.

## V3 development candidates — authoritative

Original run `33581322528`, candidate job `100096037798`: SUCCESS.

- 177 admissible development tracks only;
- baseline events **29,245**;
- ordinary V2 proposals **10,693**;
- trigger-eligible events **10,642**;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- candidate artifact ID `9828683652`, ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

Changed pitches: `C075-M005` 5869, `C075-M010` 4012, `C075-M015` 2685, `C075-M020` 1732, `C100-M005` 4881, `C100-M010` 3546, `C100-M015` 2457, `C100-M020` 1620.

**Never regenerate these candidates for this V3 study.**

## V3 development result — TERMINAL `NO_DEVELOPMENT_SIGNAL`

After two checkpointed mechanical scorer-recovery issues (absolute-path checksum receipt, then JAMS 0.3.4 / NumPy 2.x incompatibility), the scorer-only runtime recovery changed only the runtime pin to `numpy==1.26.4` with unchanged `jams==0.3.4`.

Successful recovery:
- workflow creation commit `fea2d10cdeeae39424abd6dd5cd94792d01614ce`;
- run `33582451429`;
- job `100099402236`: **SUCCESS**;
- original artifact identity and all 177 candidate hashes reverified before references;
- exact 177 development JAMS references only; no players `00/01/03`, no anomaly files;
- Basic Pitch unavailable in scorer runtime; candidateRegenerated=false.

Frozen score report:
- `guitarset-v3-development-score.json` SHA256 `80f68643e11644d085674ddbb1771d7bd6502bcc328c94d3cc356aea1a7af057`;
- report artifact ID `9828894162`;
- artifact ZIP SHA256 `569252da6d45a38e6661a5f26feb1cbbda2c0971c54e979c30470037b2d1087b`.

Baseline on 177 development tracks / 28,115 reference events:
- primary macro F1 **80.3621313923964%**;
- primary micro F1 **76.62482566248256%**;
- strict50 micro F1 **74.51882845188284%**.

**None of the 8 frozen V3 configurations qualified.** `qualifiedConfigIds=[]`; `selectedConfig=null`; event-count identity=true.

All configurations regressed macro, primary micro and strict50 micro. Least harmful was the strictest/fewest-change `C100-M020`:
- changed pitches **1620 / 29245 = 5.539408445888186%**;
- primary macro F1 **79.36093022561383%**, delta **-1.0012011667825789pp**;
- primary micro F1 **75.09414225941423%**, delta **-1.5306834030683376pp**;
- strict50 micro delta **-1.509762900976284pp**;
- player primary micro deltas: `02` -2.5933119848810975pp, `04` -0.6761529922292766pp, `05` -1.3518628670307749pp.

Dedicated terminal checkpoint:
- `docs/checkpoints/OPEN_CORPUS_V3_GUITARSET_NO_DEVELOPMENT_SIGNAL_20260902.md`;
- creation commit `cd6e06687d3a5c8f7a0a4c4588ed78f3fd711f3a`.

### Frozen consequence

The current V3 eight-config trigger family is **closed / terminal**. Do not weaken its gate, select a least-bad configuration, or run it on GuitarSet evaluation players `00/01/03`.

GuitarSet development score calls = **1**. Prospective evaluation processed=false; prospective evaluation score calls=**0**. V168 prospective reference-facing score calls=**0**.

## NEXT SAFE ACTION

1. Keep GuitarSet evaluation players `00/01/03` sealed. Do **not** run V3 prospective evaluation.
2. If continuing the open-corpus lane, begin a distinctly named **V4 development-only hypothesis-generation phase** on already-consumed development players `02/04/05`.
3. Before any new per-event reference analysis, preregister the V4 exploratory question, allowed development data, forbidden evaluation data, and evidence outputs.
4. V4 may use development evidence iteratively, but a future prospective evaluation is allowed only after the final V4 feature logic, candidate generation, scorer, selection rule and PASS/FAIL contract are frozen first.
5. GOAT approval remains the independent primary V168 path; on approval follow the frozen GOAT intake sequence before any V168 arm.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
