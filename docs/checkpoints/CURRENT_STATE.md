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

## V144 diagnostic — READY TO TRIGGER
- Diagnostic script: `analyzer/v144_rhythm_calibration_diagnostics.py`, added in commit `bbd153fbd4042475520b9721e12161df95188078`.
- CPU workflow: `.github/workflows/v144-rhythm-calibration-diagnostic.yml`, added in commit `6dded05029b35b65b7be9355f12fba00566d388a`.
- Workflow runs only manually or on exact trigger path `debug/v144-rhythm-calibration/run-v5-diagnostic.txt` on this branch.
- It verifies the frozen V5 stream hash, verifies the existing terminal result, fetches and SHA-verifies the exact consumed structured source, runs aggregate diagnostics, deletes the transient source, and persists only `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`.
- No Modal and no Production access.

## Next exact actions
1. Create `debug/v144-rhythm-calibration/run-v5-diagnostic.txt` to run the CPU diagnostic once.
2. Read the aggregate report and determine whether timing/alignment, pitch selection/over-generation, or both are the first V6 target.
3. Keep terminal V5 artifacts unchanged.
4. Use Modal/L4 only after a specific hypothesis justifies it.
5. Once calibration performance is strong, freeze a candidate and validate once on a new unseen professional song/reference.
