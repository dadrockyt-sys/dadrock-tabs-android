# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using consumed V5 professional reference as calibration data; preserve V5 history; never touch main/Production during calibration.**

## Boundaries
- Terminal V5 stays immutable on `v143-contextual-prune-lobo`; V144 only for new calibration work.
- `Are You Gonna Go My Way` professional reference is consumed calibration data, not unseen holdout. Final independent proof requires a different unseen professional song/reference.
- Do not modify/merge `main` or Production.
- Scorer + Modal/L4 archive: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`. Preserve scorer/freeze/fidelity assets, branch `v143-github-modal-smoke`, workflow blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, integration L4 probe blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`.

## V6 immutable calibration baseline — VERIFIED
- V6 stream `debug/v144-rhythm-calibration/v6-attack-gate/v6-render-stream.json`; SHA256 **`c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`**.
- Generation run `32922227911` SUCCESS: 1149 events / 839 onsets; removed 60 events / 52 attacks using only `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`; no timing/pitch/voicing rewrite, no reference read, no Modal/L4, no Production.
- Frozen calibration score run `32922358891` SUCCESS; report blob `6f336e2e1918c10ba86a406231ce1d6a9e34deef`; `predictionVerified=true`.
- V6 metrics: onset F1 `0.48682385575589454`; exact-event `0.04486873508353222`; pitch `0.6042959427207636`; pitch-class `0.8085918854415275`; measure+pitch `0.28544152744630075`; measure+pitch-class `0.4715990453460621`; position-content `0.469689737470167`.
- Every overall swept metric improved vs terminal V5. Keep V6 immutable.

## V6 pitch opportunity — candidate pool is useful but badly ranked
- Opportunity diagnostic run `32922569934` SUCCESS; report blob `8b95f34dd21121a3d81f1a34682e06920f0d8d5f`.
- Shared V6/reference exact onsets: 351. Current V6 primary exact hit: 41.
- Exact reference MIDI exists somewhere in original V2 candidate pool at **162** shared onsets; correct reference pitch class exists at **278**.
- Of 310 wrong primaries: **121 exact-selection opportunities**, **116 register-only opportunities**, **73 no-candidate-pitch-class misses**.
- Correct exact candidates are usually deeply misranked by current source evidence: median source-score rank 4, mean 5.10, p75 7, p90 11.

## V6 primary context sweep — COMPLETE, NEGATIVE
- Full sweep script `analyzer/v144_v6_primary_context_sweep.py` commit `d9ec3317d42577528bbb4a30cc98190e5d815cb6`; workflow commit `4a12b809872e058b2f3130eb9c90dc481cfbe215`.
- Trigger `e502af163de099b6824658fe7c58d6bee7ff5916`; run **`32922808616` = SUCCESS**.
- Full report `debug/v144-rhythm-calibration/v6-attack-gate/v6-primary-context-sweep.json`; blob `c5875f8e3f0ee70816ed6c986b269fb3dc259820`.
- Compact summarizer `analyzer/v144_summarize_primary_context_sweep.py` commit `c7d90e227287b35d6110b3417337060119bbebbe`; workflow commit `2b5d0d1ae2ed17bc14a878ba451531a627eb2985`; trigger `c13d66c3612107eee8d5f0f857c9614fe5c4adcc`; run **`32923006289` = SUCCESS**.
- Compact summary `debug/v144-rhythm-calibration/v6-attack-gate/v6-primary-context-summary.json`; blob **`f9ec0d3547985b462456ea20128015882cddbab2`**.
- All **47** source-only policies were included. Families: current/top-score, local-neighbor continuity, time-weighted dynamic programming, repeated-measure/same-step consensus.
- **Maximum robust improved metric count = 1. Multi-robust policy count = 0. Positive primary-exact-hit policy count = 0. Promotable policy count = 0.**
- Zero-regression policy count = 1, and that one policy is simply `v6-current-primary` (unchanged baseline).
- Across the 46 non-baseline alternatives, exact-event regressed in 46, pitch-content regressed in 46, measure+pitch regressed in 46. Measure+pitch-class regressed in 31; pitch-class content regressed in 25.
- Only pitch-class content ever improved robustly (14 policies). No policy robustly improved exact-event, pitch-content, measure+pitch, or measure+pitch-class.
- Best local-neighbor policy `local-neighbor-gap4.0-lambda0.20` improved pitch-class F1 `+0.00873` but reduced primary exact hits `41 -> 34` and materially regressed exact pitch and measure+pitch.
- Best DP policy similarly improved only pitch class while reducing primary exact hits to 30 and strongly regressing exact-pitch metrics.
- Best repeat-consensus policy reduced primary exact hits to 37 and regressed exact pitch/content.
- Raw top-source-score reduced exact-primary hits to 35 and regressed all five pitch metrics.
- **Decision: do not generate V7 from these CPU context/continuity rules.** The recoverable candidate pool cannot currently be reliably selected using the correlated V2 source views and these structural priors.

## L4 is now justified — but only as a targeted separation experiment
- The reason to use preserved Modal/L4 is now specific, not exploratory:
  1. **73 shared attacks have no correct reference pitch class anywhere in the current V2 candidate pool** — selection logic cannot solve them.
  2. At another 237 wrong-primary shared attacks, correct MIDI/pitch-class alternatives often exist but current paired-view source scores rank them poorly; naive continuity/repetition makes selection worse.
  3. Existing paired views appear too correlated to provide a useful discrimination signal.
- Goal for L4 is therefore **not** to generate V7 directly. First create genuinely different rhythm-guitar separation views and measure whether they improve candidate coverage and candidate ranking at frozen V6 attacks.

## Next exact actions
1. Re-read `docs/testing/SCORER_MODAL_L4_ARCHIVE.md` and the preserved L4 workflow/probe implementation.
2. Design a report-only targeted L4 calibration experiment pinned to frozen V6 and exact source/audio identities. No V7 output.
3. Primary success tests should include: reduce the 73 no-pitch-class candidate misses; increase exact/reference pitch candidate coverage; improve correct-candidate rank/discrimination vs existing V2 evidence; require similar direction on odd/even internal splits.
4. Only if L4 separation creates materially better source evidence should a later V7 policy/generator be considered.
5. Final legitimate validation still requires a different unseen professional song/reference.
