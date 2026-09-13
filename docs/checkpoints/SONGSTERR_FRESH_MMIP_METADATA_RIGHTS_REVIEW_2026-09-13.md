# Songsterr Fresh V6 — MMIP Metadata / Rights / Reference Review

Status: **REJECTED BEFORE MEDIA ACCESS OR CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Candidate

Multi-Modal Instrument Performances (MMIP), Kyriakou, Aristidou, Charalambous, 2025.

Public project/dataset site: `https://mmip.cs.ucy.ac.cy`
Paper DOI: `10.1111/cgf.70025`.

## Why it was investigated

Public materials describe a real multimodal musical-performance corpus containing synchronized audio, video, motion capture and MIDI for guitar, piano and drums. The paper calls MIDI performance ground truth and describes note pitch/onset/timing information, making MMIP initially appear relevant to the frozen V6 external-scoring matcher.

No MMIP media was downloaded and no Basic Pitch/V6 correctness was run.

## Rights gate

The authoritative MMIP dataset license page states that all repository content is released under **CC BY-NC-SA 4.0** and permits noncommercial use only. It separately instructs users to contact the authors for commercial licensing.

This does not provide the explicit permissive commercial-use dataset-audio rights required for the Songsterr V6 product-validation holdout path.

Rights disposition: **FAIL / not admissible under current public license**.

## Reference-semantics gate

The associated MMIP paper states that piano and drum MIDI can be exported directly from digital instruments, but this is not the case for guitar. For guitar performances, MMIP created the MIDI using **Ableton audio-to-MIDI conversion software** from the recorded audio.

Therefore the guitar MIDI is a detector/transcription-derived representation of the same audio being evaluated, not an independent immutable performed note-level ground-truth stream captured from the performer/instrument.

The frozen V6 protocol does not permit manufacturing reference truth from audio detectors or model output. A derived guitar MIDI track cannot be promoted to independent reference truth merely because the paper describes the corpus MIDI generally as ground truth.

Reference disposition: **FAIL / unsuitable reference provenance for frozen V6 matching**.

## Decision

MMIP is **REJECTED as a V6 admission holdout candidate** before any media access or correctness.

Do not:
- download/audit MMIP for V6 admission under current terms;
- use its guitar Ableton audio-to-MIDI output as immutable reference truth;
- replace that derived MIDI with another onset/pitch detector;
- tune or alter V6/scoring rules to accommodate MMIP;
- use piano/drum portions as substitutes for the required real-guitar holdout.

MMIP could only be reconsidered if both independent issues were resolved prospectively: (1) explicit commercially permissive dataset rights or rights-holder permission, and (2) an authoritative independent performed guitar note onset+pitch reference stream not derived from the evaluated audio. Even then, untouched-history screening would be required before media access.

## Policy boundary

No candidate media accessed.
No Basic Pitch invoked.
No V6 invoked.
No correctness computed.
No protected song used.
No duration authority changed.
`modelValidationComplete:false`.
`customerEligibleEvents:0`.
`mayAdvanceDelivery:false`.
Policy C remains `UNENROLLED`.
Production remains unchanged.
