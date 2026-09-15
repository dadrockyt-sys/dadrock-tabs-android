# Songsterr Fresh V6 — EG-Solo Pre-Media Rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: V6 replacement-holdout metadata/license/alignment search only

## Binding context

The frozen V6 method remains `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`; frozen implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. Frozen external scoring framework remains `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS reference-blind alignment/inventory run `34754519541`, job `103716527380`, was re-inspected before this search and remains `completed/success`. Its immutable audit decision remains **C**; Guitar-TECHS correctness remains prohibited.

## Candidate screened

Candidate: **EG-Solo** (electric-guitar solo note/technique transcription dataset).

Public project metadata describes 76 clips / about 40 minutes drawn from professional electric-guitar solo demonstration videos available on YouTube, with polyphonic backing tracks. It reports 6,833 note annotations plus technique/phrase annotations in MIDI-track format.

Authoritative/public project page inspected:
- `https://bryanyu1997.github.io/EG-Solo_demo/`

## Frozen-gate assessment

EG-Solo does not satisfy the frozen V6 isolated-guitar DI audio-path requirement:

- source performances are YouTube demonstration videos rather than an established isolated direct-input guitar capture;
- the described clips explicitly contain polyphonic backing tracks;
- therefore the evaluation audio is not an untouched isolated-guitar DI holdout compatible with the preregistered V6 audio path.

The presence of MIDI note labels cannot cure the audio-path failure. Admitting this corpus would require changing the frozen admission/audio-path rules after candidate observation, which is forbidden.

## Decision

**REJECT BEFORE MEDIA ACCESS.**

No EG-Solo audio/video payload, MIDI/reference payload, or annotation files were downloaded or opened. No Basic Pitch inference, V6 correctness scoring, matcher execution, threshold/tolerance change, alignment-method change, or deferred-reveal correctness run occurred.

No Modal run, Vercel heavy-GPU run, or L4 GPU run occurred.

## State invariants

- Guitar-TECHS remains closed at decision C and unscored for correctness.
- V6 constants/settings/audio path/matcher/tolerances/uncertainty/admission gates/strata/deferred-reveal rule remain frozen.
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration remains unchanged/paused.
- Policy C remains `UNENROLLED`.
- protected-song execution remains embargoed.

Next permitted work remains metadata/license/alignment search for another untouched real-guitar holdout, with no correctness exposure unless a candidate prospectively clears the frozen gates.