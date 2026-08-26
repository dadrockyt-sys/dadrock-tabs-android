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

## V144 calibration diagnostic V2 — COMPLETE
- Script: `analyzer/v144_rhythm_calibration_diagnostics.py`.
- Workflow: `.github/workflows/v144-rhythm-calibration-diagnostic.yml`.
- V2 trigger commit `7e73de6e87649bc3a6e958117c5bda4b7f86139d`; run `32920648462` = **SUCCESS**.
- Persisted aggregate report: `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`, V2 Git blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Exact consumed structured source was SHA-verified and deleted after diagnostics; only aggregates persisted.
- `candidateModified=false`, `modalInvoked=false`, `productionModified=false`, `unseenHoldout=false`.

## Confirmed V5 failure class — reconstruction / selection first
- Pitch content ignoring timing: 644 matches, F1 `0.5976798143851508`.
- Pitch-class content ignoring octave: 867 matches, F1 `0.8046403712296984`.
- Exact string/fret/pitch content F1 `0.4677494199535963`.
- Generated notes `1209` vs reference `946`; generated onsets `891` vs reference `603` — major over-generation.
- Exact onset positions already match at 360 of the 603 reference onset locations: onset F1 `0.4819277108433735`.
- At those 360 already-shared onset positions, pitch content F1 is only `0.562560620756547` while pitch-class F1 is `0.7720659553831232`; only 17 shared onsets have the exact pitch multiset and 59 have the exact pitch-class multiset.
- This directly shows that many timing positions are usable but the notes assigned to them are wrong, in the wrong octave/register, or over/under-voiced.
- Generated MIDI range `40-83` vs reference `40-71`; MIDI 64 is over-produced by `+205` notes. Several upper MIDI values occur repeatedly in V5 but never in this rhythm reference.
- Note/onset density remains heavily over-generated, including many events in calibration-reference-silent measures.

## Timing result — no global shift fix
- Pitch-conditioned absolute-step search still prefers `-14`, but V2 proves it is not a safe global timing correction.
- Unique-onset shift search improves onset F1 only from `0.4819277108433735` at zero shift to `0.4926372155287818` at `-26`; this tiny gain does not justify moving the grid.
- Quarter-song best unique-onset shifts vary widely: `-12`, `+6`, `0`, `-8` rather than one stable phase.
- Same-measure/same-pitch pairing: 305 pairs total; 48 exact-step, 85 within ±1 step, 140 within ±2; step deltas are broad rather than dominated by one offset.
- A one-measure pitch-only shift improves F1 modestly from `0.2831` to `0.3165`, again consistent with repeated riff structure rather than proof of a measure-origin bug.
- Conclusion: **do not apply a global timing or measure shift.** Keep timing stable for the first V6 experiment and attack reconstruction/selection first.

## V143 path inspection
- `analyzer/v143_reference_free_timing.py` estimates beat grid and bar phase from full-mix onset/low-frequency accents.
- `analyzer/v143_candidate_timing_adapter.py` maps Basic Pitch candidates onto that grid.
- `analyzer/v143_reference_free_rhythm_pipeline.py` uses caller-selected candidate rhythm stems plus paired carrier stems.
- V5 overlay explicitly did not relocate attacks. No V144 timing change has been made.

## V6 first target
1. Reduce non-rhythm / lead contamination and false-positive onsets before changing timing.
2. Reduce octave/register bias, especially unsupported upper-register hypotheses.
3. Improve pitch selection/voicing at onset positions already supported by rhythm evidence.
4. Make each rule depend only on source/model evidence; the consumed professional reference is used for grading/calibration, not copied into runtime decisions.
5. Measure contamination gate and register/pitch changes as isolated V6 experiments.
6. Keep scorer and Modal/L4 assets preserved; use L4 only for a specific separation hypothesis or later GPU verification.
7. Final independent validation must use a different unseen professional song/reference.

## Next exact actions
1. Trace V5 attack rescue and primary-pitch selection logic, especially why MIDI 64/high-register hypotheses dominate and why silent/lead-dominant regions survive.
2. Build a V144 source-only diagnostic that scores V5 events by their original candidate evidence (source count, amplitude, grid error, carrier scores, model agreement) against calibration outcomes, without changing V5.
3. Derive conservative V6 gating/register rules from those source-only features, then generate the first V6 candidate.
4. Save checkpoint before V6 generation.
