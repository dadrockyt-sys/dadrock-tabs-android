# Songsterr Fresh V6 — replacement-holdout pre-media batch: URMP / GAPS / EGDB

Date: 2026-09-15 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata / license / annotation-provenance screening only

## Frozen ingress rule

A V6 replacement holdout may advance to media access only when public metadata establishes all of the following before any candidate media is opened:

1. real guitar performance;
2. usable public licensing for this project;
3. pre-existing synchronized note events aligned to the exact performance;
4. reference provenance sufficiently independent for frozen V6 scoring — do not manufacture, infer, transcribe, or otherwise derive the scoring reference from the candidate with the system under test or a materially circular procedure.

A failure of any mandatory gate is enough to reject before media access. This audit does not authorize Basic Pitch, V6 correctness execution, EGFxSet reruns, or any other real-media/model run.

## Candidate 1 — URMP

### Metadata checked

Primary project page:
- https://labsites.rochester.edu/air/projects/URMP.html

The official URMP page describes 44 classical chamber pieces, isolated real-instrument tracks, MIDI scores, and frame-/note-level ground-truth annotations. However, the published URMP instrument inventory is strings, woodwinds, and brass; it does not contain guitar.

### Decision

**REJECT_PREMEDIA — fails real-guitar domain gate.**

URMP has strong synchronized note ground truth, but no guitar candidate exists in the corpus. No media was downloaded or opened.

## Candidate 2 — GAPS (Guitar-Aligned Performance Scores)

### Metadata checked

Primary project page:
- https://aim-qmul.github.io/GAPS/

Dataset record:
- https://zenodo.org/records/17152440

Paper / accepted manuscript metadata:
- https://arxiv.org/abs/2408.08653

GAPS contains real classical-guitar performances with high-resolution aligned MIDI. However, its official project page states that the dataset contains copyright material and is limited to non-commercial research, to the named individual/group/organisation, is non-transferable, and may not be sold, leased, published, or distributed without written permission.

The published construction method also does not provide an independent captured-performance reference of the kind required by the frozen V6 gate: it starts from score/audio alignment, performs DTW, then fine-aligns score notes to activations from an existing transcription model, followed by manual verification/re-alignment and filtering. Thus the high-resolution timing reference is algorithmically aligned from the performance rather than being independently captured note-event truth.

### Decision

**REJECT_PREMEDIA — fails usable-public-license gate and independent-reference provenance gate.**

No GAPS audio/video was downloaded or opened. No aligned MIDI was used for scoring.

## Candidate 3 — EGDB

### Metadata checked

Official demo/project page:
- https://ss12f32v.github.io/Guitar-Transcription/

Project repository:
- https://github.com/ss12f32v/Guitar-Transcription

Paper:
- https://arxiv.org/abs/2202.09907

Public metadata establishes real electric-guitar DI performances collected from an experienced guitarist using a hexaphonic pickup, with tablatures played to a click track and high-resolution note annotations obtained through onset alignment. The public project page exposes a dataset link.

The public project repository/page does not state a dataset license or contain a public license grant covering the dataset. Public downloadability is not itself a license grant.

### Decision

**REJECT_PREMEDIA — usable public licensing not established.**

Because one mandatory ingress gate already fails, this audit does not adjudicate whether EGDB's onset-alignment provenance would satisfy the frozen independence gate. If a project-specific written grant is later produced and explicitly authorizes the intended use, licensing could be re-audited prospectively; do not infer such a grant from public availability.

No EGDB audio, tab, or annotation payload was downloaded or opened.

## Batch result

| Candidate | Real guitar | Usable public license | Exact synchronized note reference | Independent provenance | V6 pre-media decision |
|---|---|---|---|---|---|
| URMP | **No** | Not needed after domain failure | Yes, corpus-level | Not adjudicated | **REJECT_PREMEDIA** |
| GAPS | Yes | **No — restricted/non-commercial terms** | Yes | **No for frozen V6 gate — model-assisted score alignment** | **REJECT_PREMEDIA** |
| EGDB | Yes | **Not established publicly** | Public metadata says high-resolution aligned annotations | Not adjudicated after license failure | **REJECT_PREMEDIA** |

## Safety / authorization record

- Candidate media accessed: **0**
- Candidate audio/video downloaded: **0**
- Candidate annotation/tab payloads downloaded: **0**
- Basic Pitch runs: **0**
- EGFxSet runs: **0**
- V6 correctness runs: **0**
- Frozen method/scoring changes: **0**
- V143/Gomyway activity: **0**

This batch changes only the replacement-holdout search record. All earlier V2/V3/V4/V5/Guitar-TECHS/GuitarJam evidence and closures remain unchanged.
