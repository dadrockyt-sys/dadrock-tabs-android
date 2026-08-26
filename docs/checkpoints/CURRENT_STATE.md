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

## V144 calibration diagnostic — COMPLETE
- Script: `analyzer/v144_rhythm_calibration_diagnostics.py`.
- Workflow: `.github/workflows/v144-rhythm-calibration-diagnostic.yml`.
- Trigger commit `0222b076fa99e7c1a51b40de90d0871741b1086d`.
- Run `32920350517` = **SUCCESS**.
- Persisted aggregate report: `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`, Git blob `e8d7cbdc9ef2e78bda5c9e989adad10665b2142d`.
- Exact consumed structured source was SHA-verified and deleted after diagnostics; only aggregates were persisted.
- `candidateModified=false`, `modalInvoked=false`, `productionModified=false`, `unseenHoldout=false`.

## Diagnostic findings — two independent failure classes
### 1. Timing / structural phase problem
- Baseline exact pitch+timing: 48 matches, F1 `0.044547563805104405`.
- Best global pitch+timing step shift is `-14` sixteenth-note steps: 136 matches, F1 `0.1262180974477958`.
- Best joint timing+semitone search is also `stepDelta=-14`, `semitoneDelta=0`; there is no global transposition error.
- Quarter-song best pitch/timing shifts are remarkably stable: `-14`, `-13`, `-14`, `-14`.
- This strongly indicates an approximately 14-step global phase/measure-origin error in V5 placement, not random local timing noise.
- A global shift alone is insufficient: even after the best shift, pitch+timing F1 remains only `0.1262`.

### 2. Musical reconstruction / contamination / register problem
- Pitch content ignoring timing: 644 matches, F1 `0.5976798143851508`.
- Pitch-class content ignoring octave: 867 matches, F1 `0.8046403712296984`.
- Therefore the model often finds the correct pitch class but chooses the wrong octave/register or adds extra notes.
- Exact string/fret/pitch content F1 is `0.4677494199535963`, below pitch-content F1, so voicing selection is another meaningful error source.
- Generated notes `1209` vs reference `946`; generated onsets `891` vs reference `603` — major over-generation.
- Note density: 67 measures over-generated, 33 under-generated, only 13 exact; mean absolute note-count error `4.4867` per measure.
- Onset density: 74 measures over-generated, 20 under-generated, only 19 exact; mean absolute onset-count error `3.0973` per measure.
- Several measures contain many generated events while the professional rhythm track has zero playable notes (notably 110, 106, 111, 38, 69, 113). This is strong evidence that V5 is following non-rhythm material/noise in parts of the song.
- Register bias is severe: generated MIDI range `40-83` while reference is `40-71`.
- MIDI 64 is over-produced by `+205` notes (291 generated vs 86 reference), while low/register notes such as MIDI 40, 55, and 57 are strongly under-produced.
- This points to high-register/string bias plus insufficient rhythm-source isolation, not a simple pitch transpose bug.

## Repair direction for V6
1. Do **not** hardcode `-14` as a song-specific correction. Find the source of the measure/downbeat origin error and make phase alignment reference-free.
2. Inspect the V143 timing/bar assignment code for how measure 1 / step 0 is chosen; create a new V144 analyzer path rather than altering terminal V5.
3. Add stronger rhythm-source gating so silent/lead-dominant regions do not emit dense rhythm events.
4. Rebalance pitch/register selection toward plausible rhythm-guitar register and penalize unsupported high-register notes, but derive rules from source-only evidence rather than copying the professional pitches.
5. Re-run the calibration diagnostic after each isolated V6 change to measure which error class improves.
6. Use Modal/L4 only once a concrete separation/stem hypothesis is ready to test.
7. Final independent validation must use a new unseen professional song/reference.

## Next exact actions
1. Inspect V143 timing/downbeat/measure assignment and rhythm-carrier selection logic without modifying it.
2. Design V144 timing-origin correction and contamination gate as separate experiments so their effects can be measured independently.
3. Save checkpoint before any V6 candidate generation.
