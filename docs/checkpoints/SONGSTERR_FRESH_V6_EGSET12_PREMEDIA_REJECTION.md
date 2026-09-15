# Songsterr Fresh V6 — EGSet12 Pre-Media Rejection

Date: 2026-09-15 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Scope: V6 replacement-holdout metadata/license/alignment search only; no correctness.

## Frozen authority

V6 method remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md` at commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`. External scoring remains frozen by `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md` at commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Guitar-TECHS run `34754519541`, job `103716527380`, was reverified `completed/success` before this search. Artifact `guitar-techs-v6-alignment-inventory` remains artifact ID `10317695640`, digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`, with frozen alignment decision C. Guitar-TECHS correctness remains forbidden.

## Candidate

EGSet12, Zenodo record `11406378`, published as twelve real and original solo electric-guitar performances for guitar-tablature-transcription evaluation.

Authoritative public metadata establishes:

- twelve real solo electric-guitar performances;
- a Sire T7 Telecaster and Yamaha B15 amplifier;
- audio captured by an ECM8000 microphone positioned 15 cm from the amplifier into a UMC202 HD interface;
- 48 kHz recording; stereo files duplicate a mono signal;
- no additional effects beyond the amplifier;
- the corpus is explicitly intended as an evaluation set and associated material exposes ground-truth tablature/JAMS in downstream documented use.

## Frozen V6 admission finding

**REJECT BEFORE MEDIA ACCESS.**

The frozen V6 external holdout requires the preregistered isolated-guitar DI audio path. EGSet12's authoritative dataset description instead specifies a microphone recording of the guitar amplifier. That is a materially different signal path. The presence of real guitar performances and usable symbolic ground truth cannot cure failure of the frozen audio-path gate, and the gate cannot be changed after observing a candidate.

No EGSet12 WAV, JAMS, MIDI, annotation, or other candidate media/reference payload was downloaded or opened for this V6 audit. No Basic Pitch or V6 correctness was run. No V6 constants, Basic Pitch settings, matcher, tolerances, uncertainty, admission gates, strata, alignment method, or deferred-reveal/single-run rule changed.

## Decision

EGSet12 is ineligible as the untouched V6 replacement holdout because its authoritative capture path is amplifier-microphone audio rather than the frozen DI path. Continue metadata/license/alignment search only.

Fail-closed state remains:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution embargoed

No Modal run, Vercel heavy-GPU run, or L4 GPU run occurred.
