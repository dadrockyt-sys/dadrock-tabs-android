# Songsterr Fresh V6 — FretboardFlow Metadata / Reference Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: replacement untouched real-guitar holdout metadata/license/reference review only. No candidate media access. No Basic Pitch/V6 correctness.

## Authority preserved

- V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- Frozen implementation remains commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- External scoring remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.
- Guitar-TECHS remains closed outcome `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness is permitted.

## Candidate

FretboardFlow, Marcel Vélez Vásquez et al., ISMIR 2025.

Primary/public sources reviewed:

1. ISMIR 2025 paper/program page: `https://ismir2025program.ismir.net/poster_266.html`
2. Public project repository: `https://github.com/Marcel-Velez/FretboardFlow`
3. Repository `README.md` on public `main` as observed 2026-09-14.

## Positive evidence

The ISMIR record describes FretboardFlow as a new public dataset of expert-performed rhythm-guitar material recorded with a hexaphonic pickup. It reports 97 recordings across 35 songs, with multiple voicing variations. The project therefore contains genuine real-guitar performances and is relevant to a V6 replacement-holdout search.

The public repository README states:

- `97 recordings across 35 songs`;
- up to five versions per song;
- capture with a hexaphonic pickup;
- MIDI files stored under `data/midi`;
- four guitar experts so far.

## Decisive reference failure

The same authoritative project README explicitly states that the released MIDI is quantized to four chords per bar and is **not millisecond-accurate transcription**. This is incompatible with the frozen V6 requirement for immutable independent performed note-level onset + pitch truth suitable for one-to-one onset matching at <= 50 ms.

The ISMIR description additionally says the dataset builds on the GuitarSet pipeline and uses a Python translation of the KAMIR interference-reduction method for **automated hexaphonic transcriptions**. That further establishes that the released symbolic representation is a processed/derived transcription product rather than an independent high-resolution performed onset stream.

This is a hard pre-media gate failure. No attempt may be made to repair, re-time, infer, regenerate, or align this MIDI from the evaluated audio for V6 admission.

## Public-audio / rights status

The public repository README states that audio recordings "will also" be uploaded, while the repository metadata currently reports no declared repository license. The authoritative repository therefore does not presently establish both:

1. a released immutable audio package corresponding to the symbolic population; and
2. explicit permissive performance-audio rights suitable for product validation.

Those are independent blockers, but they are not needed to reach rejection because the reference-timing gate already fails.

## Population observation

97 recordings across 35 songs is a small population relative to the frozen requirement for a plausible >=1,000 V6-positive estimate capacity, and multiple versions of the same songs must not be treated as automatically independent evidence. No media/count audit was performed because the candidate already fails the independent high-resolution reference gate.

## Frozen decision

**FretboardFlow — REJECTED BEFORE MEDIA ACCESS.**

Reasons:

- real guitar: yes;
- independent performed note-level onset + pitch truth: **fail** — repository explicitly says MIDI is quantized and not millisecond-accurate; symbolic material is produced through the GuitarSet/KAMIR automated hexaphonic-transcription pipeline;
- explicit permissive performance-audio rights: **not established** in the public repository reviewed;
- released audio package: **not established** by the current public repository README;
- plausible >=1,000 V6-positive capacity: not established and not audited after the hard reference failure;
- untouched status: not relevant after the hard gate failure.

No candidate media was downloaded or inspected. No Basic Pitch, V6, scoring, correctness exposure, Modal, Vercel heavy-GPU, or L4 work occurred.

## Continuing authority

FretboardFlow must not be scored or used to tune/alter V6. Continue only metadata/license/alignment search for a genuinely new untouched real-guitar corpus whose independent performed note-level onset+pitch reference and rights can be defended before media access.

Fail-closed state remains unchanged:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed
