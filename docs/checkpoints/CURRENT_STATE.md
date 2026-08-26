# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v144-rhythm-post-holdout-calibration`
Priority: **repair Rhythm using the consumed V5 professional reference as calibration data; preserve V5 history; do not touch main/Production.**

## Phase boundaries
- V5 remains terminal/immutable on `v143-contextual-prune-lobo`.
- New work only on `v144-rhythm-post-holdout-calibration`.
- Consumed `Are You Gonna Go My Way` professional reference is calibration data now, not an unseen holdout.
- Improvements against it are calibration results only. A different unseen professional song/reference is required for independent final validation.
- Do not modify/merge `main` or Production.
- Preserve scorer and Modal/L4 work; do not run L4 blindly.

## Terminal V5
- Archive: `docs/checkpoints/V5_TERMINAL_RECORD.md`.
- Old terminal checkpoint `12898eb6590067d06ded7620eb86964bd9124c10`; final result commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`; final run `32919666736`.
- 1209 generated notes/events vs 946 reference notes; 891 generated onsets vs 603 reference playable onsets; 113 measures.
- PDF fidelity `1.0`; pitch-content professional F1 `0.2830626450116009`; pitch/timing tolerant F1 `0.044547563805104405`; string/fret/timing tolerant F1 `0.03062645011600928`; critical mismatches `1875`; `rhythmComplete=false`.
- Frozen raw stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; canonical scorer SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.

## Scorer + Modal/L4 preserved
- Manifest: `docs/testing/SCORER_MODAL_L4_ARCHIVE.md`.
- Preserve scorer/canonical/freeze/fidelity/completeness harness and V5 scorer evidence.
- Preserve branch `v143-github-modal-smoke`, `.github/workflows/v143-modal-live-smoke.yml` blob `11e8ab8cc9e34242a45442226c693a25fcb29b67`, and `analyzer/v143_modal_http_live_smoke.py` integration blob `ea3cd0bea0c9b43fc6a707f974c4d6d4a6925fc1`.
- L4 probe expects `modalGpu == "L4"`, deterministic seed `143`, Demucs shifts `1`, paired carrier stems, and two-view bend/legato consensus.
- Use L4 later only for a specific separation hypothesis or candidate verification.

## Calibration diagnostic V2 — COMPLETE
- `analyzer/v144_rhythm_calibration_diagnostics.py`; workflow `.github/workflows/v144-rhythm-calibration-diagnostic.yml`.
- V2 trigger `7e73de6e87649bc3a6e958117c5bda4b7f86139d`; run `32920648462` = SUCCESS.
- Report `debug/v144-rhythm-calibration/v5-diagnostic-baseline.json`, blob `d1a5fa3d1584c104c23ba46508ac967532cf9418`.
- Exact consumed structured source SHA-verified then deleted; only aggregate diagnostics persisted. No Modal/Production/candidate change.

## Confirmed failure class
- Pitch content ignoring timing: 644 matches, F1 `0.5976798143851508`.
- Pitch-class content ignoring octave: 867 matches, F1 `0.8046403712296984`.
- Exact string/fret/pitch content F1 `0.4677494199535963`.
- Exact onset positions: 360 matches, onset F1 `0.4819277108433735`.
- Major over-generation: 67 measures note-overgenerated; 74 measures onset-overgenerated; many events appear in calibration-reference-silent measures.
- Generated MIDI range `40-83` vs reference `40-71`; MIDI 64 over-produced by `+205` notes. Strong register/octave + contamination/voicing problem.
- **Do not apply a global timing shift.** Unique-onset offset search gives only tiny improvement and quarter-song offsets vary (`-12,+6,0,-8`). Same-measure pitch deltas are broad. Keep timing fixed for first V6 work.

## Original V2 evidence recovered exactly
- Authorized precursor run `32805316807` still has live artifact `9548666053`, name `v143-precision-v2-one-shot-32805316807`.
- Artifact ZIP SHA256 `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- It contains `repaired-timing-precision-candidate-product.json` SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951` (the pinned V5 baseline candidate SHA), plus replay policy/validation/capture-lock files.
- Candidate product carries complete `precisionReplayEvidence`: 984 eligible attacks, 725 originally retained, 259 originally pruned, all eligible attack keys, source-side `precisionStrength`, grid error, stem/sweep support, detection counts, and per-MIDI attack/early/sustain/paired-view evidence.
- This makes it possible to grade V5 baseline/rescue decisions against their original source-only evidence without reconstructing missing V3/V4 intermediate files.

## V5 source-evidence diagnostic — READY, NOT RUN YET
- Added `analyzer/v144_v5_source_evidence_diagnostics.py` commit `e8df18bca639c620e245214b88205fbe0379b4d9`.
- Added CPU workflow `.github/workflows/v144-v5-source-evidence-diagnostic.yml` commit `4e778b21b0a1a1f75ca3d5757ba9cfa0a6956b27`.
- Workflow pins the live V2 artifact ZIP SHA and candidate-product SHA, verifies terminal V5, fetches/SHA-verifies the consumed structured calibration source, grades V5 using original V2 source evidence, deletes transient V2/reference material, and persists aggregates only.
- Diagnostic reports attack precision/recall by baseline vs rescued class, evidence distributions for correct vs false onsets, cross-split source-only rule sweeps, per-pitch evidence distributions, V2 selected/primary provenance, and octave-confusion evidence.
- No candidate modification, no Modal, no Production.

## Next exact actions
1. Trigger `debug/v144-rhythm-calibration/run-v5-source-evidence-diagnostic.txt` once.
2. Inspect aggregate source-evidence report.
3. Choose the first conservative V6 attack/pitch rule only if it improves calibration on both odd/even internal splits and is expressible solely from source evidence.
4. Save checkpoint before generating any V6 candidate.
5. Build V6 as a separate candidate; do not mutate V5.
