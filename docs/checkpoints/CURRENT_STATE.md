# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 14:28 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference is scorer-only; runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future score requires a genuinely new approved-audio/frozen-evidence corrected candidate identity → immutable freeze/PDF → lock → exactly one professional score.
- Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Continue with cryptographically bound historical evidence and CPU-only/reference-free development.

## First retired professional score
- Candidate: 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- score run `32731885778`:
  - measure coverage recall `1.0`
  - pitch-content F1 `0.23718280683583634`
  - pitch+timing tolerant F1 `0.033143448990160536`
  - critical mismatches `1723`
- retired render identity `a81190...`.

## Proven promoted-harmonic defect/fix
- 144 fundamental promotions; all 144 also rendered the strongest raw pitch.
- 96/144 strongest pitches are upper harmonic-family intervals: +12=78, +19=11, +24=6, +28=1.
- minimal reference-free guard is green: attack identity unchanged, primary unchanged, exactly 96 contradictory strongest harmonics suppressed.
- helper commit `588b314c3103ffbea8a0a933351562551750f670`; integration `534be3fec36cf5ec4a87089b1298becb4933693d`.
- deletion-only projection was insufficient because 48 surviving notes require different legal string/fret mappings after suppression.

## Modal timeout / quota boundary
- one-shot corrected candidate reached Modal but hit its 1800s timeout; do not retrigger.
- exact successful historical run `32697939613` proved frozen separator/evidence identities, including normalized WAV `ab64e7c...`, direct guitar `0ac47da...`, cascade guitar `546e517...`, carrier grid `ccedc788...`, carrier rows `b308a052...`, precision events `a4181182...`, pitch sets `4a986b25...`, primaries `bd08caf8...`.
- staged CPU→L4→CPU recovery remains sealed under the user quota boundary.

## Rich pre-scorer historical evidence — recovered and persisted
Source preholdout run: `32702772593`.
Artifact: `rhythm-professional-preholdout-real-audio`, artifact ID `9511117529`, digest `fe16e937bae1c4af9f52b0d7863846c9a8da4da91be0af03256947bc2f5deaf4`.
The artifact predates professional scoring and proves approved source SHA, reference-free runtime, 725 attacks, 985 old rendered notes, all 113 measures, retired event SHA and PDF fidelity 1.0.
The recovered raw product is represented by the persisted immutable evidence path used by the CPU reconstruction, so Actions no longer depends on artifact retention.

## CPU-only corrected reconstruction — GREEN
Files:
- `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`
- `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-corrected-render.json`
- `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-reconstruction-proof.json`

Proven reconstruction facts:
- source audio SHA exact `215bd5...`
- professionalReferenceUsed=false; referenceRuntimeInputUsed=false; runtimeLabelsRequired=false
- freshSeparatorInference=false; historicalFrozenUpstreamReused=true; modalUsed=false
- exactly 96 promoted harmonic duplicates suppressed
- 725 attack identities preserved
- 889 corrected render notes
- 48 surviving notes deterministically remapped after suppression
- historical legato links: 28 total, 27 retained evidence-backed links, 1 invalidated link stripped, no new legato invented
- 13 sustain values conservatively clamped; no sustain lengthened
- corrected canonical render identity `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- reconstruction proof passed; Production and protected runtime unchanged.

## CPU frozen-evidence preholdout — PASSED
Workflow run `32751771832`.
Proof: `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-preholdout-proof.json`.
- `passed=true`, no failed checks
- 889 events / 113 measures
- frozen/PDF event SHA exact `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- PDF-event fidelity `1.0`
- renderer projection exact
- reference remained sealed
- no Modal and no Production modification.

## SECOND PROFESSIONAL SCORE — COMPLETED, FAILED 0.99
One-shot scorer workflow: `.github/workflows/v143-frozen-evidence-harmonic-guard-professional-score.yml`.
Trigger SHA `b1014ef35607987b0767d856919a39468d244b3f`.
Score run `32752374788`, attempt 1.
Diagnostic: `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-professional-score.json`.
Permanent authorization lease: `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-professional-score-lease.json`, state `score-completed`; trigger marker consumed/removed. Duplicate score is fail-closed.

Exact score result:
- frozen/PDF identity `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- PDF-event fidelity `1.0`
- generated notes `889`; reference notes `946`
- measure coverage recall `1.0`; no missing reference measures
- pitch-content F1 `0.24305177111716622`
- pitch+timing tolerant F1 `0.03051771117166212`
- string/fret+timing tolerant F1 `0.01852861035422343`
- chord pitch-set tolerant F1 `0.012048192771084336`
- exact voicing tolerant F1 `0.012048192771084336`
- gross unmatched generated notes `789`
- gross unmatched reference notes `846`
- critical mismatches `1635`
- near-100 professional gate `false`
- `rhythmComplete=false`
- scorer return code `2`
- reference completeness passed; reference opened only after freeze validation
- professional reference was not used by analyzer/runtime; reference payload was not committed
- protected pipeline unchanged
- Modal unused; Production unchanged and promotion unauthorized.

### Aggregate comparison to first scored freeze
- coverage remains solved at `1.0`.
- pitch-content F1 improved slightly: `0.2371828068` → `0.2430517711`.
- critical mismatches improved: `1723` → `1635` (88 fewer).
- pitch+timing F1 did not improve: `0.0331434490` → `0.0305177112`.
- Therefore the promoted-harmonic contradiction was real and worth correcting, but it is not the dominant remaining failure. Grid/timing identity and broad pitch identity remain fundamentally wrong.

## Scorer/reference state — CLOSED AGAIN
- The professional scorer/reference is closed after run `32752374788`.
- Do NOT inspect/tune against per-event professional mismatches and do NOT rescore `07b12f...`.
- Only aggregate score results above may guide high-level diagnosis.
- Any next correction must be justified independently from reference-free audio/evidence, produce a brand-new immutable scored identity, and pass fresh CPU binding/freeze/PDF gates before another one-shot score.

## Next exact actions
1. Continue reference-free broad pitch/register diagnosis from the persisted approved-audio evidence; simple global phase and BPM fixes are now rejected.
2. Quantify octave/register ambiguity, adjacent-primary jump behavior, physical string/register plausibility, and whether context-supported octave folding would improve continuity without consulting labels/reference.
3. Keep retrigger suppression secondary: 176 short same-primary repeat pairs exist, but only 14 weak carryover suspects and 0 strict weak-front/strong-body suspects under the current physical test.
4. Only after a general audio-only correction is independently justified should a genuinely new corrected render identity be created and frozen.
5. Only after new freeze/PDF fidelity 1.0 and fail-closed lock may another professional score be considered.

## Resume log — 2026-08-24 11:45 America/Thunder_Bay
- Reopened branch `v143-contextual-prune-lobo`; head at resume was `079d274c2cb132d942c331890949c93b44320eff` (`Checkpoint frozen-evidence professional score result`).
- Re-read this checkpoint and reaffirmed all hard boundaries, especially **CPU-only/reference-free work and no Modal/L4**.
- Immediate work resumed on dominant unresolved grid/timing and broad-pitch diagnosis from persisted approved-audio evidence; scorer/reference remains closed.

## Reference-free diagnosis — 2026-08-24 13:44 America/Montreal
- Recovered the exact prior approved-shadow physical-review implementation from its persisted source blobs (`c8025ee99596354d731628b57e42f69e0ca39c10` review logic; `e2facac5a63d49af05bd85f4bcf05625113284cf` checker).
- Confirmed the old physical review was deliberately constrained to `attackTimingChanged=false`, `candidateRelocatesEvents=false`, and preservation of all base events. It therefore **could not diagnose or repair sustained-note retriggers / wrong attack-grid identity**.
- The historical harmonic-guard reconstruction likewise has a fail-closed invariant that preserves all 725 attack keys. That was appropriate for the retired harmonic-only correction, but must not constrain the next genuinely new candidate.
- Next reference-free diagnostic is therefore separated from the protected runtime: classify whether a selected attack is a real new pick versus continued carrier/sustain energy, using only persisted pre-scorer onset/carrier/pitch evidence. Confident repicks must be preserved; only weak-new-onset + strong-carryover cases may be proposed as retrigger suppressions.
- In parallel, broad pitch diagnosis will evaluate fundamental-vs-harmonic-family support from attack/body evidence rather than strongest-bin-only selection.
- No scorer/reference opened, no Modal/L4 used, protected pipeline unchanged, Production untouched.

## Attack-physics / bar-phase diagnostic — 2026-08-24 14:05 America/Montreal
- Synced to newer branch head `8137b0b5a180fe0e9e04c6a4823b55cebdbbcb3c` before making any new change; it records `debug/v143-contextual-prune/frozen-evidence-attack-physics-diagnostic.json` and `analyzer/v143_frozen_evidence_attack_physics_diagnostic.py`.
- The diagnostic remains fully reference-free/CPU-only and mutates no events.
- Global lag recurrence metrics are effectively phase-rotation insensitive apart from edge effects, so their split winners at offsets 4/8/12 are not sufficient evidence for a bar-boundary correction.
- Physical primary-attack support is materially different: the strongest whole-beat phase candidate is offset **8 sixteenth steps** from the current boundary (a half-bar shift). This is now a source-level clue, but **not yet a correction**.
- Next action: test 0-vs-8 attack-support contrast across contiguous local windows / musical sections with edge-safe aggregation, robust median and sign-vote statistics. Only if the half-bar signal is stable across the piece will measure-origin mapping be inspected for a global phase defect; if it is sectional, inspect pickup/local reset behavior instead.
- Scorer/reference remains closed. Modal/L4 remains closed. Protected runtime and Production remain untouched.

## Edge-safe phase stability diagnostic — 2026-08-24 14:19 America/Montreal
- Added `analyzer/v143_frozen_evidence_phase_stability_diagnostic.py` and CPU-only workflow `.github/workflows/v143-frozen-evidence-phase-stability-diagnostic.yml`; no candidate generation, Modal, scorer, runtime edit, or Production edit is permitted by the diagnostic.
- Persisted report: `debug/v143-contextual-prune/frozen-evidence-phase-stability-diagnostic.json`.
- The stricter method compares every phase on the **same current-measure set**, rotates whole-beat positions modulo 16, zero-fills missing attacks, and reports occupied-only means separately. This removes the leading/trailing truncation and occupancy-conditioning weaknesses in the earlier phase clue.
- Global zero-filled physical-accent ranking still places offset 8 first: offset-8 contrast `0.1768629263` versus offset-0 `0.1011387611`; difference `+0.0757241652`. Occupied-only contrast also favors offset 8 (`0.4863533122` versus `-0.0474636840`).
- However the signal is **not stable across the piece**:
  - paired measure-by-measure step-8 minus step-0 support: phase 8 wins 47, phase 0 wins 41, ties 25; median difference `0.0`; non-tie phase-8 win fraction `0.5341`.
  - non-overlapping 8-measure windows: phase 8 wins 7 vs phase 0 wins 7; median contrast difference `+0.1116815`.
  - 16-measure windows at 8-measure stride: phase 8 wins 6 vs phase 0 wins 7; median contrast difference `-0.1065373`.
  - diagnostic classification: `sectional-or-mixed-phase-accent-clue`; `stablePhase8PhysicalAccentClue=false`.
- Therefore **reject a global half-bar shift correction**. The apparent global offset-8 advantage is a sectional/arrangement clue, not evidence for moving every measure origin.
- Scorer/reference remains closed. Modal/L4 remains closed. Protected runtime and Production remain untouched.

## Sectional phase / fine-phase diagnostic — 2026-08-24 14:23 America/Montreal
- Added `analyzer/v143_frozen_evidence_phase_section_diagnostic.py` and CPU-only workflow `.github/workflows/v143-frozen-evidence-phase-section-diagnostic.yml`; persisted `debug/v143-contextual-prune/frozen-evidence-phase-section-diagnostic.json`.
- 8-measure coarse whole-beat phase runs are strongly sectional: measures 1–32→8, 33–40→0, 41–64→8, 65–72→4, 73–112→12.
- Coarse transitions occur near measures 33, 41, 65, and 73, but they are not consistent with one simple grid reset. At measure 73 the coarse winner jumps 4→12 while the unrestricted fine-phase winner remains 13→13, proving that at least one apparent coarse transition is only a change inside the restricted 0/4/8/12 view.
- The unrestricted 4-measure phase winner is highly volatile: 24 changes across 27 consecutive windows; 12 changes are >=4 sixteenth steps, only 9 are 1–2 steps, and only `0.375` of changes are small among changed windows.
- This volatility is incompatible with using physical attack accent as a smooth global tempo-drift estimator. It is much more consistent with arrangement/accent changes and local phrase structure.
- Therefore reject attack-accent phase as the basis for a timing mutation. Keep phase only as descriptive reference-free section evidence.

## Grid timestamp consistency diagnostic — 2026-08-24 14:28 America/Montreal
- Added `analyzer/v143_frozen_evidence_grid_timestamp_diagnostic.py` and CPU-only workflow `.github/workflows/v143-frozen-evidence-grid-timestamp-diagnostic.yml`; persisted `debug/v143-contextual-prune/frozen-evidence-grid-timestamp-diagnostic.json`.
- A simple global BPM error is **not** present: frozen metadata BPM is `129.19921875`; global timestamp-vs-labeled-step fit implies `129.2881694947`, only `+0.06885%` different.
- Nevertheless the timestamp/grid relationship is strongly nonuniform: nominal-tempo residuals span `7.375` labeled sixteenth steps, and even the best global linear fit leaves a `7.965`-step residual span.
- Local 8-measure fits vary materially: approximately `125.33–131.63 BPM`. Window median residuals versus the nominal grid move from `-3.625` steps (m1–8), through near zero in the middle, to `+1.825` (m49–56), and back to `-3.225` (m105–112).
- The residual trend is not monotonic (`correlation=-0.1607`), so this is **not** a simple cumulative tempo drift that a single BPM replacement would fix.
- Adjacent selected attack pairs still center exactly on the metadata grid (713 pairs, median implied BPM `129.19921875`), while the tails are broad. This is consistent with locally varying/piecewise grid timing rather than one globally wrong tempo.
- Combined timing conclusion: reject both a global half-bar origin shift and a global BPM replacement. Any future timing correction must model local grid timing/warping from reference-free physical evidence; no timing mutation is yet justified.
- Immediate work pivots to the other dominant unsolved axis: broad pitch/register identity. The existing harmonic guard corrected contradictory duplicated upper harmonics but deliberately preserved every primary, so primary octave/register errors remain untested.
- Scorer/reference remains closed. Modal/L4 remains closed. Protected runtime and Production remain untouched.
