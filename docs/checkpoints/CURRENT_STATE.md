# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 remains the explicitly scorer/reference-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 004 is the frozen current best: Guitar 42.617717478052675% F1 and Bass 80.45325779036827% F1. The post-I004 aggregate/reference-blind Guitar diagnosis is terminal/frozen. A small state-split Guitar family is now fully preregistered in code, but no state-split candidates have been generated or scored yet. The family fixes the high-value Basic-Pitch-active/max-active branch and varies only the inactive branch. A no-score q1.00/noharm reproduction control must normalize exactly to I004 before any scorer/reference read. The scorer is constrained to exactly 5 Guitar score calls total (I004 + four new rules), 0 Bass score calls, and 0 reproduction-control score calls. No I005 exists. `main`/Production remain untouched; no GPU/CUDA/Modal work is authorized or used.**

## Current execution checkpoint — STATE-SPLIT CODE STAGED / SWEEP NOT ARMED
- Frozen I004 terminal self-seal `edb1cbca37ffcac2cf1020e2af05120e2f3a5353`.
- I004 candidate `debug/v167-single-song-calibration/iteration-004-generated.json`: blob `8dd85049a65f00541f7874ff99511b081a0b5ff2`, SHA256 `728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc`.
- I004 promotion proof blob `d055f3f0a1cbf91cd4d6ac4cb26ee654b599925d`, SHA256 `b35c7bff5583786a8e23e736c56898505306e7c6c69106bf565aa11e0e0ae753`; receipt blob `a880a1e29dab29cc0e77f1aa569dd123e1092457`, status `ITERATION_004_FROZEN`.
- I004 Guitar 1113 = all 1050 rich I003 Guitar events + 63 frozen contextual additions. I004 Bass is exactly I003, 512 events.
- Frozen post-I004 diagnosis: analysis blob `d7f698bf9960814dea43c2f1cbd93f754c07dc43`, SHA256 `99396cd675fc107ac37142aa3afa7805d73ccc02edd875ac1059a043ee8f0f07`; receipt blob `c1f8640b1f728e219430789d96f6d6722572e1a7`; terminal `623a4c3bb8f39aa580a03fd47a11a8581011ea73`.
- State-split generator `validation/v167_single_song_calibration/build_state_split_guitar_variants_v167.py`: commit `db7385813f3782cb4ee826f41832d70ccbef2bc0`, blob `6b480d43744a5c67c02510d55162581d896afee4`.
- State-split scorer `validation/v167_single_song_calibration/score_state_split_guitar_variants_v167.py`: commit `14687ad08f21b5c6b1759e7e494760105d7b8285`, blob `7e5068ce607d7f817429d39ea363840c7ba8d51e`.
- Generator is reference-blind and accepts only frozen I003, frozen I004, frozen evidence pool, frozen V166 timebase, output directory, and manifest path. It has no reference/scorer input.
- Scorer verifies I004 SHA, manifest/schema/policy, every generated candidate hash, reproduction-control exact normalized Guitar/Bass equality to I004, and Bass identity for all four new variants **before** importing scorer code or opening the professional reference.
- Reproduction control is explicitly unscored. Bass is never scored. The only reference-facing calls allowed by the staged scorer are one I004 Guitar baseline + four new Guitar whole variants.
- Winner selection is preregistered: max Guitar F1, then max precision, fewer total additions versus I003, then lexicographic rule id. No automatic I005 promotion.
- No state-split workflow is armed yet; no new state-split manifest/report/receipt exists; zero new reference-facing score calls have occurred in this phase.

## Frozen I004 current-best metrics
### Guitar — `gctx-o50-q100-allow-noharm`
- F1 **42.617717478052675%**; precision **47.97843665768194%**; recall **38.334529791816224%**.
- 534 matched / 1113 generated / 1393 reference; FP 579; FN 859.
- Delta vs I003: F1 **+0.702040032289275pp**; precision **-0.7834681042228231pp**; recall **+1.5793251974156486pp**; +22 matches; +41 FP; -22 FN.
- Frozen config: rank >=0.975; activity >=0.05; onset >=0.50; candidate/max-active template score >=1.00; `allow_active`; reject nearest different active intervals 12/19/24; active context required; inherited `fundamentalPresent`; top-1/site; cap 6.

### Bass — closed / exactly I003
- F1 **80.45325779036827%**; precision **83.203125%**; recall **77.87934186471663%**.
- 426 matched / 512 generated / 547 reference; FP 86; FN 121.

## Frozen post-I004 diagnosis — terminal evidence
### Harmonic suppression
- `exclude_harmonic_octave` vs `none`, fixed onset/ratio/active-state: **12/12 higher F1**.
- Mean: **+0.33091040828484897pp F1**, **+1.0527597777533495pp precision**, **-0.13161043311797302pp recall**, **-28.583 additions**, **-26.75 FP**, only **-1.833 matches**.
- `chord_interval` vs `none`: 9/12 higher F1, mean +0.1992187851689651pp F1 and +1.3185304874835773pp precision, but -7 matches / -0.5025125628140712pp recall on average.

### Ratio boundary
- Ratio `1.00` vs `0.75`: **12/12 higher F1**; mean +0.21439806530977137pp F1, +0.6033166465310075pp precision, only -0.0358937544867192pp recall / -0.5 matches, while removing 15.25 additions / 14.75 FP.
- Positive rules by ratio: 0.75 = 4; 1.00 = 6; 1.25 = 0.
- Ratio `1.25` vs `1.00`: mean -0.12922580604163061pp F1, -0.5623354869586016pp recall, -7.833 matches despite +0.5849634748314879pp precision.
- Structural reason: a Basic-Pitch-active candidate cannot exceed the max-active score ratio 1.00; ratio >=1.00 retains max-active ties, while 1.25 necessarily removes the active branch.

### Active-state mechanism
- `allow_active` vs `inactive_only`: 12/18 higher F1, 6 ties, 0 lower.
- Mean +0.45000989139467595pp F1, +0.7418042593921987pp recall, +10.333 matches; precision nearly neutral at -0.028885316185440275pp.
- All 10 positive contextual rules are `allow_active`; 0/18 `inactive_only` rules beat I003.
- Frozen I004 winner additions: 46 Basic-Pitch-active / 17 inactive. No individual event is labeled a true positive/re-attack by reference.

### Addition-count mechanism
- Across 36 rules: additions vs precision delta `-0.8666120193973829`; additions vs FP `+0.9839527233419079`; additions vs recall `+0.8598359824170556`; additions vs matches `+0.8598359824170553`; additions vs F1 only `+0.17557607845070156`.
- Remaining hypothesis: preserve active/max-active additions while applying stronger precision control to inactive proposals.

## Preregistered state-split family — FROZEN IN CODE BEFORE SCORING
Common fixed structure:
- Generate from immutable I003 + frozen evidence/timebase, not by mutating I004.
- rank >=0.975; activity >=0.05; onset >=0.50; Basic-Pitch active context required; inherited `fundamentalPresent`; top-1/site; parent-aware new `(step,midi)` dedupe; cap 6; frozen nearest-subdivision then `-12` timing.
- Active branch fixed: Basic-Pitch-active candidate, ratio >=1.00, `exclude_harmonic_octave` rejecting {12,19,24}.
- Inactive branch is the only experimental dimension.

No-score reproduction control:
- `gss-repro-q100-noharm`: inactive ratio >=1.00 + `exclude_harmonic_octave`.
- Must normalize exactly to frozen I004 Guitar and Bass before manifest generation can complete; score calls = 0.

Four genuinely new whole rules:
1. `gss-active-only`: inactive branch off.
2. `gss-inactive-q125-noharm`: inactive ratio >=1.25 + `exclude_harmonic_octave`.
3. `gss-inactive-q100-chord`: inactive ratio >=1.00 + `chord_interval` {3,4,5,7,8,9,10}.
4. `gss-inactive-q125-chord`: inactive ratio >=1.25 + `chord_interval`.

Scoring boundary:
- Freeze all five generated candidate files + SHA256 manifest before scorer/reference read.
- Score I004 Guitar baseline + four new Guitar rules only = **5 Guitar score calls**.
- **0 Bass score calls**; Bass inherited exactly from I004/I003.
- **0 reproduction-control score calls**.
- Whole-rule selection only; no event-level reference choices; no post-score mutation/retuning; no automatic I005.

## Immutable source/evidence boundary
- I003 `debug/v167-single-song-calibration/iteration-003-generated.json`: blob `758f8762632e916306aed9b036a6483af9431dc0`, SHA256 `f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115`.
- Evidence pool blob `aa7da3a55344b1418a291f30fab9ca55858fc094`, SHA256 `1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673`.
- Frozen V166 timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`.
- Base recovery builder blob `24413d321f64bbfcce48812ceb85b4593dcfa80c`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.

## Standing V167 methodology
- Calibration only; never present V167 scores as holdout/generalization performance.
- Reference/scorer may grade complete predeclared whole variants only. No per-event reference choices or direct reference-event copying.
- I004 remains immutable during this family. If a new state-split rule beats I004, freeze the sweep first and require a separate no-rescore deterministic I005 promotion boundary.
- Bass is closed and must stay exactly I004/I003 for every Guitar variant.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.

## NEXT boundary — arm one-shot state-split sweep
1. Re-read exact branch head/checkpoint and staged generator/scorer blobs.
2. Create one self-removing CPU-only workflow from the exact checkpoint parent.
3. Pre-reference step: generate all five state-split candidate files and permanent manifest; require reproduction control exact I004 normalized equality; verify every SHA and Bass identity; then freeze candidate files against mutation.
4. Only after all pre-reference assertions pass, open the frozen scorer/reference and score exactly I004 Guitar + four new Guitar variants. Do not score Bass or reproduction control.
5. Freeze `state-split-guitar-sweep-manifest.json`, `state-split-guitar-sweep.json`, and receipt; self-remove the workflow.
6. If no new rule beats I004, close this family and keep I004 current best. If one beats I004, freeze winner/report and open a separate no-rescore I005 promotion boundary; do not create I005 automatically.
7. CPU only; no GPU/CUDA/Modal. Never modify `main` or Production.
