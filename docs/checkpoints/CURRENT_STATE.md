# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using consumed V5 professional reference as calibration data; preserve V5 history; never touch main/Production during calibration.**

## Boundaries
- Terminal V5 stays immutable on `v143-contextual-prune-lobo`; V144 only for new calibration work.
- `Are You Gonna Go My Way` reference is consumed calibration data, not unseen holdout. Final independent proof needs a different unseen professional song/reference.
- Scorer + Modal/L4 archive: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`. Preserve all scorer/freeze/fidelity assets, branch `v143-github-modal-smoke`, workflow blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, integration L4 probe blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`. Do not run L4 without a specific justified hypothesis.

## Terminal V5 facts
- Archive `docs/checkpoints/V5_TERMINAL_RECORD.md`; final result commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`; run `32919666736`.
- 1209 notes/events, 891 onsets vs reference 946 notes / 603 playable onsets; 113 measures.
- PDF fidelity `1.0`; professional pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.
- Stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; canonical scorer SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.

## Calibration V2 findings
- Diagnostic run `32920648462` SUCCESS; report `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json` blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Pitch content ignoring timing F1 `0.5976798143851508`; pitch-class F1 `0.8046403712296984`; position content F1 `0.4677494199535963`; exact onset F1 `0.4819277108433735`.
- Major over-generation/register bias: MIDI range `40-83` vs reference `40-71`, MIDI 64 `+205` notes.
- No global timing shift: unique-onset offset gives tiny gain and quarter-song offsets vary. Timing remains unchanged for first V6 experiments.

## Exact source evidence recovered
- Authorized V2 artifact `9548666053` from run `32805316807`; ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- `repaired-timing-precision-candidate-product.json` SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- 984 eligible attacks, 725 originally retained, 259 pruned, complete attack/grid/stem/sweep/detection and per-MIDI attack/early/sustain/paired-view evidence.

## Source-evidence diagnostic complete
- `analyzer/v144_v5_source_evidence_diagnostics.py`; run `32921346833` SUCCESS; report `debug/v144-rhythm-calibration/v5-source-evidence-diagnostic.json`.
- Rescued 166 attacks have exact-onset precision `0.48193` vs baseline attack precision `0.38621`; **do not undo V3 rescue wholesale**.
- Best tested conservative attack gate: `detectionCountSum>=12 && precisionGridErrorSeconds<=0.06`. Keeps 839 attacks / 351 exact onsets; F1 `0.48682` vs V5 `0.48193`; improves odd and even splits. Useful but small.
- Exact event matches only 48/1209. 42/48 are V5 primaries; only 6 exact matches are among 318 secondary notes. Secondary/polyphonic expansion is the next target.
- Per-pitch score/attack/sustain/view evidence overlaps heavily between exact and false notes. No hard MIDI ceiling or octave rewrite is justified. Paired-view deltas are also too similar, suggesting correlated source views/contamination.

## V6 policy sweep — PREPARED, NOT RUN YET
- Added `analyzer/v144_v6_policy_sweep.py` commit `a4869c96c8b07793284eb926be8ed67a844ed3a1`.
- Added `.github/workflows/v144-v6-policy-sweep.yml` commit `1f9f8729df9f088316202f14ad120fc315b8d42b`.
- No candidate is generated. It pins V5 + exact V2 artifact + consumed source, then compares source-only policies:
  - no secondary pruning / primary-only;
  - primary + original V2 selected;
  - rank/relative-score/absolute-score secondary gates;
  - attack-strength/sustain secondary gates;
  - primary + best one secondary;
  - each with and without conservative attack gate `detection>=12&grid<=0.06`.
- Metrics include exact event, onset, pitch content, pitch-class content, measure+pitch, measure+pitch-class, position content, event/onset counts, and odd/even split deltas.
- Policies are ranked by robust improvements across multiple metrics/splits; report only, no V6 output.

## Next exact actions
1. Trigger `debug/v144-rhythm-calibration/run-v6-policy-sweep.txt` once.
2. Inspect report; choose a policy only if it improves multiple metrics and does not hide a split regression.
3. Save checkpoint before any V6 candidate generation.
4. Generate V6 as a separate candidate, never mutate V5.
5. If no source-only secondary policy gives robust improvement, preserve that as evidence for a later explicitly authorized L4 separation experiment instead of forcing a weak rule.
