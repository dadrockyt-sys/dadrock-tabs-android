# Songsterr Fresh V6 — DoMP metadata/release review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/release inspection only; no candidate media download, no Basic Pitch, no V6 correctness.

## Candidate

Dataset of Monophonic Patterns (DoMP), Silva & Turchet, Zenodo DOI `10.5281/zenodo.10818617`.

## Why it was worth checking

The Audio Mostly 2024 paper describes 4,000 live human-performed monophonic patterns/variations from 40 musicians, including 20 electric-guitar players. The guitar performances used a Fishman TriplePlay MIDI tracking device. The paper says the dataset contains patterns in MIDI and audio format. The guitar subset alone is 2,000 performed patterns/variations, and the authors report substantial event density, so capacity would be plausibly large enough to merit scrutiny if synchronized evaluated audio were actually released.

Zenodo explicitly marks the dataset CC BY 4.0. This is materially cleaner licensing than many prior candidates.

## Authoritative release inspection

Zenodo record `10818617` currently exposes exactly one archive:

- `DoMP.zip`
- size: `2.7 MB`
- MD5: `c5f0e2b10eae47435f409930a4fa94ae`
- license: Creative Commons Attribution 4.0 International

The Zenodo archive preview exposes `.mid` files throughout the tree. The preview has no `.wav`, `.flac`, `.mp3`, `.aiff`, or `.m4a` entries. The 2.7 MB archive size is also consistent with a symbolic-MIDI release rather than thousands of synchronized audio performances.

Therefore the public release, as actually deposited on Zenodo, does not provide an evaluated real-guitar audio population that can be paired with the performed MIDI reference for V6 scoring.

## Frozen-gate decision

**REJECT / NOT AUDIT-READY: PUBLIC RELEASE LACKS EVALUATED AUDIO.**

DoMP is not admitted to a V6 structural audit because frozen replacement-holdout gate 1/2/3 must apply to an actually available audio+reference corpus. A paper statement that audio exists is not enough when the authoritative public deposit currently exposes only the tiny MIDI archive.

This rejection is independent of model correctness and does not modify any V6/scoring constants, matcher, tolerance, Basic Pitch setting, uncertainty rule, admission threshold, stratum rule, or deferred-reveal/single-run requirement.

## Important nuance

DoMP is stronger than many rejected candidates in two respects: the guitar MIDI was captured during live performance via a dedicated MIDI tracker rather than reconstructed later from the evaluated audio, and Zenodo provides an explicit CC BY 4.0 license. If an authoritative future release adds the synchronized original guitar audio under the same usable rights, DoMP could merit a fresh untouched-status + preregistration review. That would be a genuinely new hard-gate change, not a reason to infer or acquire unavailable media now.

## Sources inspected

- Zenodo record `https://zenodo.org/records/10818617`
- Zenodo archive preview `https://zenodo.org/records/10818617/preview/DoMP.zip?include_deleted=0`
- Silva & Turchet, *Real-Time Pattern Recognition of Symbolic Monophonic Music*, Audio Mostly 2024
- Nishal Silva research/dataset summary `https://nish.al/research.html`

## Authority after this review

Unchanged:

- Guitar-TECHS remains frozen outcome C before correctness.
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration remains unchanged/paused.
- Policy C remains `UNENROLLED`.
- protected-song execution remains embargoed.
- no Modal, Vercel heavy-GPU, or L4 GPU compute was used.
