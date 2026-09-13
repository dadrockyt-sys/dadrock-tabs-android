# Songsterr Fresh V6 — Replacement Holdout Search Update

Status: **REFERENCE-BLIND METADATA/LICENSE/STRUCTURE RESEARCH ONLY — NO CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Authority

This update is subordinate to `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` and the already-frozen V6 method/scoring framework. No candidate audio/reference pairs were downloaded or scored. Basic Pitch and V6 were not invoked.

## EG-IPT — promising real-DI lead, not audit-ready

Public identity:
- Zenodo record `15205644`, DOI `10.5281/zenodo.15205644`.
- 52,320 monophonic electric-guitar audio files, 28 h 22 m 56 s, 96 kHz / 24-bit.
- 19 playing-technique classes.
- professional real-guitar studio recording.
- six simultaneous capture paths including a BSS AR-133 DI channel.
- three Gibson SG pickup configurations.
- archive reported by Zenodo as `EG-IPT.zip`, 23.8 GB, MD5 `48a5135adfd090515ff0af7dc5c3c32f`.

Accompanying public code repository `nbrochec/nime2025` confirms that the dataset is organized under pickup configuration and that the project-generated CSV contains only `file_path`, technique `label`, and train/test/validation split. Its processing code trims silence for technique classification. The surfaced public metadata/code does **not** establish a separate immutable note-level pitch/onset annotation stream suitable for the already-frozen V6 correctness matcher.

The repository code is GPL-3.0, but that is not sufficient evidence by itself for the audio archive's dataset license. Zenodo search results available in this research pass did not expose a clear audio-license field. Therefore rights must also be resolved independently before any audit selection.

Disposition: **keep as metadata-only lead, not audit-ready**. Do not download the 23.8-GB archive or run a contamination audit yet. First establish both (a) audio-dataset license/provenance and (b) a deterministic performed pitch/onset reference contract that exists independently of model output. If either cannot be established, reject without corpus access.

## GUITAR-FX-DIST / IDMT-SMT-Audio-Effects — rejected on rights gate

GUITAR-FX-DIST is derived from the IDMT-SMT-Audio-Effects source recordings. Fraunhofer's official dataset page states that IDMT-SMT-Audio-Effects is provided for evaluation under **CC BY-NC-ND 4.0**.

This is materially narrower than the permissive product-validation rights required for the V6 admission path. The corpus also consists predominantly of isolated two-second note/effect samples rather than independent musical performances.

Disposition: **REJECTED for V6 admission under the current product-validation path.** Do not download/audit/score GUITAR-FX-DIST or IDMT-SMT-Audio-Effects as a replacement holdout.

## EG-Solo — rejected on recording provenance

Public project metadata describes 76 electric-guitar solo clips / 6,833 annotated notes with MIDI note/technique labels, but the audio comes from professional electric-guitar demonstration videos on YouTube, including popular-song solos with backing tracks.

That recording provenance is not a defensible permissive-audio basis for this product-validation holdout. A separately downloadable annotation file does not grant rights to the underlying third-party recordings.

Disposition: **REJECTED on audio-rights/provenance before any corpus access.** Do not download/audit/score EG-Solo for V6 admission.

## GIHME status refinement

Additional public UMONS/ORBi metadata confirms that the 2022 GIHME publication is described as a dataset-related work and links DOI `10.5281/zenodo.6573697`, but the surfaced Zenodo records still resolve to the conference-paper artifact rather than a clearly licensed multi-hour dataset package. No stable downloadable corpus identity or dataset license was found in this pass.

Disposition remains: **scientifically promising but unresolved and not audit-ready**. Do not infer a license or archive identity from the paper DOI.

## Current selection state

No replacement holdout has been selected. No replacement candidate has had V6 correctness exposed.

Closed/rejected: GuitarSet, IDMT-SMT-Guitar, Guitar-TECHS, GAPS, EGSet12, GUITAR-FX-DIST / IDMT-SMT-Audio-Effects, EG-Solo.

Still metadata-only leads:
- GIHME — real, long-form, richly annotated, but dataset archive/license unresolved.
- EG-IPT — large real electric-guitar DI corpus, but dataset license and note-level performed pitch/onset reference contract unresolved.
- EGFxSet — permissive real electric-guitar backup, but isolated-tone independence/onset/evidence-volume limitations remain.

## Next allowed work

1. Continue searching for a different untouched, permissively licensed **real guitar** corpus with immutable performed note-level onset/pitch truth and enough independent events to plausibly satisfy the frozen >=1,000-positive gate.
2. Resolve GIHME corpus archive/license without downloading candidate media.
3. Resolve EG-IPT dataset license and whether raw metadata exposes pitch plus an immutable onset reference; do not manufacture onset truth by trimming/detection.
4. Keep EGFxSet as a narrow backup only; effect duplicates may not be counted as independent evidence merely to satisfy the volume gate.
5. Before selecting any candidate, run a branch-specific contamination/history audit; default-branch search is insufficient.
6. Only after rights, provenance, untouched status, reference semantics and plausible evidence volume are defensible may a corpus-specific reference-blind inventory/alignment preregistration be frozen.

Fail-closed authority remains unchanged: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected song embargoed, Production unchanged.
