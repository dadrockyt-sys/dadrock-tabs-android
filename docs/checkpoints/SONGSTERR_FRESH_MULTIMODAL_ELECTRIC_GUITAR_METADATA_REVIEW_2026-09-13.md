# Songsterr Fresh V6 — Multimodal Electric Guitar Data Metadata Review

Status: **REFERENCE-BLIND METADATA/LICENSE/STRUCTURE RESEARCH ONLY — NO CORRECTNESS**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Authority

This review is subordinate to `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`, the frozen V6 method preregistration, and the frozen V6 external-scoring framework. No candidate media/archive was downloaded. Basic Pitch and V6 were not invoked. No correctness was computed.

## Candidate identity

Candidate: **Multimodal Electric Guitar Data**

Public repository identity:
- Zenodo record family `6470235` / `6470236`;
- DOI `10.5281/zenodo.6470236`;
- authors Cagri Erdem, Qichao Lan, Alexander Refsum Jensenius;
- two published archives totaling about 32.5 GB: `part1.zip` (~28.9 GB, MD5 `015b6ce53b4363a1414ecc6e706467dc`) and `part2.zip` (~3.6 GB, MD5 `59235595955ba4a2d4ed1d28a156cf44`), plus a small README PDF.

Public descriptions state that the corpus contains recordings from 36 student/semi-professional electric guitarists performing basic sound-producing actions and free improvisations. Modalities include audio, video, EMG and motion capture.

## Rights gate

Current indexed Zenodo metadata exposes **CC BY 4.0** for the dataset. This is materially better than the unresolved/explicitly restrictive rights situations already encountered for AG-PT-set, GAPS and several other candidates.

The rights signal is therefore provisionally compatible with the V6 product-validation path, subject to exact-record verification before any future corpus selection.

## Reference-semantics gate

The decisive problem is scientific/reference structure, not license.

The public dataset description and associated publication describe three basic sound-producing-action families (`impulsive`, `sustained`, `iterative`) plus free improvisations. The associated research objective is modeling motion/EMG relationships to **audio energy features**. Publicly surfaced materials establish EMG, motion capture, video and audio recordings, but do **not** establish an immutable performed note-level reference containing both:
- note onset time; and
- performed pitch/MIDI identity

for the recorded guitar events.

No synchronized MIDI pickup, JAMS note stream, score-performance note alignment, or equivalent note-level pitch/onset annotation contract is documented in the surfaced public metadata.

The frozen V6 matcher requires performed note-level onset and pitch truth. Motion/EMG timestamps, action labels, segment boundaries, metronomic task instructions or derived audio onset detectors cannot be substituted for that truth. Creating note references by onset/pitch estimation would contaminate the external correctness reference and is forbidden.

## Disposition

**NOT AUDIT-READY / DO NOT DOWNLOAD FOR V6 ADMISSION.**

The candidate has attractive real-player diversity and a permissive license signal, but current public evidence does not establish the immutable performed note-level pitch/onset reference required by the already-frozen V6 correctness protocol.

Do not run a contamination audit or download the 32.5-GB corpus unless an authoritative source first establishes that the released dataset contains a deterministic note-level pitch/onset annotation stream independent of model/detector output.

If such a reference stream is later established, the next steps would be:
1. verify exact dataset license on the authoritative Zenodo record;
2. run branch-history contamination screening before media access;
3. inspect metadata/reference structure only;
4. freeze a corpus-specific reference-blind inventory/alignment preregistration before any real audio/reference audit.

## Policy boundary

This review changes no V6 method/scoring rule and grants no admission authority.

Remain fail-closed:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
- Production unchanged.
