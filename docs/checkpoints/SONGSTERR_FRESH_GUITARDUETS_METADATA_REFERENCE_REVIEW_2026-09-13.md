# Songsterr Fresh V6 — GuitarDuets Metadata / Reference Review

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/reference screening only; no corpus media access and no Basic Pitch/V6 correctness.

## Candidate

GuitarDuets, Zenodo record `12802440`, introduced for classical-guitar duet source separation.

Public release description reports approximately three hours of combined real and synthesized classical-guitar duet recordings. The real recordings used four classical guitars, condenser microphones, and include a leakage-free test subset. The released description explicitly states that **note-level MIDI annotations are provided for the synthesized duets**.

The associated paper likewise describes the dataset as containing real and synthesized guitar recordings with note-level annotations for the synthesized subset.

## V6 reference-provenance decision

**REJECT / NOT AUDIT-READY FOR V6 ADMISSION.**

The frozen V6 external scorer requires a real-guitar holdout with immutable performed note-level onset+pitch truth independent of the evaluated audio. GuitarDuets does not establish such truth for its real-performance subset. MIDI labels attached only to synthesized performances cannot be substituted for real-guitar performed truth, and the synthetic subset is not an acceptable replacement for the required real-guitar external holdout.

No attempt may be made to manufacture reference truth for the real recordings via transcription, onset detection, score alignment, source separation, or model output.

## Rights

The Zenodo record is openly accessible, but rights do not need to be adjudicated further for V6 admission because the independent real-performance note-reference gate already fails. Open access alone is not treated as a license grant.

## Disposition

- Do not download GuitarDuets for V6 admission.
- Do not run Basic Pitch or V6 correctness on it.
- Do not count synthesized-MIDI events toward the real-guitar external holdout gate.
- Reconsider only if the authors release an authoritative real-performance note-level onset+pitch reference that is independent of evaluated audio, with suitable rights; then untouched-history screening would still be required before media access.

## Authority

No frozen V6 method/scoring setting changes. `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration unchanged/paused, Policy C `UNENROLLED`, protected song embargoed.
