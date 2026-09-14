# Songsterr Fresh V6 — PolyMap Metadata Holdout Review — 2026-09-14

## Scope

Metadata/license/reference-provenance screening only. No candidate media was acquired and no Basic Pitch/V6 correctness was run.

## Guitar-TECHS prerequisite recheck

- Run `34754519541`, job `103716527380`: terminal success.
- Artifact `guitar-techs-v6-alignment-inventory`, id `10317695640`, remains unexpired through 2026-12-12.
- GitHub-reported archive digest: `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`.
- Frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION` remains binding; Guitar-TECHS correctness remains prohibited.

## Candidate

**PolyMap: A 64-Channel Polyphonic Guitar Pickup System** — David Wieland, Jonas Roth, Christoph Studer, ETH Zürich / Integrated Information Processing Group, 2026.

Primary public evidence reviewed:

- ETH Zürich D-ITET news, 2026-03-23: https://ee.ethz.ch/de/news-und-veranstaltungen/d-itet-news-channel/2026/03/e-gitarre-die-jede-saite-detailgetreu-wiedergibt-geht-viral.html
- ETH Zürich IIP news index: https://iip.ethz.ch/news-and-events.html
- 2026 preprint: https://arxiv.org/abs/2608.27522

## Public-evidence review

The primary sources establish a real electric-guitar pickup/capture prototype: an eight-string custom instrument with eight pickups per string (64 total) whose signals are independently digitized and transmitted over MADI for processing. That makes PolyMap technically relevant to future independent-sensor capture design.

However, the authoritative public material reviewed here presents PolyMap as a pickup system/prototype and research paper, not as a released external validation corpus. It does not establish the combination required by the frozen V6 replacement-holdout gates:

1. a released real-performed-guitar audio population suitable for external scoring;
2. an immutable independent performed note-level onset + pitch reference stream for that population, not reconstructed from evaluated audio/model output;
3. an explicit usable/permissive corpus-level performance-audio rights package for product validation;
4. a documented population plausibly capable of satisfying the frozen >=1,000 V6-positive admission requirement without duplicate/effect inflation; and
5. immutable released package identities needed to establish untouched status.

This review makes no claim that a future PolyMap-derived corpus could never satisfy those requirements. It records only that the current public evidence does not establish an admissible existing holdout.

## Frozen decision

`NOT_ADMISSIBLE_ON_CURRENT_PUBLIC_EVIDENCE_METADATA_ONLY_LEAD_CLOSED_FOR_NOW`

Do not acquire PolyMap media or run Basic Pitch/V6 correctness on this basis. Any future reopening requires new authoritative evidence of an actual released corpus and starts again at metadata/rights/reference-provenance screening before media access.

## Governance unchanged

- No V6 constants, Basic Pitch settings, audio path, matcher, tolerances, uncertainty, admission gates, strata or deferred-reveal/single-run rules changed.
- No Guitar-TECHS correctness, repair, binding or rerun.
- No candidate media acquisition.
- No Modal, Vercel heavy-GPU or L4 GPU use.
- `modelValidationComplete:false`.
- `customerEligibleEvents:0`.
- `mayAdvanceDelivery:false`.
- Duration authority unchanged/paused.
- Policy C remains `UNENROLLED`.
- Protected-song execution remains embargoed.
