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

## What the failure strongly suggests
- Only about 305 of the 1209 generated notes match reference MIDI content when timing is ignored (derived from the persisted pitch-content F1 and 1209/946 note counts).
- Only about 48 generated/reference notes match under the scorer's pitch+timing tolerance (derived from the persisted pitch/timing F1).
- Therefore this is not a PDF problem. It is primarily a musical reconstruction problem, with a likely additional alignment/placement problem.
- First diagnostic priority: determine how much of the timing collapse is explained by global/bar/step alignment versus genuinely wrong pitches/onsets.
- Second priority: quantify over-generation (1209 generated vs 946 reference notes), pitch/octave errors, onset density errors, and string/fret voicing errors.

## Scorer preserved for future testing
- Preservation manifest: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`.
- Keep `validation/rhythm_holdout/score_rhythm_holdout.py`, `canonical.py`, freeze builder, PDF fidelity validator, completeness validator, and V5 scorer workflows/results intact.
- The V5 final result must never be overwritten.
- New calibration diagnostics may reuse scorer logic and may produce new files under a V144 calibration directory.

## Modal/L4 preserved for future testing
- Preserve branch `v143-github-modal-smoke`.
- Preserve `.github/workflows/v143-modal-live-smoke.yml` blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`.
- Preserve `analyzer/v143_modal_http_live_smoke.py` on `v143-ai-tab-production-integration`, blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`.
- That probe explicitly expects `modalGpu == "L4"` and deterministic separator settings.
- Do not run Modal/L4 yet just to iterate blindly. Use it after CPU diagnostics identify a concrete hypothesis or when a candidate is ready for GPU verification.

## V144 diagnostic — PREPARED, NOT RUN YET
- Added `analyzer/v144_rhythm_calibration_diagnostics.py` in commit `bbd153fbd4042475520b9721e12161df95188078`.
- It does not modify V5 and does not call Modal.
- It compares the frozen V5 against the now-calibration professional structured source and emits aggregate diagnostics only.
- It measures exact pitch content, pitch-class content, measure+pitch, exact pitch/timing, exact position content/timing, onset alignment, best global step shift, best semitone shift, best joint pitch+timing shift, quarter-song alignment drift, per-measure note/onset density error, and MIDI distribution deltas.
- Expected counts are hard-checked: 1209 generated notes and 946 reference notes.

## Next exact actions
1. Add a CPU-only V144 workflow that fetches/verifies the exact previously consumed structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`, runs the diagnostic, and persists only its aggregate report.
2. Trigger that diagnostic once and inspect the report.
3. Use the result to decide whether V6 first fixes timing/alignment, pitch selection/over-generation, or both.
4. Keep terminal V5 artifacts unchanged.
5. Use Modal/L4 only after a specific hypothesis justifies it.
6. Once calibration performance is strong, freeze a candidate and validate once on a new unseen professional song/reference.
