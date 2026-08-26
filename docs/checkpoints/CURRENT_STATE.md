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

## V144 calibration facts before V6
- Baseline diagnostic run `32920648462` SUCCESS: content pitch F1 `0.5976798143851508`, pitch-class `0.8046403712296984`, position-content `0.4677494199535963`, exact-onset `0.4819277108433735`.
- Major over-generation/register bias; no defensible global timing shift.
- Exact V2 artifact `9548666053` from run `32805316807`; ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`; V2 candidate-product SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Source-evidence run `32921346833` SUCCESS. Rescued attacks were useful; do not undo V3 rescue wholesale.
- Best conservative gate: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`.
- V6 policy sweep run `32921577491` SUCCESS. No secondary-note pruning policy was clean enough to promote.

## V6 source-only generation — COMPLETE
- Generator `analyzer/v144_generate_v6_attack_gate.py` commit `7ba6cc7e59b7882fa99350f612e8ac5742f0286d`; workflow `.github/workflows/v144-v6-generate.yml` commit `82d8115f0bbc3cf8fbb049052419ff14c902ad00`.
- Trigger `0e38d0266ebb4f86394823ffd7af19694176c670`; run `32922227911` = **SUCCESS**.
- V6 stream `debug/v144-rhythm-calibration/v6-attack-gate/v6-render-stream.json`; Git blob `6b372e97e0d8e7c3f700099333886f0840a5ed35`; SHA256 **`c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`**.
- V6 = **1149 events / 839 onsets**; removed 60 events / 52 attacks. Surviving V5 event content unchanged.
- No timing relocation, pitch rewrite, octave ceiling, secondary prune, rescue rollback, professional-reference read during generation, Modal/L4, or Production modification.

## Frozen V6 calibration score — COMPLETE AND VERIFIED
- Scorer `analyzer/v144_score_v6_calibration.py` commit `e5c215b741249c8acf8c9be360d987facb33a3df`; workflow commit `b6f616c36be13003225da3bf9e3904b2e4c68458`.
- Trigger `6e17c83f656deb30b27c24fc07f158e1f3346067`; run `32922358891` = **SUCCESS**.
- Score report `debug/v144-rhythm-calibration/v6-attack-gate/v6-calibration-score.json`; blob `6f336e2e1918c10ba86a406231ce1d6a9e34deef`; `predictionVerified=true`.
- Every overall swept metric improved vs V5. V6: onset F1 `0.48682385575589454`; exact-event `0.04486873508353222`; pitch `0.6042959427207636`; pitch-class `0.8085918854415275`; measure+pitch `0.28544152744630075`; measure+pitch-class `0.4715990453460621`; position-content `0.469689737470167`.
- Metrics improving on both odd/even splits: onset, pitch-class content, measure+pitch, measure+pitch-class. Even-split micro-regressions remain in exact-event, pitch-content, position-content.

## V6 pitch-opportunity diagnostic — COMPLETE
- Script `analyzer/v144_v6_pitch_opportunity_diagnostic.py` commit `f2a462b919cf36b08f9e6b1829414c09b9d734f5`; workflow `.github/workflows/v144-v6-pitch-opportunity.yml` commit `423a83fb096c0b7951a2f18ecc86b6da7218499c`.
- Trigger `cbaa555dfe11c7e89411dc01596b9535547a4640`; run `32922569934` = **SUCCESS**.
- Report `debug/v144-rhythm-calibration/v6-attack-gate/v6-pitch-opportunity.json`; blob `8b95f34dd21121a3d81f1a34682e06920f0d8d5f`.
- Frozen V6/reference exact shared onsets: **351**. V6-only onsets: **488**. Reference-only onsets: **252**.
- At the 351 shared onsets:
  - V6 primary exact-reference-pitch hit: **41**.
  - Any current V6 event exact hit: **47**.
  - Top V2 source-score candidate exact hit: **35**.
  - Exact reference MIDI exists somewhere in the original V2 candidate pool: **162**.
  - Correct reference pitch class exists somewhere in the original V2 candidate pool: **278**.
  - Full reference MIDI set covered by candidates: **99**; full reference pitch-class set covered: **211**.
- Of **310 wrong V6 primaries**:
  - **121 selection-fixable**: exact reference MIDI is already in the V2 candidate set.
  - **116 register-only opportunity**: exact MIDI absent, but correct reference pitch class exists in another register.
  - **73 candidate-generation/separation misses**: no V2 candidate even matches a reference pitch class.
- This opportunity split is similar on odd/even measures: selection-fixable `66/55`, register-only `51/65`, candidate-generation miss `37/36`.
- Exact correct candidates are usually not the source-score winner: among 162 onsets with an exact candidate, best correct-candidate source-score rank median **4**, mean `5.10`, p75 `7`, p90 `11`; score gap from top median **2.47**, mean `2.27`.
- Conclusion: **do not jump to L4 yet.** The existing candidate pool contains substantial recoverable pitch information; source-score ranking is the bigger immediate problem at shared onsets. However, 73 primary misses have no correct pitch class candidate and remain a concrete future separation/L4 target.

## Next exact actions — context selection before L4
1. Keep V6 immutable.
2. Build a report-only CPU primary-selection/context sweep over frozen V6 + exact V2 evidence.
3. Test source-only policies that can re-rank broad candidate pools without copying the calibration answer: local register continuity, sequence/Dynamic Programming continuity, nearby repeated-measure/step consensus, and recurring-riff candidate support.
4. Score simulated primary replacement against calibration metrics using the reference only for grading, not runtime decisions. Do not score string/fret position for replaced-MIDI simulations until a fingering mapping is defined.
5. Require improvement in multiple pitch metrics and odd/even internal splits before any V7 generation.
6. If context cannot exploit the 121 exact-candidate + 116 pitch-class opportunities, then formulate a specific L4 experiment around the remaining candidate-generation/separation failure.
7. Final legitimate validation still requires a different unseen professional song/reference.
