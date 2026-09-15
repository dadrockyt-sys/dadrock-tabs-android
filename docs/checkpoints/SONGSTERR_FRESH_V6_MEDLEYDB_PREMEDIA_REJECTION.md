# Songsterr Fresh V6 — MedleyDB pre-media rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference suitability only; no candidate media access and no correctness.

## Frozen authorities

- V6 method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- Frozen implementation commit: `3a6cbb144fec5613ab6350deb6539297d713df28`; blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- External scoring framework preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

## Guitar-TECHS prerequisite recheck

GitHub Actions run `34754519541`, job `103716527380` was rechecked live before candidate screening and remains `completed/success`. The previously frozen Guitar-TECHS audit decision remains **C**. It must not be scored and no duplicate audit run was started.

## Candidate

Candidate: MedleyDB / MedleyDB 2.0, including the public MedleyDB Pitch Tracking Subset.

Authoritative/public metadata reviewed before any media access establishes:

- MedleyDB is a multitrack music dataset with mixes, processed stems, raw audio, metadata, melody-f0 annotations and instrument-activation annotations.
- The public Pitch Tracking Subset contains 103 solo monophonic stem audio files with corresponding manually annotated continuous pitch/f0 annotations.
- Public licensing is non-commercial Creative Commons (the project download page identifies CC BY-NC-SA 4.0 for the dataset).
- The public documentation does **not** establish a synchronized pre-existing MIDI/JAMS-style note-event ground-truth population for electric-guitar DI performances that can be consumed by the frozen V6 note-event matcher without constructing/inferencing a new reference.
- MedleyDB audio provenance is general multitrack production: raw recordings and processed stems from full musical productions. Public metadata does not establish that a qualifying electric-guitar population follows the frozen ordinary isolated-guitar DI capture path.

Sources reviewed:

- https://medleydb.weebly.com/
- https://medleydb.weebly.com/description.html
- https://medleydb.weebly.com/downloads.html
- https://zenodo.org/records/2620624

## Binding decision

**REJECT BEFORE MEDIA ACCESS.**

Independent fail-closed reasons are sufficient:

1. **Reference-form gate fails:** manually annotated f0 contours are not the frozen synchronized note-event reference required by the V6 matcher. Converting f0 contours into note events would manufacture a candidate-specific reference after preregistration.
2. **Audio-path gate is not established:** public metadata does not establish a qualifying isolated electric-guitar DI population matching the frozen V6 audio path.
3. **License is non-commercial:** this is additionally incompatible with treating the dataset as an unrestricted downstream/customer-validation asset, although the first two structural failures already reject it for this audit.

No MedleyDB audio or annotation payload was downloaded/opened, no Basic Pitch or V6 correctness was run, no frozen constant/settings/matcher/tolerance/admission/strata/deferred-reveal rule changed, and no Modal, Vercel heavy-GPU, or L4 execution occurred.

## State invariants

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration remains unchanged/paused
- Policy C remains `UNENROLLED`
- protected song remains embargoed

Search may continue only for another untouched real-guitar holdout under the frozen pre-media metadata/license/alignment gates.