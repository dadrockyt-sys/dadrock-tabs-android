# Songsterr Fresh V6 — GIHME Metadata / Release Review

Status: **NOT AUDIT-READY / NO RELEASED CORPUS LOCATED**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Scope

Metadata/release/license/reference-semantics review only. No GIHME audio, annotations, Basic Pitch, V6, or correctness was downloaded or executed.

## Candidate

GIHME = Guitar Improvisations with Hexaphonic Multieffect.

Paper: Reboursière, Dutoit, Tiffon, Sound and Music Computing Conference 2022.
Paper Zenodo records surfaced as `6573697` / `6798338`; the latter contains only the conference-paper PDF.
The paper explicitly points to `https://github.com/numediart/GIHME` as the resulting dataset location.

## Scientific properties established by the paper

The paper describes:
- approximately ten hours of guitarist improvisations;
- five guitarists;
- hexaphonic guitar capture, one pickup per string;
- clean/dry and wet six-channel hexaphonic audio plus a mono wet mix;
- 44.1 kHz / 16-bit capture;
- recorded signals synchronized by a deliberately played sharp palm-muted low-string event;
- annotations covering notes, playing techniques, tuning, effects and interviews.

For played-note annotations, the paper states that six pitch extractions were run in parallel on clean hexaphonic strings with Aubio `yin-fft`; fret numbers were inferred using known tuning/string identity; generated note/fret data were then manually verified. This could in principle provide performed note pitch/onset information if an immutable completed release existed.

However, the paper also states that **at the time of submission, acquisition of all objective annotations was not finished**.

## Official repository inspection

Repository: `numediart/GIHME`.

Current repository contents contain only `README.md` with:

`Repository for GIHME (Guitar Improvisations with Hexaphonic Multi-Effects) Dataset`

and

`Information on this dataset will be uploaded soon.`

Repository history contains only two commits, both from 2022-02-08:
- `0e522fe4298622f0849a7d0c9f219bb656e5240e` — Initial commit
- `60f7b4b68e4662572452adf0b81029a41daf3b0f` — Update README.md

No released corpus files, annotation manifests, immutable media identities, dataset license, checksums, or completed annotation package are present in the official repository.

## Rights

The conference paper itself is open access under a Creative Commons license. That licenses the paper, not an absent multi-hour dataset release. No authoritative separate dataset-audio license was located because no actual corpus distribution was located.

## V6 disposition

GIHME is **not audit-ready** and must not be selected or downloaded for V6 admission under current evidence.

Reasons:
1. the official dataset repository is still a placeholder with no released corpus;
2. the paper states objective annotation acquisition was unfinished at submission;
3. no immutable audio/reference package identities or checksums are available;
4. no authoritative license for a released corpus package is available;
5. therefore completeness, performed-note reference semantics, evidence volume, rights, and untouched-source identity cannot be frozen defensibly.

Do not manufacture a holdout from paper-linked videos, author demos, detector output, or reconstructed annotations.

GIHME may be reconsidered only if an authoritative completed corpus release appears with explicit data-file rights, immutable package identity/checksums, and performed note onset+pitch annotations suitable for the already-frozen matcher. Any future reconsideration still requires untouched-history screening before real media/reference access.

## Policy boundary

- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
- no Modal, Vercel heavy-GPU, or L4 execution
- no V6 real-corpus correctness exposed
