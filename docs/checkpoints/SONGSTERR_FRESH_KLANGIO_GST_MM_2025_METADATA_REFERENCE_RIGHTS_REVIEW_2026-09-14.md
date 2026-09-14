# Songsterr Fresh V6 — Klangio GST-MM-2025 Metadata / Reference / Rights Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference-provenance review only. No candidate media access, no Basic Pitch, no V6 correctness.

## Candidate

Klangio `klangio-gst-mm-2025`, accompanying Sebastian Murgul, Johannes Schimper, and Michael Heizmann, “Joint Transcription of Acoustic Guitar Strumming Directions and Chords,” ISMIR 2025.

Primary surfaced repository: `Klangio/guitar-strumming-transcription`.

## Public evidence

The authoritative repository describes:

- 90 minutes of real-world acoustic-guitar recordings;
- microphone (`*_phone.wav`) and pickup (`*_line.wav`) audio;
- ESP32 smartwatch motion data (`*.csv`);
- strumming annotations (`*.strums`);
- three guitarists;
- a structured recording protocol;
- semi-automatic annotation combining **spectral-flux onset detection**, synchronized motion data, and the structured recording plan;
- chord and strumming-direction labels rather than an immutable per-performed-note MIDI/onset stream.

The repository license statement is explicitly for **software** under Apache-2.0. The public README does not establish an explicit permissive license for the real performance-audio dataset itself suitable for product validation.

## Frozen V6 pre-media gate assessment

### Gate 1 — explicit usable/permissive performance-audio rights

**FAIL / not established.**

The public repository exposes an Apache-2.0 software license, but that does not by itself license the real performance recordings. No separate explicit permissive performance-audio license was established in this metadata review.

### Gate 2 — real guitar

**PASS.**

The real subset is acoustic-guitar performance audio captured from microphone and pickup signals.

### Gate 3 — immutable independent performed note-level onset + pitch truth

**FAIL.**

Two independent reasons are sufficient:

1. The released supervision is strum-event / direction / chord labeling, not a discrete performed per-note onset + pitch/MIDI reference stream of the type required by the frozen V6 one-to-one note matcher.
2. The onset labels are described as semi-automatic and explicitly combine **spectral-flux onset detection from the recorded signal** with motion data and the recording plan. Therefore the timing reference is materially derived in part from evaluated audio rather than being an untouched independent performed note-event clock.

The structured chord plan cannot be substituted for performed per-note timing, and chord membership cannot be expanded into synthetic per-string/per-note truth without violating the frozen no-reconstruction rule.

### Gate 4 — plausible >=1,000 V6-positive capacity

**Not reached.**

Although 90 minutes of strumming likely contains many musical events, capacity cannot cure the failed reference-provenance/granularity gate.

### Gate 5 — defensible untouched status

**Not reached.**

No correctness or model-output inspection was performed. Untouched-history analysis is unnecessary once earlier hard gates fail.

## Binding decision

**REJECTED BEFORE MEDIA ACCESS — REFERENCE GRANULARITY + AUDIO-DERIVED ONSET + RIGHTS NOT ESTABLISHED.**

Do not download/acquire the real dataset for V6 admission, do not reconstruct per-note truth from chords/recording plans, and do not run Basic Pitch/V6 correctness on this candidate.

A future explicit dataset-audio license would not cure the reference failure. A materially different authoritative release would need to provide independent performed per-note onset + pitch identity captured without deriving the reference timing from evaluated audio before this candidate could be reconsidered.

## Governance impact

None. Frozen V6 constants, Basic Pitch settings, matcher, tolerances, admission gates, deferred-reveal rule, and fail-closed production authority remain unchanged.

`modelValidationComplete:false`
`customerEligibleEvents:0`
`mayAdvanceDelivery:false`
Duration remains paused/unchanged.
Policy C remains `UNENROLLED`.
Protected-song execution remains embargoed.
