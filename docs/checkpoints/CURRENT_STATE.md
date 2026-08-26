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
- Frozen stream: `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json` SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- 1209 events / 891 onsets / 113 measures vs calibration reference 946 notes / 603 playable onsets.
- PDF fidelity `1.0`; terminal professional pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.

## Calibration diagnosis
- Diagnostic run `32920648462` SUCCESS; aggregate report `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`, blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Content-only calibration metrics: pitch F1 `0.5976798143851508`; pitch-class F1 `0.8046403712296984`; position-content F1 `0.4677494199535963`; exact-onset F1 `0.4819277108433735`.
- Major over-generation/register bias: generated MIDI `40-83` vs reference `40-71`; MIDI 64 over-produced by `+205`.
- **No global timing shift.** Offset gains are tiny/inconsistent by song section; timing remains unchanged for first V6.

## Exact source evidence recovered
- Authorized V2 artifact `9548666053` from run `32805316807`; ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- `repaired-timing-precision-candidate-product.json` SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Replay evidence has 984 eligible attacks, 725 originally retained, 259 pruned, with attack/grid/stem/sweep/detection and per-MIDI evidence.

## V5 source-evidence diagnostic — COMPLETE
- `analyzer/v144_v5_source_evidence_diagnostics.py`; run `32921346833` SUCCESS; report `debug/v144-rhythm-calibration/v5-source-evidence-diagnostic.json`.
- Rescued attacks are useful: 166 rescued attacks have exact-onset precision `0.48193` vs baseline `0.38621`; do **not** undo V3 rescue wholesale.
- Best conservative source-only attack gate: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`.
- Gate keeps 839/891 attacks and 351 exact reference onsets; onset F1 `0.48682` vs V5 `0.48193`, improving both odd/even splits.
- Pitch/voicing remains dominant failure. Only 48/1209 events are exact measure+step+MIDI calibration matches; 42/48 are V5 primaries. V5 has 318 secondary notes but only 6 exact event matches among them.
- Per-pitch/source-view evidence overlaps heavily between correct/false events; no hard MIDI ceiling or octave rewrite is justified.

## V6 policy sweep — COMPLETE
- Script `analyzer/v144_v6_policy_sweep.py`; workflow `.github/workflows/v144-v6-policy-sweep.yml`.
- Trigger commit `bab2e421a08387a3cfbdec7ef6586f408384f903`; run `32921577491` = **SUCCESS**.
- Persisted aggregate report: `debug/v144-rhythm-calibration/v6-policy-sweep.json`, blob `544fb3cd35c49b09cdc5ed56a02980f18d375b34`.
- Sweep tested primary-only, original-V2-selected, rank/relative-score/absolute-score/attack/sustain secondary gates and max-two voicing, with/without the conservative attack gate.
- **No secondary-note pruning policy is clean enough to promote yet.** Each attractive secondary policy trades away other useful metrics/splits.
- The only tested policy with **no overall metric regressions** is: keep all V5 voicing on attacks that pass `detection>=12 && gridError<=0.06`.
- Expected calibration result: 1149 events / 839 onsets; onset F1 `0.48682385575589454`; pitch-content F1 `0.6042959427207636`; pitch-class F1 `0.8085918854415275`; measure+pitch F1 `0.28544152744630075`; measure+pitch-class F1 `0.4715990453460621`; position-content F1 `0.469689737470167`; exact-event F1 `0.04486873508353222`.
- It improves every overall swept metric vs V5. Robust on both odd/even splits for onset, pitch-class content, measure+pitch, and measure+pitch-class; some even-split micro-regressions remain in exact-event/pitch/position.

## V6 decision locked
- V6 first change = **attack gate only**: `detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06`.
- Do not move attacks, rewrite pitches, impose MIDI ceiling, undo rescue logic, or prune secondary voicings in V6.
- Generation must not read the professional reference.

## V6 generation — READY, NOT TRIGGERED YET
- Source-only generator: `analyzer/v144_generate_v6_attack_gate.py`, commit `7ba6cc7e59b7882fa99350f612e8ac5742f0286d`.
- CPU generation workflow: `.github/workflows/v144-v6-generate.yml`, commit `82d8115f0bbc3cf8fbb049052419ff14c902ad00`.
- Generator verifies frozen V5 has 1209 events / 891 onsets and exact V2 replay evidence has 984 attacks.
- It applies only the locked attack gate and copies every surviving V5 event object unchanged.
- It hard-fails unless output is exactly 1149 events / 839 onsets (60 events / 52 attacks removed).
- Workflow SHA-verifies frozen V5, V2 artifact ZIP, and V2 candidate product; **does not fetch the professional reference**; no Modal/L4; no Production.
- Planned outputs are separate under `debug/v144-rhythm-calibration/v6-attack-gate/`: `v6-render-stream.json`, `v6-generation-manifest.json`, and `v6-generation-sha256.txt`.

## Next exact actions
1. Trigger `debug/v144-rhythm-calibration/run-v6-generate.txt` once.
2. Verify generation run success and persisted V6 SHA/counts.
3. Add/run a separate calibration scorer that fetches the already-consumed professional reference only after generation; verify V6 metrics match the policy-sweep prediction.
4. Save checkpoint immediately after V6 generation/scoring.
5. Next repair target: source separation / pitch-voicing discrimination. Use current source evidence first; bring preserved L4 back only for an explicit separation hypothesis if CPU views cannot distinguish contamination.
