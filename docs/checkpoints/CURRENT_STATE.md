# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal and consumed forever after exactly one valid professional-reference CPU score. Generation passed independent timebase QC and independent structural QC, but the frozen candidate failed the front-end score gates: combined Guitar timing-aware pitch F1 `0.09975470155355683`, Bass `0.18073485600794442`, required `0.80` each. The sole score workflow self-deleted and self-sealed at bot commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`. No rerun, rescore, retune, candidate repair, re-QC, threshold sweep, or variant selection is permitted. Next: preregister V161 successor analysis/design before using V160 score evidence to change any successor implementation. V161 must remain reference-blind: no direct professional-reference reads and no V160 candidate reuse. GPU/Modal/CUDA remain 0; main/Production remains untouched.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only. Direct reference content must never influence generation/transcription/QC/candidate repair or successor implementation.
- Frozen aggregate score evidence may inform a successor only after that successor's analysis/design boundary is preregistered.
- V159 is closed forever: no re-arm/replay/regeneration/re-QC/score.
- **V160 is closed forever:** generation and score are both consumed; no re-arm/replay/regeneration/re-QC/candidate replacement/threshold sweep/variant selection/human correction/retune/rescore.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen shared scorer/reference identities
Song: Lenny Kravitz — Are You Gonna Go My Way.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Frozen score gates: combined Guitar timing-aware pitch F1 >= `0.80`; Bass >= `0.80`; both required before role/string/fret/technique/PDF work.
- Frozen primary timing tolerance `0.50` grid steps; gross diagnostic tolerance `2.00` grid steps.

## Historical closed results
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- V159: one generation run forever; structural-QC runtime failure; score count 0 forever.
- **V160: one generation run + one score forever; structural QC PASS; score gate FAIL; consumed.**

## V160 sealed generation identities
- Preregistration blob `cc238bcbf62c5defec410def962124d5012bd506`.
- Numeric implementation contract blob `3d5ef47a998b638683c83ae08c92e45d5422f389`.
- Timebase builder blob `b5aa459381da6a5d5379ed8bdb1a07ba26467b63`.
- Timebase QC blob `a2dba655709572d5c50dd8d4ec8656fa96eb03a3`.
- Transcriber blob `864f0da266816e999cd6c2750dbceb27e870b67a`.
- Structural QC blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
- JSON-native fixture blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
- Negative runtime guard blob `e6cd45c7d8bd23a92100847f3a219c84524cbbc2`.
- Immutable pre-run receipt blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`.
- Runtime-compatible pre-run envelope blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`.
- Static preflight consumed PASS: run `33197726025`, run #1 attempt #1, job `98939034732`; never rerun.

## V160 sole generation — TERMINAL STRUCTURAL_QC_PASS / CONSUMED
- Sole generation arm commit `a66d4b23ba625ee1583aa9d6f11eb0115efb2de2`; workflow blob `35c644cb4d29341d2f7d0404b896703c7fca2da4`.
- Generation run ID `33205440520`; run #1 attempt #1; job `98965166224`; conclusion success.
- Generation terminal bot commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`; generation workflow self-deleted.
- Candidate `debug/v160-cpu-autonomous/generated.json`; Git blob `892be048486c843ae5d3268e35f84cd95b4245af`; SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`; combined Guitar 2276 events; Bass 460 events.
- Timebase-QC SHA256 `45cc89876921b99886cb126bd381e272968f8fc0c6affe672184f0ac81da8aa4`; PASS; 448 beats.
- Structural-QC Git blob `5372885dfc9e07dfa8394294deafdf32c8f5a356`; SHA256 `2bb154499a849596f9e6e098df232d69a72379aa8508544dfa748797e23c3f34`; PASS; every check true; errors `[]`.
- Generation terminal freeze blob `9690c523290955dcf0ef15074bb6746105ec0810`; `STRUCTURAL_QC_PASS`; candidateAuthoritative=true; eligibleForProfessionalReferenceScoring=true; neverRearmV160=true.
- Generation/QC direct reference reads=0; score calls=0; CUDA/GPU/Modal=0; main/Production untouched.

## V160 one-score preregistration — SEALED BEFORE REFERENCE-FACING SCORE WORK
- `debug/v160-cpu-autonomous/score-preregistration.json`; seal commit `2ee882897ebeeed6aca0a768eba36be78827b741`; Git blob `8cdc8f8d561124b7d417d5de7ea96fae5e0ec4ed`.
- Status `SEALED_BEFORE_REFERENCE_OR_SCORER_OPEN`; validation PASS.
- Candidate was frozen before scorer/reference audit reads and before the sole score execution.
- Maximum professional-reference score executions frozen at 1; no rerun/rescore/retune/candidate mutation/re-QC/threshold sweep/variant selection/human correction.

## V160 sole professional-reference CPU score — TERMINAL SCORE_GATE_FAIL / CONSUMED
- Score workflow path was `.github/workflows/v160-score.yml`; final Git blob `b05b43bdac131561da15209b0beed56b3c6ea982`.
- Sole score arm commit `9ceb142f3811b0c0d5e475fd0a9b847bac9540e6`; parent `33e6f4286557ce08ce1c6cd10576a20e828039aa`.
- Score run ID `33206424361`; run #1 attempt #1; job `98968523271`; conclusion success as a valid one-shot score execution.
- Guard PASS; frozen scorer executed exactly once; terminal score self-seal PASS.
- Score terminal bot commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`; message `research: freeze sole V160 professional-reference score FAIL [skip ci]`; direct parent is the sole score arm.
- Score workflow self-deleted and is absent after terminal freeze.
- Score report `debug/v160-cpu-autonomous/reference-score.json`; Git blob `d280a19052228f71e4520db077686dfe9ae8f9bb`; SHA256 `32476d8d6036c72cb3b29bc4e67ec7c3fd5e7dc11b9334bd04730b4fd25e5e04`.
- Score terminal receipt `debug/v160-cpu-autonomous/score-terminal-freeze.json`; Git blob `bc73cefe6653b9c398e65381256caa843182661d`; schema `dadrock.tabs.v160.professional-reference-score-terminal.v1`; status TERMINAL; outcome `SCORE_GATE_FAIL`.
- `scoreExecutionCount=1`; `scoreOpportunityConsumed=true`; `candidateConsumed=true`; `neverRerunOrRescoreV160=true`; eligibleForRoleStringFretTechniquePdfPhase=false.
- Terminal score safety: candidateModified=false; candidateRegenerated=false; candidateReQc=false; thresholdSweep=false; variantSelection=false; humanCorrection=false; postScoreRetune=false; professionalReferenceUsedForScoringOnly=true; referenceFacingScoreCalls=1; GPU/CUDA/Modal=false; main/Production=false.

## V160 frozen score evidence
### Combined Guitar
- Primary timing-aware pitch: matched `183` / generated `2276` / reference `1393`; precision `0.0804042179261863`; recall `0.13137114142139267`; **F1 `0.09975470155355683`**.
- Gross ±2-step timing-aware pitch: matched `391`; precision `0.171792618629174`; recall `0.28068916008614503`; F1 `0.2131370945761788`.
- Measure+pitch content diagnostic (timing ignored within measure): matched `712`; precision `0.31282952548330406`; recall `0.511127063890883`; F1 `0.3881166530389752`.
- Generated count is substantially above reference count (`2276` vs `1393`), indicating severe Guitar over-generation in addition to pitch/timing disagreement.

### Bass
- Primary timing-aware pitch: matched `91` / generated `460` / reference `547`; precision `0.19782608695652174`; recall `0.1663619744058501`; **F1 `0.18073485600794442`**.
- Gross ±2-step timing-aware pitch: matched `160`; precision `0.34782608695652173`; recall `0.29250457038391225`; F1 `0.31777557100297915`.
- Measure+pitch content diagnostic: matched `258`; precision `0.5608695652173913`; recall `0.4716636197440585`; F1 `0.5124131082423039`.
- Bass count is somewhat below reference (`460` vs `547`), but measure-level pitch content is materially stronger than exact timing-aware performance, suggesting timing/onset placement plus missing notes are dominant successor targets.

### Frozen interpretation limits
- These are aggregate scorer outputs only. They may inform V161 after V161's analysis/design boundary is preregistered.
- Do not inspect the professional reference again for successor generation design.
- Do not reuse or mine the V160 candidate event-by-event to tune V161 to this song.
- Do not change V160 in response to these metrics.

## Current hard boundary
- V159 closed forever.
- **V160 generation count=1 and score count=1; both opportunities consumed forever.**
- No V160 rerun, replay, repair, re-QC, score, rescore, or post-score tuning.
- V160 did not meet the front-end gate and cannot proceed to role/string/fret/technique/PDF work.
- Before any V161 implementation or successor-specific tuning, seal a V161 analysis/design preregistration that defines allowed evidence and forbidden leakage.
- V161 generation must be reference-blind and must not consume V160 candidate events or direct professional-reference content.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Create `debug/v161-cpu-autonomous/preregistration.json` **before V161 implementation**, freezing the allowed successor evidence as aggregate V154/V157/V158/V160 score summaries + frozen V159/V160 structural/runtime diagnoses + reference-blind implementation source identities; explicitly forbid direct professional-reference reads and event-level mining/reuse of V160 candidate.
3. Freeze V161 hypotheses before implementation. At minimum, address: Guitar over-generation/precision collapse; Bass onset/timing alignment and recall; pitch-confidence/event-selection calibration without reference-guided sweeps; separation/source attribution; and a song-blind validation plan.
4. Create a numeric V161 implementation contract before code changes. Any thresholds/algorithms must be fixed from reference-blind reasoning and song-blind fixtures, not selected by rescoring V160.
5. Implement V161 only after those seals. Use CPU-only unless fresh explicit GPU authorization is obtained.
6. V161 must get its own static/reference-blind preflight and pre-run identity seal before any song processing.
7. V161 candidate may be generated only once under its preregistered boundary, structurally QC'd independently, then—only if authoritative—scored exactly once after a separate score preregistration.
8. Preserve `CURRENT_STATE.md` frequently while working.
