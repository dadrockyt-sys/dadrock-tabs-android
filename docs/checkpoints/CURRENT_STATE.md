# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference is scorer-only; runtime/shadows may never read/train/tune/select from it.
- Retired scored render SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rerun/rescored.
- Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete until the new locked candidate is scored.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Current corrected path uses frozen approved-audio evidence and CPU-only downstream reconstruction.

## Last retired professional score
- Retired candidate: 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- professional score run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- retired render identity: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`.

## Proven promoted-harmonic defect/fix
- 144 fundamental promotions; all 144 also rendered the strongest raw pitch.
- 96/144 strongest pitches are upper harmonic-family intervals: +12=78, +19=11, +24=6, +28=1.
- minimal reference-free guard is green: attack identity unchanged, primary unchanged, exactly 96 contradictory strongest harmonics suppressed.
- helper commit `588b314c3103ffbea8a0a933351562551750f670`; integration `534be3fec36cf5ec4a87089b1298becb4933693d`.
- earlier deletion-only projection proof projected 889 notes but was explicitly simulation-only and insufficient because 48 surviving notes require different legal string/fret mappings.

## Modal timeout / quota boundary
- one-shot corrected candidate reached Modal but hit its 1800s timeout; do not retrigger.
- exact successful historical run `32697939613` proved frozen separator/evidence identities, including normalized WAV `ab64e7c...`, direct guitar `0ac47da...`, cascade guitar `546e517...`, carrier grid `ccedc788...`, carrier rows `b308a052...`, precision events `a4181182...`, pitch sets `4a986b25...`, primaries `bd08caf8...`.
- staged CPU→L4→CPU recovery remains sealed under the user quota boundary.

## Rich pre-scorer historical evidence — recovered and persisted
Source preholdout run: `32702772593`.
Artifact: `rhythm-professional-preholdout-real-audio`, artifact ID `9511117529`, digest `fe16e937bae1c4af9f52b0d7863846c9a8da4da91be0af03256947bc2f5deaf4`.
The artifact predates professional scoring and proves approved source SHA, reference-free runtime, 725 attacks, 985 old rendered notes, all 113 measures, retired event SHA and PDF fidelity 1.0.
The recovered raw product is now represented by the persisted immutable evidence path used by the CPU reconstruction, so Actions no longer depends on artifact retention.

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
- 48 surviving notes deterministically remapped to the legal voicing produced after suppression
- historical legato links: 28 total, 27 retained evidence-backed links, 1 invalidated link stripped, no new legato invented
- 13 sustain values conservatively clamped because corrected same-string topology creates earlier hard ends; no sustain is lengthened
- corrected canonical render identity: `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- reconstruction proof `passed=true`; Production unchanged; protected runtime unchanged.

## CPU frozen-evidence preholdout — PASSED
Workflow: `V143 Frozen Evidence Harmonic Guard Pre-Holdout`
Trigger commit: `315f9525ff747f2b42e5020c9579713f5f962d7b`
Workflow run: `32751771832`
Proof: `debug/v143-contextual-prune/harmonic-guard-frozen-evidence-preholdout-proof.json`

Exact result:
- `passed=true`
- all 10 fail-closed checks true; `failedChecks=[]`
- `eventCount=889`
- `uniqueMeasureCount=113`
- frozen event SHA `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- PDF event SHA exact same `07b12f...`
- `pdfEventFidelity=1.0`
- renderer projection exact
- brand-new frozen identity true and not any retired identity
- approved source hash exact
- source commit exact
- reference remained sealed (`referenceOpened=false`)
- `professionalScoreRun=false`
- `modalUsed=false`
- `productionModified=false`
- one-shot trigger marker was consumed/removed by the successful workflow.

## Professional score authorization — PREPARED
- User explicitly authorized the single professional holdout score for the new locked identity.
- New fail-closed workflow: `.github/workflows/v143-frozen-evidence-harmonic-guard-professional-score.yml`, creation commit `bfda89db6dc9fbc9b5bb27d977c0db704607d35d`.
- It binds preholdout run `32751771832`, corrected SHA `07b12f...`, 889 events, 113 measures, PDF fidelity 1.0, protected runtime blob and approved source hash before any reference access.
- It creates and pushes a permanent score-authorization lease before opening the professional source, so an accidental duplicate score is refused.
- It uses the same immutable scorer-only professional structured source/revision and unchanged `0.99` scorer as the prior holdout.
- It contains no Modal/L4 step and does not authorize Production.
- Score trigger marker has NOT yet been created at this checkpoint.

## Current gate state
The corrected no-Modal candidate is frozen/PDF-locked with exact PDF-event fidelity 1.0 and a genuinely new immutable render identity. All preholdout requirements are satisfied, and the one-shot scorer workflow is prepared but not yet triggered at this checkpoint.

## Next exact action
Create `debug/v143-contextual-prune/RUN_FROZEN_EVIDENCE_HARMONIC_GUARD_SCORE_ONCE` once to trigger the professional score. Observe exactly one result, close the scorer/reference, save the diagnostic, and evaluate completion against score >= 0.99, critical mismatches 0, PDF-event fidelity 1.0. Never rerun any retired identity.
