# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
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
1. Resume reference-free diagnosis from the persisted approved-audio evidence. Prioritize the dominant unresolved problems: musical grid/timing identity and broad pitch identity, not coverage.
2. Use CPU-only tests against physical onset/CQT/carrier evidence and deterministic reconstruction. No Modal and no scorer/reference.
3. Look for a general audio-only correction that materially changes timing/pitch identity rather than merely suppressing a small subset of notes.
4. Prove any proposed correction on reference-free invariants and create a genuinely new corrected render identity.
5. Only after new freeze/PDF fidelity 1.0 and fail-closed lock may another professional score be considered.
