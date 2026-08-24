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
- Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Reuse cryptographically bound prior outputs/evidence instead.

## Last scored result
- 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- professional score run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- scorer/reference is closed again.

## Proven promoted-harmonic defect/fix
- 144 fundamental promotions; all 144 also rendered the strongest raw pitch.
- 96/144 strongest pitches are upper harmonic-family intervals: +12=78, +19=11, +24=6, +28=1.
- minimal reference-free guard is green: attack identity unchanged, primary unchanged, exactly 96 contradictory strongest harmonics suppressed.
- helper commit `588b314c3103ffbea8a0a933351562551750f670`; integration `534be3fec36cf5ec4a87089b1298becb4933693d`.
- offline projection proof `debug/v143-contextual-prune/harmonic-guard-offline-projection-proof.json` reproduces old 985-event SHA and projects 889 notes / SHA `50aa17f6855a816ce73f8b427062e8c24c5ce0a5751c7b6425e79c6cea89ecca`, but explicitly says `simulationAcceptedAsCandidate=false`.

## Modal timeout / quota boundary
- one-shot corrected candidate did reach Modal but hit its 1800s timeout; do not retrigger.
- exact successful run `32697939613` proves the frozen stage hashes:
  - normalized WAV `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
  - direct guitar `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
  - cascade guitar `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`
  - carrier grid `ccedc78898c84d86099f912a18605d72ae52b5d14c66bf35a1878f0c91f81b83`
  - carrier rows `b308a052c5c0e42091db242815227b8963fc62408548650d8f0f27a49e9cf498`
  - precision events `a418118222079a423b4319c7362867c13710620e506f5b211d73e974015392cc`
  - precision pitch sets `4a986b255002fe2fce2e1a74df73b9b2ed73ebea9a611a857779ccbcbba839e9`
  - precision primaries `bd08caf874fc3afd969cadc1595f87f1fb68a539bf1ff9af2977f976bf46a6a8`
- successful run resource split: deterministic CPU Demucs (~7m42), GPU BS-RoFormer (~47s), deterministic CPU cascade Demucs (~7m17), then downstream CPU analysis; full pass ~18m26.
- exact proof artifacts for `32697939613` contain JSON reports, not WAV stem bytes.
- direct Demucs is already cross-host byte-exact on CPU, so it need not consume L4.
- staged CPU→L4→CPU recovery preflight is green but is now SEALED; do not trigger it under the quota boundary.

## CRITICAL RECOVERY: rich pre-scorer historical product artifact FOUND
Source preholdout run: `32702772593`.
Artifact: `rhythm-professional-preholdout-real-audio`, artifact ID `9511117529`, artifact digest `fe16e937bae1c4af9f52b0d7863846c9a8da4da91be0af03256947bc2f5deaf4`.
Downloaded artifact contains:
- `.preholdout/raw-product-output.json`
- `.preholdout/rhythm-freeze-input.json`
- frozen analysis/manifest/PDF fidelity proofs
- full + preview frozen PDFs
- binding/runtime-isolation logs
- `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json`

The artifact summary itself proves:
- source audio SHA exact `215bd5...`
- reference-free=true; professionalReferenceUsed=false; referenceRuntimeInputUsed=false; runtimeLabelsRequired=false
- candidate result commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`, candidate blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`
- selectedAttackCount=725, renderNoteCount=985, all 113 measures
- frozen/pdf event SHA exactly retired `a81190...`, PDF fidelity 1.0
- human reference was still sealed and no professional score had run at this stage.

`raw-product-output.json` is therefore the best available immutable **pre-scorer, approved-audio, reference-free frozen upstream evidence** for no-Modal correction/testing. It has all 985 rich product events including physical onset provenance, explicit primary, per-pitch physical CQT support, string/fret mapping, bend/legato evidence, sustain evidence and candidate/timing diagnostics.

## New equivalence audit — deletion-only projection is NOT sufficient
Using the recovered raw product and the current deterministic chord voicing algorithm:
- serialized physical evidence independently re-identifies exactly the same 96 promoted-harmonic suppressions and interval distribution.
- after suppressing those 96 pitch-set members and rerunning the exact candidate voicing rule, the selected MIDI sets equal `old rendered MIDI set - suppressed harmonic` at all 725 attacks (no surprise/additional pitch changes).
- HOWEVER **48 surviving notes change legal string/fret mapping** when the contradictory harmonic is removed.
- Example: measure 1 step 14 old `{57,69}` maps MIDI57 to D-string fret7; after suppressing MIDI69, MIDI57 legally remaps to G-string fret2.
- therefore merely deleting 96 final events (the earlier 889-event offline projection) is useful evidence but is not semantically identical to running the guard before candidate assembly.

This matters because downstream legato and sustain passes use same-string event topology. We must rebuild/remap the 889-note candidate conservatively from the serialized pre-scorer evidence rather than relabel the deletion-only simulation.

## Safe no-Modal reconstruction direction
1. Bind input to artifact ID/digest, candidate commit/blob, approved source SHA, old retired event SHA and historical stage hashes.
2. Apply the exact guard from serialized physical pitch evidence; require exactly 96 suppressions and unchanged 725 attack keys/primaries.
3. Rerun the exact deterministic joint chord voicing from guarded pitch sets. Update noteMapping/chord indexes/counts/string/fret. Require exactly 889 notes and no unobserved pitch/attack.
4. Bend evidence is pitch/time based; for a surviving remapped primary it may be retained only with `bendTargetFret` recomputed from the new fret. Secondary audio semantics remain prohibited.
5. Legato is topology-dependent. Retain an old evidence-backed primary→primary link only if both endpoints survive and remain a valid same-string adjacent pair under the new mapping; remap event indices. Strip invalidated links. **Do not invent newly possible legato links without stem evidence.**
6. Sustain is also topology-dependent. Reuse historical two-view sustain evidence only conservatively: never lengthen it; clamp to any earlier new same-string hard end and requantize. If remapping creates more space, keep the old shorter supported duration.
7. Re-run the event-only semantic guard and sustain promotion, then render/freeze/PDF using normal CPU gates.
8. This rebuilt product must have a new product/render identity and explicitly declare historical frozen-upstream reuse; it is not a fresh separator inference.
9. Only after binding + PDF fidelity 1.0 may exactly one professional score run.

## Downstream prepared
- CPU candidate post-proof: `.github/workflows/v143-harmonic-guard-candidate-postproof.yml` commit `5d7e96c38c8328457bd82aeeb691245a66ffed00`.
- fail-closed preholdout: `.github/workflows/v143-harmonic-guard-final-preholdout.yml` commit `12958a2f5f245697148a7fba190dd7bb8e98987c`; marker NOT created.

## Next exact actions
1. Build a CPU-only reconstruction checker against the recovered artifact evidence with the conservative remap/legato/sustain rules above.
2. Prove its invariants locally/CPU-only: exact provenance, 96 suppressions, 725 attacks, 889 notes, no new pitch/attack, correct remapping, no unsupported semantic links, protected blob exact, anti-leakage green.
3. Persist the minimum immutable historical evidence needed so Actions does not depend on artifact retention.
4. Create a new corrected candidate identity from that evidence; run existing binding/preholdout freeze/PDF gates without Modal.
5. Keep scorer sealed until new PDF fidelity = 1.0 and all fail-closed gates pass.
