# Songsterr Fresh V6 — M-M Guitar / Perez-Carrillo Multimodal Guitar Metadata + Reference Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/reference-provenance review only; no corpus media acquired; no Basic Pitch/V6 correctness exposed.

## Candidate

The older Perez-Carrillo multimodal guitar corpus (also described in later surveys as “Multi-modal Guitar” / “M-M Guitar”) contains approximately ten monophonic classical-guitar fragments, each around one minute, performed by two guitarists with synchronized audio and motion capture.

Primary methodology source:
- Alfonso Perez-Carrillo, Josep-Lluis Arcos, Marcelo M. Wanderley, *Estimation of Guitar Fingering and Plucking Controls based on Multimodal Analysis of Motion, Audio and Musical Score* (CMMR 2015).
- Follow-up methodological description: Alfonso Perez-Carrillo, *Finger-String Interaction Analysis in Guitar Playing With Optical Motion Capture*, Frontiers in Computer Science (2019).

Later survey source:
- *Virtual Instrument Performances (VIP): A Comprehensive Review* (Computer Graphics Forum, 2024), which lists the corpus as ten guitar samples / about ten minutes and notes audio, score/detail and motion modalities.

## Frozen V6 gate assessment

### Gate 2 — real guitar

PASS in principle. The corpus is based on performances by real guitarists recorded with a guitar-body transducer and optical motion capture.

### Gate 3 — immutable independent performed onset + pitch truth

FAIL.

The primary method explicitly states that the low-level controls used to derive guitar-event parameters combine:
- note onsets detected by **audio analysis**;
- pitch extracted from the **musical score**;
- finger/string geometry derived from motion capture.

The 2019 follow-up is equally explicit: “From the audio signal we extract the pitch and the onsets,” and these quantities are then used to determine plucking instants/string/fret and downstream interaction features.

Therefore the performed-note timing is materially reconstructed from the evaluated recording itself rather than emitted by an independent physical note-event sensor. This violates the frozen V6 independence gate. Score pitch does not cure onset provenance.

### Gate 4 — plausible >=1,000 V6-positive capacity

FAIL / independently insufficient. The later survey reports only ten excerpts totaling roughly ten minutes. Even before correctness, this is not a defensible replacement for the required multi-player/category external holdout capacity under the frozen framework.

### Gate 1 — usable/permissive performance-audio rights

NOT ESTABLISHED from the surfaced authoritative sources. The 2025 MMIP review specifically describes the older M-M Guitar corpus as not publicly available. No authoritative permissive product-validation license for the performance audio was surfaced in this review.

### Gate 5 — untouched status

Not evaluated further because gates 1, 3 and 4 already fail before media access.

## Binding decision

**REJECTED BEFORE MEDIA ACCESS — AUDIO-DERIVED PERFORMANCE ONSETS + INSUFFICIENT POPULATION + RIGHTS/AVAILABILITY NOT ESTABLISHED.**

This candidate must not proceed to reference-blind inventory/alignment, Basic Pitch, V6 scoring, correctness, or any rescue based on manually repairing/aligning its event stream.

No frozen V6 constants, Basic Pitch settings, matcher, tolerances, admission gates, strata, uncertainty treatment or deferred-reveal/single-run rules were changed.

## Authority unchanged

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
- Guitar-TECHS remains closed at decision C before correctness
- no Modal, Vercel heavy-GPU or L4 GPU used
