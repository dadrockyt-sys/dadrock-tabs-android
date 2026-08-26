# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using consumed V5 professional reference as calibration data; preserve V5 history; never touch main/Production during calibration.**

## Boundaries
- Terminal V5 stays immutable on `v143-contextual-prune-lobo`; V144 only for new calibration work.
- `Are You Gonna Go My Way` professional reference is consumed calibration data, not unseen holdout. Final independent proof requires a different unseen professional song/reference.
- Do not modify/merge `main` or Production.
- Scorer + Modal/L4 archive: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`. Preserve scorer/freeze/fidelity assets, branch `v143-github-modal-smoke`, workflow blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, integration L4 probe blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`. Do not run L4 without a specific justified hypothesis.

## Terminal V5
- Archive `docs/checkpoints/V5_TERMINAL_RECORD.md`; result commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`; run `32919666736`.
- Frozen stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- 1209 events / 891 onsets / 113 measures vs calibration reference 946 notes / 603 playable onsets.
- PDF fidelity `1.0`; terminal professional pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.

## V6 source-only generation — COMPLETE
- Conservative attack gate: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`; no timing/pitch/voicing rewrite.
- Generator `analyzer/v144_generate_v6_attack_gate.py` commit `7ba6cc7e59b7882fa99350f612e8ac5742f0286d`; workflow commit `82d8115f0bbc3cf8fbb049052419ff14c902ad00`.
- Trigger `0e38d0266ebb4f86394823ffd7af19694176c670`; run `32922227911` = **SUCCESS**.
- V6 stream `debug/v144-rhythm-calibration/v6-attack-gate/v6-render-stream.json`; Git blob `6b372e97e0d8e7c3f700099333886f0840a5ed35`; SHA256 **`c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`**.
- V6 = **1149 events / 839 onsets**; removed 60 events / 52 attacks. No professional-reference read during generation, no Modal/L4, no Production modification.

## Frozen V6 calibration score — COMPLETE AND VERIFIED
- Run `32922358891` = **SUCCESS**; report `debug/v144-rhythm-calibration/v6-attack-gate/v6-calibration-score.json`, blob `6f336e2e1918c10ba86a406231ce1d6a9e34deef`; `predictionVerified=true`.
- V6 metrics: onset F1 `0.48682385575589454`; exact-event `0.04486873508353222`; pitch `0.6042959427207636`; pitch-class `0.8085918854415275`; measure+pitch `0.28544152744630075`; measure+pitch-class `0.4715990453460621`; position-content `0.469689737470167`.
- Every overall swept metric improved vs V5. Metrics improving on both odd/even splits: onset, pitch-class content, measure+pitch, measure+pitch-class.

## V6 pitch-opportunity diagnostic — COMPLETE
- Run `32922569934` = **SUCCESS**; report `debug/v144-rhythm-calibration/v6-attack-gate/v6-pitch-opportunity.json`, blob `8b95f34dd21121a3d81f1a34682e06920f0d8d5f`.
- Shared exact V6/reference onsets **351**; V6-only **488**; reference-only **252**.
- V6 primary exact hit **41**; exact reference MIDI exists in V2 candidate pool at **162** shared onsets; correct pitch class exists at **278**.
- Of 310 wrong primaries: **121 exact-selection opportunities**, **116 register-only opportunities**, **73 no-candidate-pitch-class misses**.
- Correct exact candidate source-score rank median **4**, mean `5.10`, p75 `7`, p90 `11`; source-score ranking is a major bottleneck.

## V6 source-only primary context sweep — COMPLETE, SUMMARY PENDING
- Script `analyzer/v144_v6_primary_context_sweep.py` commit `d9ec3317d42577528bbb4a30cc98190e5d815cb6`.
- Workflow `.github/workflows/v144-v6-primary-context-sweep.yml` commit `4a12b809872e058b2f3130eb9c90dc481cfbe215`.
- Trigger `e502af163de099b6824658fe7c58d6bee7ff5916`; run **`32922808616` = SUCCESS**.
- Persisted full report: `debug/v144-rhythm-calibration/v6-attack-gate/v6-primary-context-sweep.json`; blob **`c5875f8e3f0ee70816ed6c986b269fb3dc259820`**.
- 47 source-only selector policies tested: current/top-score baselines, local-neighbor continuity, time-weighted DP continuity, repeated-measure/same-step consensus. Selectors did not read the professional reference; reference used only for grading. No V7 candidate generated.
- Preliminary read of sorted report is unfavorable: first-ranked `local-neighbor-gap4.0-lambda0.20` has only one robust improved metric (`pitchClassContent`) while exact-event, pitch-content, measure+pitch, and measure+pitch-class regress. It changes 226 primaries and lowers exact-primary hits from 41 to 34.
- Search of the available report resource found **no policy with `regressedMetrics: []`**, but the large report output was truncated. Do not make a final V7/L4 decision until a compact all-policy summary is persisted.

## Next exact actions
1. Produce a compact summary of all 47 context policies from the persisted full JSON: max robust metric count, zero-regression count, best deltas for each metric/primary-hit count, top 10, and best policy per family.
2. Save checkpoint with that conclusion.
3. If no context selector gives multi-metric split-robust improvement, do **not** generate V7 from these rules.
4. Then inspect the preserved Modal/L4 archive and formulate a narrow separation experiment around the measured failure: 73 shared onsets with no correct pitch-class candidate plus the correlated source-score misranking problem.
5. Final legitimate validation still requires a different unseen professional song/reference.
