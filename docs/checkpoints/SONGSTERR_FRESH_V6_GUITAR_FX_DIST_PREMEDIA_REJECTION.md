# Songsterr Fresh V6 — GUITAR-FX-DIST Pre-Media Rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: V6 replacement-holdout metadata/license/alignment search only; no correctness.

## Prior audit state reverified

Guitar-TECHS reference-blind alignment/inventory run `34754519541`, job `103716527380`, was rechecked before this search step and remains `completed/success`. Its previously frozen alignment decision C remains binding; Guitar-TECHS is not scored and no duplicate audit run was started.

## Candidate

`GUITAR-FX-DIST` (Zenodo records including 4296040/4298000/4298017/4298025), Marco Comunità / Queen Mary University of London.

Authoritative Zenodo metadata describes a large electric-guitar effects dataset containing both unprocessed and processed recordings. The unprocessed source population consists of 624 monophonic notes and 420 polyphonic intervals/chords from two guitars, while the processed population applies overdrive/distortion/fuzz variants. Critically, the Zenodo record states that the original unprocessed recordings are from the `IDMT-SMT-Audio-Effects` dataset.

## Frozen-scope/admission finding

This candidate is rejected before media/reference access for two independent fail-closed reasons:

1. The candidate's underlying real-guitar source is explicitly IDMT-SMT-Audio-Effects. The user's current hard scope expressly forbids resuming IDMT/V4. A derivative/processed repackaging is not a legitimate new untouched external holdout that can bypass that closed lineage.
2. The public GUITAR-FX-DIST record reviewed here does not establish a synchronized pre-existing note-event MIDI/JAMS reference aligned to the candidate recordings under the frozen V6 matcher. Its stated annotations/use are effects-oriented; no independent synchronized event-ground-truth identity was established at the pre-media gate.

No attempt was made to inspect or execute the underlying IDMT corpus, and no media archive/member was downloaded or opened.

## Decision

**REJECT BEFORE MEDIA ACCESS.**

This rejection is structural/scope-based and contains no Basic Pitch/V6 correctness observation. It does not alter the frozen V6 method, Basic Pitch settings, audio path, matcher, tolerances, uncertainty rules, admission gates, strata rules, or deferred-reveal/single-run rule.

No Modal run, Vercel heavy-GPU run, L4 GPU run, protected-song execution, duration research, GOAT/reference scoring, GuitarSet/V3, IDMT/V4 execution, archived V143/Gomyway work, `main`, or Production work occurred.

Fail-closed state remains: `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`; duration remains paused; Policy C remains `UNENROLLED`; protected-song execution remains embargoed.
