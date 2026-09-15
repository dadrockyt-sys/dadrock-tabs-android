# Songsterr Fresh V6 — GIHME Pre-Media Rejection

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: replacement-holdout metadata/license/alignment search only; no correctness.

## Binding upstream state

- Guitar-TECHS reference-blind alignment/inventory run `34754519541`, job `103716527380` was rechecked live before this screen and remains `completed/success`.
- Guitar-TECHS frozen audit decision remains **C**. It is closed and must not be scored.
- Frozen V6 method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- Frozen V6 implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- Frozen external scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

## Candidate

**GIHME — Guitar Improvisations with Hexaphonic Multieffect** (Reboursière, Dutoit, Tiffon).

Authoritative/public metadata reviewed without downloading or opening candidate audio/reference media:

- The SMC paper describes ten hours of real guitarist improvisations and notes/playing-technique/tuning/effect annotations.
- The recording system is a **hexaphonic guitar**, providing six independent pickup signals, one per string. The study records a hexaphonic stream without effects, a hexaphonic stream with effects, and a monophonic reduction with effects.
- The paper/thesis describes objective annotations as a mixture of automatic, semi-automatic/manual-verification, and manual processes.
- The public SMC paper record is CC BY 4.0 (the paper text itself states CC BY 3.0), but this does not by itself establish that a separately distributed underlying media corpus has the exact immutable dataset-level license/identity required for admission.

Sources reviewed:

- `https://orbi.umons.ac.be/bitstream/20.500.12907/43013/1/2022-GIHME-SMC.pdf`
- `https://zenodo.org/records/6798338`
- `https://pepite-depot.univ-lille.fr/LIBRE/EDSHS/2021/2021LILUH052.pdf`

## Frozen-gate assessment

GIHME is **not admissible as the untouched V6 external holdout** on the evidence available before media access.

The decisive structural mismatch is the frozen audio path: the clean source described by the authors is a six-channel/string-separated **hexaphonic pickup stream**, not the frozen ordinary isolated-guitar mono DI path used by V6. The available monophonic stream is described as a reduction **with effects**, which is also not the frozen clean DI path. Selecting, summing, or otherwise transforming the six hexaphonic channels to manufacture a new mono DI input would introduce a new candidate-specific audio path after preregistration and is forbidden.

Additionally, public metadata reviewed here does not establish a pre-existing synchronized MIDI/JAMS-style note-event reference with the immutable timing/identity properties required by the frozen matcher. The annotation process includes automatic/semi-automatic components; no inference or reconstruction of a V6 reference from those materials is allowed.

## Decision

**REJECT BEFORE MEDIA ACCESS.**

Do not download/open GIHME candidate audio or annotation payloads for V6 correctness. Do not run Basic Pitch or the V6 matcher on GIHME. Do not modify V6 constants, Basic Pitch settings, audio path, matcher, tolerances, uncertainty, admission gates, strata, or deferred-reveal/single-run rules to accommodate this candidate.

No correctness exposure occurred. No Modal run, Vercel heavy-GPU run, or L4 GPU run occurred.

Fail-closed state remains:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed

Next permitted V6 work remains metadata/license/alignment search for another untouched real-guitar holdout only.