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

## Calibration diagnosis + source evidence
- Baseline diagnostic run `32920648462` SUCCESS. Content calibration: pitch F1 `0.5976798143851508`; pitch-class F1 `0.8046403712296984`; position-content F1 `0.4677494199535963`; exact-onset F1 `0.4819277108433735`.
- Major over-generation/register bias; no defensible global timing shift.
- Exact V2 artifact `9548666053` from run `32805316807`; ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`; V2 candidate-product SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Source-evidence run `32921346833` SUCCESS. Rescued attacks were useful; do not undo V3 rescue wholesale.
- Best conservative source-only gate: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`.

## V6 policy sweep — COMPLETE
- Run `32921577491` SUCCESS; report `debug/v144-rhythm-calibration/v6-policy-sweep.json` blob `544fb3cd35c49b09cdc5ed56a02980f18d375b34`.
- No secondary-note pruning policy was clean enough to promote.
- Locked V6 policy: keep all surviving V5 voicing, remove only attacks failing `detection>=12 && gridError<=0.06`.

## V6 source-only generation — COMPLETE
- Generator `analyzer/v144_generate_v6_attack_gate.py` commit `7ba6cc7e59b7882fa99350f612e8ac5742f0286d`.
- Workflow `.github/workflows/v144-v6-generate.yml` commit `82d8115f0bbc3cf8fbb049052419ff14c902ad00`.
- Trigger `0e38d0266ebb4f86394823ffd7af19694176c670`; run `32922227911` = **SUCCESS**.
- V6 stream `debug/v144-rhythm-calibration/v6-attack-gate/v6-render-stream.json`; Git blob `6b372e97e0d8e7c3f700099333886f0840a5ed35`; SHA256 **`c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`**.
- Generation manifest blob `f3c5ecdb271db5d7ab457e2eb5aecce84f49bea9`; SHA256 `d99d0384ac5d12377bf9656cdfe5d9ef5eede41bc15e3dba97a5a19d1865cc32`.
- V6 = **1149 events / 839 onsets**; removed exactly 60 events / 52 attacks.
- Surviving event content unchanged. No timing relocation, pitch rewrite, octave ceiling, secondary prune, or rescue rollback.
- Generation read no professional reference, invoked no Modal/L4, and touched no Production.

## Frozen V6 calibration score — COMPLETE AND VERIFIED
- Scorer `analyzer/v144_score_v6_calibration.py` commit `e5c215b741249c8acf8c9be360d987facb33a3df`.
- Workflow `.github/workflows/v144-v6-calibration-score.yml` commit `b6f616c36be13003225da3bf9e3904b2e4c68458`.
- Trigger `6e17c83f656deb30b27c24fc07f158e1f3346067`; Actions run `32922358891` = **SUCCESS**.
- Aggregate score `debug/v144-rhythm-calibration/v6-attack-gate/v6-calibration-score.json`; blob `6f336e2e1918c10ba86a406231ce1d6a9e34deef`.
- `predictionVerified=true`; frozen V5 and V6 reproduced expected metrics to `1e-12`.
- Every overall swept metric improved: onset `+0.0048961`, exact-event `+0.0003212`, pitch `+0.0066161`, pitch-class `+0.0039515`, measure+pitch `+0.0023789`, measure+pitch-class `+0.0029216`, position-content `+0.0019403` F1.
- Metrics improving on both odd/even splits: onset, pitch-class content, measure+pitch, measure+pitch-class.
- Even-split micro-regressions remain in exact-event, pitch-content, and position-content; V6 is a verified conservative improvement, not a solved transcription.
- Score used consumed reference only after V6 freeze. `candidateModified=false`, `modalInvoked=false`, `productionModified=false`, `unseenHoldout=false`.

## Pitch / voicing / source-discrimination diagnostic — READY, NOT TRIGGERED
- Report-only script `analyzer/v144_v6_pitch_opportunity_diagnostic.py` commit `f2a462b919cf36b08f9e6b1829414c09b9d734f5`.
- Workflow `.github/workflows/v144-v6-pitch-opportunity.yml` commit `423a83fb096c0b7951a2f18ecc86b6da7218499c`.
- Pins frozen V6 SHA256 `c1e6389f...` and exact V2 artifact/candidate-product identities.
- At the 351 exact shared V6/reference onsets it will classify primary pitch failures into:
  1. **selection-fixable**: exact reference MIDI already exists in original V2 candidate set;
  2. **register-only**: exact MIDI absent but correct pitch class exists in another octave/register;
  3. **candidate-generation/separation miss**: no original V2 candidate even matches a reference pitch class at that onset.
- Also measures current-primary hit, any-current-V6 hit, top-source-score hit, original-V2 selected/primary hit, full candidate-set coverage, correct-candidate source-score rank/gap, and odd/even split behavior.
- No candidate generation/modification; no Modal/L4; aggregate calibration report only.

## Next exact actions
1. Trigger `debug/v144-rhythm-calibration/run-v6-pitch-opportunity.txt` once.
2. If exact reference pitches commonly exist in V2 candidate pools, build source-only local/repetition/context selection sweeps before any V7.
3. If correct pitch classes are commonly absent from V2 candidate pools, treat that as concrete evidence for a better-separation experiment and formulate the preserved L4 test around that failure.
4. Save checkpoint immediately after the diagnostic.
5. Do not generate V7 until a rule improves multiple calibration metrics and survives internal splits.
6. Final legitimate validation still requires a different unseen professional song/reference.
