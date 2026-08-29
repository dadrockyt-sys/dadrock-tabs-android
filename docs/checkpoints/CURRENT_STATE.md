# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 001 remains the best frozen candidate at Guitar 40.36% / Bass 70.60%. Global timing is corrected by the shared `-12` lattice shift; broad 8-measure timing correction and generated-only repeat completion were tested and rejected for promotion. The latest candidate-evidence probe found rich per-event audio-derived timing evidence: every admitted event stores three lattice candidates. Next boundary is a fixed global step-selection-rule sweep over those stored choices. `main`/Production remain untouched.**

## Standing V167 methodology
- Calibration only, not holdout/generalization performance.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Score/reference-guided diagnostics and parameter experiments are allowed.
- Direct/manual copying of professional-reference events into generated output is forbidden.
- Reference may grade a complete fixed rule/variant but must not choose an individual event's answer.
- Improvements must come from deterministic algorithm/code/parameter behavior.
- CPU work authorized; fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit direction.

## Closed V166 anchor
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`; Guitar 1050, Bass 402; structural QC PASS.
- V159–V166 generations closed forever.

## V167 Iteration 001 — CURRENT BEST / FROZEN
- Transform blob `9b13b65a2b4c9fd6a801afe50a0ecc153de56b3c`.
- Run `33227463521`, job `99033850831`; terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`.
- Candidate `debug/v167-single-song-calibration/iteration-001-generated.json`, blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`, SHA256 `cfe521efac40b28b3fd34268cd24d7cdc24d92926fc33815f0928942edb56911`.
- Guitar **40.36021285304953%** — 493 matched / 1050 generated / 1393 reference; gross 54.93246009005321%; pitch-content 59.43512075317232%.
- Bass **70.60063224446786%** — 335 / 402 / 547; gross 74.81559536354058%; pitch-content 75.23709167544784%.
- No MIDI or scored-cardinality change; no direct reference copy; no GPU/main changes.

## Frozen negative/weak diagnostics
- Fixed 8-measure shared phase sweep: run `33227532512`, terminal commit `2d6930a058bfd5a6ed3c622378270e14c43f87f3`, report blob `415be9b6670a0b03ad593ae008b3353d59c26c05`; every block chose additional shift 0.
- Generated-only repeat completion: run `33227633093`, terminal commit `a379a3a1c329326f2311a7db3812dcc7f048a2e6`, report blob `3a71ad10fd74805d86803f5e86c5332c54acf0ef`; Bass never beat baseline; Guitar best was only 40.9824% while adding 285 notes, so no promotion.

## V167 candidate evidence schema probe — FROZEN SUCCESS
- Probe code `validation/v167_single_song_calibration/probe_candidate_evidence_v167.py`, blob `3fafa2194ab5228f39292d110bef14592dacb909`.
- One-shot run `33227694682`, run 1, attempt 1, job `99034499031`; SUCCESS.
- Arm commit `bd7df6cea7bfe958d926bef3ca11ad54e01bd417`.
- Terminal commit `0944ca72009e087c46cb02ab3d544a211d442b90`, message `research: freeze V167 candidate evidence schema probe [skip ci]`.
- Report `debug/v167-single-song-calibration/candidate-evidence-probe.json`, blob `b15fcdf72f39ce5342c7306f0fb78c1588c80f75`.
- Probe was reference-free and candidate-read-only.

### Evidence findings
- No large top-level rejected-event pool is preserved. The main lists are `streams.combinedGuitar` 1050 and `streams.bass` 402.
- **Every admitted event stores `stepSelection.candidates` with exactly 3 audio-derived lattice candidates** plus a winner.
- Each step candidate stores absolute lattice `step`, `time`, `score`, `instrumentSupport`, `sharedSupport`, and normalization windows.
- Iteration 001 shifted final event coordinates by `-12`, but nested `stepSelection.candidates[].step` retains the pre-correction absolute lattice. Therefore any alternate selected in V167 must use `correctedAbsoluteStep = candidate.step - 12` before recomputing measure/step.
- This is confirmed by provenance fields: final `absoluteGridStep` averages ~12 lower than `nearestLatticeStep`/stored candidate steps.
- Guitar events retain rich audio evidence including `confidence`, `persistenceSupport`, `templateScore`, `templateRank`, register context, and recovery evidence. Bass events retain `combinedPitchScore`, `harmonicTemplateScore`, `medianPyinMidi`, voiced probability, state MIDI/probability, and proposal metadata.
- Metadata reports a small number of admission rejections but not the rejected event dictionaries themselves; deeper recall recovery will likely require a new instrumented CPU front-end calibration run rather than a pure frozen-candidate transform.

## NEXT boundary
1. Run a read-only fixed **global step-selection rule sweep** from immutable Iteration 001. MIDI/cardinality must remain unchanged.
2. Predeclare rules using only stored per-event audio evidence, e.g. current baseline; max candidate `score`; max `instrumentSupport`; max `sharedSupport`; max `score*instrumentSupport`; max `score*sharedSupport`; and a few fixed weighted combinations.
3. For any selected nested candidate, subtract exactly 12 from its stored absolute step, then recompute final measure/step on the 16-step lattice.
4. Score complete global rules separately for Guitar and Bass; reference may select the best whole rule per instrument but may not select per-event alternatives.
5. Freeze the complete rule sweep before applying any new candidate.
6. Promote Iteration 002 only if the gain is material and the rule is deterministic/provenance-tracked. Otherwise move to a new CPU front-end calibration run with additional instrumentation for low-Bass and Guitar polyphony near-miss pools.
