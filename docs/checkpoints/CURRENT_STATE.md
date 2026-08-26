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

## Calibration diagnosis
- Run `32920648462` SUCCESS; `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json` blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Content calibration: pitch F1 `0.5976798143851508`; pitch-class F1 `0.8046403712296984`; position-content F1 `0.4677494199535963`; exact-onset F1 `0.4819277108433735`.
- Major over-generation/register bias; no defensible global timing shift. Timing stays unchanged for V6.

## Exact V2 source evidence
- Authorized artifact `9548666053` from run `32805316807`; ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- V2 candidate-product SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- 984 eligible attacks with attack/grid/stem/sweep/detection and per-MIDI evidence.

## Source-evidence + policy sweeps — COMPLETE
- Source-evidence run `32921346833` SUCCESS. Rescued attacks were useful; do not undo V3 rescue wholesale.
- Best conservative source-only gate: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`.
- V6 policy-sweep run `32921577491` SUCCESS; report `debug/v144-rhythm-calibration/v6-policy-sweep.json` blob `544fb3cd35c49b09cdc5ed56a02980f18d375b34`.
- No secondary-note pruning policy was clean enough to promote. The only tested policy with no overall metric regressions was the conservative attack gate while keeping surviving V5 voicings untouched.
- Predicted calibration metrics for that policy: 1149 events / 839 onsets; onset F1 `0.48682385575589454`; pitch F1 `0.6042959427207636`; pitch-class F1 `0.8085918854415275`; measure+pitch F1 `0.28544152744630075`; measure+pitch-class F1 `0.4715990453460621`; position-content F1 `0.469689737470167`; exact-event F1 `0.04486873508353222`.

## V6 source-only generation — COMPLETE
- Generator `analyzer/v144_generate_v6_attack_gate.py` commit `7ba6cc7e59b7882fa99350f612e8ac5742f0286d`.
- Workflow `.github/workflows/v144-v6-generate.yml` commit `82d8115f0bbc3cf8fbb049052419ff14c902ad00`.
- Trigger commit `0e38d0266ebb4f86394823ffd7af19694176c670`; Actions run `32922227911` = **SUCCESS**.
- V6 stream: `debug/v144-rhythm-calibration/v6-attack-gate/v6-render-stream.json`; Git blob `6b372e97e0d8e7c3f700099333886f0840a5ed35`; SHA256 `c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`.
- Generation manifest: `debug/v144-rhythm-calibration/v6-attack-gate/v6-generation-manifest.json`; blob `f3c5ecdb271db5d7ab457e2eb5aecce84f49bea9`; SHA256 `d99d0384ac5d12377bf9656cdfe5d9ef5eede41bc15e3dba97a5a19d1865cc32`.
- V6 = **1149 events / 839 onsets**. Exactly 60 V5 events and 52 V5 attacks were removed.
- Surviving event content was copied unchanged. No attack relocation, pitch rewrite, octave ceiling, secondary-voicing prune, or rescue rollback.
- Generation read no professional reference (`calibrationReferenceUsedDuringGeneration=false`), invoked no Modal/L4, and modified no Production.
- V6 primary events = 839; attack-class event counts after gate: baseline 913, rescued 236.

## Next exact actions
1. Add a separate calibration scorer pinned to V6 SHA256 `c1e6389fdf9d7a18adb50407f248673fe494b236889d635a467100adb6070ddf`.
2. That scorer may fetch the already-consumed professional reference only after V6 is frozen; score V5 and V6 independently with the same metric implementation and verify V6 matches the policy-sweep prediction.
3. Persist only aggregate calibration results; keep V6 immutable.
4. Save checkpoint immediately after scoring.
5. Next repair target: source separation / pitch-voicing discrimination. Use CPU/source evidence first; bring preserved L4 back only for an explicit separation hypothesis if current views cannot distinguish contamination.
