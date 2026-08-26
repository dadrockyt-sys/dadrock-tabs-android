# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using the consumed V5 professional reference as calibration data; preserve V5 history; do not touch main/Production.**

## Phase change authorized by user
- V5 remains terminal and immutable on `v143-contextual-prune-lobo`.
- New work happens only on `v144-rhythm-post-holdout-calibration`.
- The old `Are You Gonna Go My Way` professional reference has been consumed and may now be used repeatedly for calibration/diagnostics/training.
- Any improvement measured against that reference is **not** an independent holdout result.
- A different unseen song/reference will be required for the next legitimate final validation.
- Do not merge or modify `main`/Production during this calibration phase.

## Preserved terminal V5 record
- Archive: `docs/checkpoints/V5_TERMINAL_RECORD.md`.
- Terminal checkpoint commit on old branch: `12898eb6590067d06ded7620eb86964bd9124c10`.
- Final result commit: `4af2bf9046a5f038106a855eb03fbaefaebf299e`.
- Final run `32919666736`.
- V5: 1209 rendered events / 113 measures; PDF fidelity 1.0.
- Final musical result: pitch-content F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.

## Scorer + Modal/L4 preservation
- Preservation manifest: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`.
- Keep the professional scorer/canonical/freeze/fidelity/completeness harness and all V5 scorer evidence intact.
- Preserve branch `v143-github-modal-smoke`, workflow blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, and integration probe blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`.
- Do not run Modal/L4 blindly. Use it later for a specific hypothesis or end-to-end verification.

## V144 calibration diagnostic — baseline complete
- Script: `analyzer/v144_rhythm_calibration_diagnostics.py`.
- Workflow: `.github/workflows/v144-rhythm-calibration-diagnostic.yml`.
- Baseline trigger commit `0222b076fa99e7c1a51b40de90d0871741b1086d`; run `32920350517` = **SUCCESS**.
- Persisted aggregate report: `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`, baseline Git blob `e8d7cbdc9ef2e78bda5c9e989adad10665b2142d`.
- Exact consumed structured source was SHA-verified and deleted after diagnostics; only aggregates were persisted.
- `candidateModified=false`, `modalInvoked=false`, `productionModified=false`, `unseenHoldout=false`.

## Baseline findings — musical reconstruction is definitely poor
- Pitch content ignoring timing: 644 matches, F1 `0.5976798143851508`.
- Pitch-class content ignoring octave: 867 matches, F1 `0.8046403712296984`.
- Exact string/fret/pitch content F1 is `0.4677494199535963`.
- Generated notes `1209` vs reference `946`; generated onsets `891` vs reference `603` — major over-generation.
- Exact onset locations nevertheless have 360 matches; onset F1 `0.4819277108433735`. This is important: a large fraction of professional onsets already coincide with V5 grid locations.
- Note density: 67 measures over-generated, 33 under-generated, 13 exact; mean absolute note-count error `4.4867` per measure.
- Onset density: 74 measures over-generated, 20 under-generated, 19 exact; mean absolute onset-count error `3.0973` per measure.
- Several measures contain many generated events while the professional rhythm track has zero playable notes (notably 110, 106, 111, 38, 69, 113), consistent with non-rhythm contamination / insufficient source gating.
- Generated MIDI range `40-83` vs reference `40-71`; MIDI 64 is over-produced by `+205` notes, while important lower-register notes are under-produced.
- Strong conclusion: V5 has substantial over-generation, register/octave bias, and voicing/pitch-selection errors.

## Timing interpretation — first report required a correction
- Baseline exact pitch+timing is only 48 matches / F1 `0.044547563805104405`.
- A pitch+timing absolute-step search found a best shift of `-14` steps, but **do not treat that as proven global clock/measure error yet**.
- Because the song contains repeated riffs and because 360 onset locations already match exactly, a pitch-conditioned shift search can prefer a repeated-pattern alias.
- V143 timing code was inspected: `v143_reference_free_timing.py` chooses bar phase from four beat-accent classes; `v143_candidate_timing_adapter.py` then maps all notes using that phase. A real phase error here would propagate globally, but the current evidence is not sufficient to assert that happened.
- Therefore no timing correction has been applied and `-14` will not be hardcoded.

## Alias-resistant diagnostic V2 — prepared
- Updated `analyzer/v144_rhythm_calibration_diagnostics.py` in commit `06e09c8f14a9fb3b2028a2638e38c51edacb67b8`.
- Added unique-onset absolute-step shift search (one vote per onset, not per note), measure-shift pitch search, same-measure/same-pitch nearest step-delta histogram, and pitch/pitch-class quality restricted to already-shared onset positions.
- Goal: separate genuine grid phase error from repeated-riff aliasing and from wrong pitches placed on otherwise-correct onsets.
- V5 remains unchanged; no Modal; no Production.

## Next exact actions
1. Re-run the CPU calibration diagnostic with schema V2 and persist aggregates.
2. If unique-onset and same-measure pitch-step evidence confirms a timing-origin problem, design a reference-free V144 timing experiment. Otherwise prioritize contamination/register/pitch selection first.
3. Build V6 changes as isolated experiments; never modify terminal V5 artifacts.
4. Use Modal/L4 only when a specific separation/stem hypothesis justifies GPU testing.
5. Final independent validation must use a new unseen professional song/reference.
