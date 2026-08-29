# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163/V164/V165 are terminal and permanently closed. V165 produced one authoritative CPU candidate, then consumed its sole professional-reference score and failed both frozen 0.80 F1 gates. V166 is now separately preregistered and its exact numeric/implementation contract is sealed BEFORE implementation. V166 has executed no song audio, Demucs, timebase, pitch inference, candidate generation, scorer/reference, V165 candidate/score reads, or GPU work. `main`/Production remain untouched.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159–V165 generation versions closed forever; V163/V165 score opportunities closed forever.
- Never rerun/rearm/repair/retune/regenerate/re-QC/rescore a closed version.
- No professional-reference event/measure mining, score-informed retune, threshold sweep, variant selection, or human correction.
- V166 does **not** claim score blindness because V165 aggregate score was observed before V166 preregistration. V166 design/numerics are explicitly quarantined from V165 score/reference evidence.
- PR #22 remains open/unmerged as visibility only.

## V165 terminal generation
- Sole generation run `33223256331`, run `1`, attempt `1`, job `99021632117`; terminal commit `97c2efe6acf988a4535de1fff449194b7b2f7c2b`.
- Terminal-freeze blob `857153fdaedd3c386d5802277cf60e68ae231dc6`; `STRUCTURAL_QC_PASS`; `candidateAuthoritative=true`; `neverRearmV165=true`.
- Candidate blob `e70a444cb7778a6f56988cf8cc69dccb9c1d89ce`; SHA256 `b1ad02001724750ea82d693591a7c0b1f214820de37a590871a6d78eef63e5cb`; Guitar `1043`, Bass `405`.
- Timebase-QC blob `abd04e343aae15c6012b8fbec03ed1fe19a6ab24`; independent PASS before pitch.
- Structural-QC blob `f411e6c98b8ae33ba6f545d1b4dea12c80019a94`; SHA256 `af2f88975b9681e256c01ca14586bc4dd50d8229dc455df057b2ffb75cc2cc57`; PASS/errors `[]`.

## V165 terminal score
- Score prereg blob `c5e44f8e60da4e7d68e71f384b702149b327a840`; score identity receipt blob `0750b12cc248e177436abc973624caee461c9d29`.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional-reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Sole actual score run `33225802868`, run `1`, attempt `1`, job `99029213716`, head `236125d7bbda7fa78126a2bfa6ab56717f291fbd`; all score/self-seal steps PASS.
- Outcome `SCORE_GATE_FAIL` against frozen Guitar/Bass F1 gates `0.80`/`0.80`.
- Guitar: matched `73`, generated `1043`, reference `1393`, precision `0.06999041227229147`, recall `0.0524048815506102`, F1 `0.059934318555008206`.
- Bass: matched `103`, generated `405`, reference `547`, precision `0.254320987654321`, recall `0.1882998171846435`, F1 `0.21638655462184872`.
- Score terminal commit `37a96aff29b88dd5c7f4272c2ed503cbbad2fc7f`; score report blob `ef1ba2a1a3a55db5c52a4bf3a0b80353b6b3755a`, SHA256 `0cce7f35d6d3de4bfcabcb1df3eea07893d35be9176b9e959980f47bc6c91576`; score-terminal blob `3e9a5b3d6e3a5d11b2f719bdf8e808b7f2076164`; `neverRescoreV165=true`.
- Delayed Actions visibility caused accidental run #2 `33225842248` / job `99029324185`; it failed at the one-run identity guard and **skipped** scorer + terminal steps. Zero second score calls. Never rerun it.
- Inert restored score workflow removed at `4d9f2dddcc1b0e5b5a87d0a7667090f1143f4799` with `[skip ci]`; cleanup spawned zero Actions runs.

## V166 preregistered hypothesis — PAIRED ADJACENT TEMPLATE WINDOW
- Prereg file `debug/v166-cpu-autonomous/preregistration.json`.
- Commit `e29bfd3cea779f447b13b78a6d299c81fd220a23`; blob `ca45241b4ab4689c8ceb3a7107e158367814cc1d`; schema `dadrock.tabs.v166.preregistration.v1`; PASS.
- Design source is static architecture only: predecessor Guitar `three_frame_template` uses offsets `[-1,0,+1]` at event/onset frames.
- Sole hypothesis: append exactly one adjacent non-overlapping three-frame block `[+2,+3,+4]`, yielding fixed Guitar template evidence offsets `[-1,0,+1,+2,+3,+4]`.
- Same frozen `template_scores` harmonic/fundamental computation; each frame independently clipped to valid CQT bounds.
- Applies uniformly to Guitar template calls (main event/register evidence and Guitar recovery pitch evidence).
- No other functional/numeric changes allowed.

## V166 implementation contract — SEALED BEFORE CODE
- Contract file `debug/v166-cpu-autonomous/implementation-contract.json`.
- Commit `5313af5ca30a0cf4201ac6b24534f2821af9d444`; blob `9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7`; schema `dadrock.tabs.v166.implementation-contract.v1`; PASS.
- Frozen predecessor pins include V165 event logic `b296b3c322c13f8963f253f9b0666db66766a178`, transcriber `45d595853302b077fbf4f3094e9a4922fba02435`, timebase builder `62d67becb768e1e5e3e8de1cd3b121eb863b2a18`, timebase QC `3c11a490d24d06647894ee8c3700d9ff7decd993`, structural QC `36b4738cc7c00fa32aa684b3d395a67d5294a61d`.
- Frozen template numerics: offsets `[-1,0,1,2,3,4]`, frame count `6`, harmonics `[1,2,3,4,5]`, weights `[1.0,0.5,0.3333333333,0.25,0.2]`, fundamental coefficient `0.75`, BPO `36`, static tolerance rel/abs `1e-12`.
- All Basic Pitch settings, Guitar admission/register thresholds and weights, onset/local-evidence logic, segmentation/recovery thresholds, Bass logic, timebase/subdivision/grid logic, and caps remain frozen.
- Canonical V166 schemas remain mechanically versioned `local-evidence` schemas.
- Implementation plan: mechanically version-isolate V165; monkey-patch only adapted module global `three_frame_template` to the exact paired-window function; static synthetic fixture proves offsets, clipping, constant-time equivalence and no runtime/reference access.

## Current counters
- V165 generation executions `1` consumed; actual score executions `1` consumed; duplicate score execution count `0`.
- V166 implementation files `0` at contract seal.
- V166 static runs `0`; song audio reads `0`; Demucs `0`; timebase builds/QC `0`; pitch inference `0`; candidates `0`; reference/scorer reads `0`; V165 candidate/score reads `0`; GPU/CUDA/Modal `0`.
- `main`/Production modifications `0`.

## Hard boundary — NEXT
1. Never reopen V163/V164/V165.
2. Implement V166 exactly to prereg blob `ca45241...` and contract blob `9ab505ee...`; no design/numeric expansion.
3. During implementation/static validation: no song audio, Demucs, pitch inference, professional reference/scorer, V165 candidate/score runtime artifacts, or GPU.
4. First create V166 event-logic isolation, paired-window transcriber, mandatory song-blind static fixture, mechanically isolated timebase/QC/structural-QC, JSON fixture, and negative runtime guard.
5. Static workflow must be CPU-only and synthetic/song-blind. Do not arm generation until static PASS, then separately seal pre-run identity and CPU environment.
6. No GPU/Modal/CUDA without fresh explicit authorization. Never modify/merge `main`/Production without explicit direction.
