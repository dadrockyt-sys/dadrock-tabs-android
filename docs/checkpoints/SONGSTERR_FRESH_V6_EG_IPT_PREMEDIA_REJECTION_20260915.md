# Songsterr Fresh V6 — EG-IPT Pre-Media Rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/alignment search only; no correctness exposure.

## Frozen V6 context

The V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. External scoring remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS run `34754519541`, job `103716527380` was reverified `completed/success`. Artifact `guitar-techs-v6-alignment-inventory`, artifact ID `10317695640`, digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`, merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`. Frozen alignment decision remains `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; therefore Guitar-TECHS correctness remains forbidden.

## Candidate

Candidate: EG-IPT Dataset (Electric Guitar Instrumental Playing Techniques), Zenodo record `15205644`, version 1, published 2025-04-13.

Authoritative public metadata establishes:

- 52,320 monophonic isolated single-note electric-guitar audio files;
- 28 h 22 m 56 s total;
- 96 kHz / 24-bit recordings;
- six simultaneous capture perspectives, including a true DI path through a BSS Audio AR-133 DI box into a Midas XL48;
- one archive `EG-IPT.zip`, 23.8 GB, MD5 `48a5135adfd090515ff0af7dc5c3c32f`.

## Pre-media gate result

**REJECT — DO NOT ACCESS MEDIA FOR V6 CORRECTNESS.**

Two independent frozen-admission requirements are not established by the authoritative dataset record:

1. The Zenodo Rights section exposes no dataset license value. An open/downloadable record is not itself a sufficient immutable usage/license grant for the frozen external-holdout gate.
2. The authoritative metadata describes isolated single-note recordings and technique labels, but does not establish synchronized note-event ground truth (MIDI/JAMS or an equivalent immutable event-time reference) suitable for the frozen V6 matcher/scoring population. Constructing event timing from filenames, clip boundaries, audio, or inferred labels would create a new reference and is outside the frozen framework.

The accompanying NIME code repository's GPL-3.0 software license is not treated as a license grant for the 23.8 GB Zenodo dataset itself.

Because the candidate fails before media admission, no archive download, audio inspection, annotation inspection, Basic Pitch invocation, V6 invocation, correctness computation, scoring harness run, or alignment tuning is permitted or performed.

## Policy boundary

- `basicPitchInvoked:false`
- `v6Invoked:false`
- `correctnessComputed:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C remains `UNENROLLED`
- protected-song execution remains embargoed
- Modal/Vercel-heavy-GPU/L4 used: false

## Next allowed action

Continue only metadata/license/alignment search for another untouched real-guitar holdout that prospectively clears every frozen pre-media gate. Do not use EG-IPT correctness observations because none were exposed.