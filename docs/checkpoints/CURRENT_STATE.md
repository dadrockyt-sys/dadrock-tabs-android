# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using the consumed V5 professional reference as calibration data; preserve V5 history; do not touch main/Production.**

## Phase boundaries
- V5 terminal/immutable on `v143-contextual-prune-lobo`; all new work only on `v144-rhythm-post-holdout-calibration`.
- Consumed `Are You Gonna Go My Way` professional reference is calibration data, not unseen holdout. New independent final validation requires a different unseen professional song/reference.
- Do not modify/merge `main` or Production.
- Preserve scorer and Modal/L4 work. Do not run L4 without a specific justified hypothesis.

## Terminal V5
- Archive `docs/checkpoints/V5_TERMINAL_RECORD.md`; terminal checkpoint `12898eb6590067d06ded7620eb86964bd9124c10`; result commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`; run `32919666736`.
- 1209 notes/events, 891 onsets, 113 measures vs reference 946 notes / 603 playable onsets.
- PDF fidelity `1.0`; professional pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.
- Raw stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; canonical scorer SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.

## Scorer + Modal/L4 preserved
- `docs/testing/SCORER_MODAL_L4_ARCHIVE.md` preserves scorer/canonical/freeze/fidelity/completeness harness and V5 evidence.
- Preserve branch `v143-github-modal-smoke`, workflow blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, integration probe blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`.
- L4 probe expects `modalGpu == "L4"`, seed `143`, Demucs shifts `1`, paired carrier stems, two-view bend/legato consensus.

## Calibration diagnostic V2 — COMPLETE
- `analyzer/v144_rhythm_calibration_diagnostics.py`; run `32920648462` SUCCESS; report `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json` blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Pitch content ignoring timing F1 `0.5976798143851508`; pitch-class F1 `0.8046403712296984`; exact string/fret/pitch content F1 `0.4677494199535963`; exact onset F1 `0.4819277108433735`.
- Major over-generation and upper-register bias. Generated MIDI `40-83` vs reference `40-71`; MIDI 64 over-produced `+205`.
- **No global timing shift.** Unique-onset shift gives only tiny gain and quarter-song offsets vary. Keep timing fixed for first V6 work.

## Original V2 source evidence recovered exactly
- Authorized precursor run `32805316807`; live artifact `9548666053`, ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- Candidate product SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Complete replay evidence: 984 eligible attacks, 725 originally retained, 259 originally pruned, per-attack precision/grid/stem/sweep/detection evidence, per-MIDI attack/early/sustain and paired-view evidence.

## V5 source-evidence diagnostic — COMPLETE
- Script `analyzer/v144_v5_source_evidence_diagnostics.py`; workflow `.github/workflows/v144-v5-source-evidence-diagnostic.yml`.
- Trigger commit `cef48c097c3c11db5f2b1882a006dfbdfc882b41`; run `32921346833` = **SUCCESS**.
- Persisted report `debug/v144-rhythm-calibration/v5-source-evidence-diagnostic.json`.
- V2 artifact and consumed source were exact-hash verified; transient materials removed; only aggregates persisted. `candidateModified=false`, `modalInvoked=false`, `productionModified=false`.

## Source-evidence findings
### Attack rescue was beneficial; do not revert V3 wholesale
- All V5 exact-onset attack metric: 360/891; precision `0.4040`, recall `0.5970`, F1 `0.48193`.
- Baseline 725 attacks: 280 exact reference onsets; precision `0.3862`.
- Rescued 166 attacks: 80 exact reference onsets; precision **`0.48193`**. Rescued attacks are substantially more precise than baseline attacks, so deleting rescue logic would throw away useful work.
- Correct vs false attacks have very similar source-evidence distributions overall. Simple confidence thresholds cannot solve the contamination problem alone.

### A conservative attack gate gives only a small, robust gain
- Best tested cross-split source-only attack rule: `detectionCountSum >= 12 AND precisionGridErrorSeconds <= 0.06`.
- Keeps 839/891 attacks, 351 exact-onset matches.
- Overall attack precision `0.41836`, recall `0.58209`, F1 `0.48682` vs V5 `0.48193`.
- Odd-measure F1 `0.50071`; even-measure F1 `0.47361`, both above unfiltered split baseline (`0.49796` odd / `0.46640` even).
- Improvement is real but small; this gate is a candidate V6 component, not a complete fix.

### Pitch/voicing is still the dominant failure
- Exact event metric: only 48/1209 V5 notes match exact reference measure+step+MIDI, F1 `0.04455`.
- Baseline exact event precision `3.31%`; rescued exact event precision `6.61%` — again, rescue notes are not the main regression.
- 42 of 48 exact matches are V5 primaries; only 6 exact matches are secondary notes. V5 has exactly one primary per attack (891 primaries), leaving 318 secondary notes that contribute disproportionately to over-voicing.
- Per-candidate attack/body/score/rank evidence for exact vs false V5 notes overlaps heavily; no single score threshold is justified yet.
- Octave confusion exists but is not the dominant mechanism: among 1161 false exact events, 26 have a lower-octave candidate that is the exact reference pitch at that onset and 5 have an upper-octave reference candidate. A hard octave replacement rule would be unjustified.
- The paired-view evidence deltas are also similar for exact vs false events, consistent with the existing two views being too correlated to distinguish contamination reliably.

## Current V6 direction
1. Keep V3 rescue concept; do not revert to baseline-only.
2. Test the conservative attack gate `detection>=12 & grid<=0.06` as one isolated component.
3. Focus next on **polyphonic expansion / secondary-note policy**, because V5 has 318 secondary notes but only 6 exact event matches among them and overall note count is 263 above the professional rhythm reference.
4. Do not use a MIDI ceiling or hard octave rewrite copied from this song.
5. Sweep source-only secondary policies (primary-only; top-N; score/rank/relative-score/original-selection conditions) and evaluate pitch content, pitch-class content, exact event metric, onset metric, density, and odd/even splits before generating V6.
6. If source-only secondary evidence cannot separate good/bad notes, that becomes a concrete future L4 separation hypothesis; do not run L4 yet.

## Next exact actions
1. Add a V144 V6 policy sweep over the frozen V5 + exact V2 evidence, with no candidate output yet.
2. Require any chosen policy to improve multiple calibration metrics and both odd/even splits, not only one headline score.
3. Save checkpoint before V6 generation.
4. Generate V6 as a separate candidate only after the policy sweep selects a defensible source-only rule.
