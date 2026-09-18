# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 22

Date: 2026-09-18 UTC
Branch: `songsterr-fresh-pipeline-v1`
Starting head: `42e5ed3ef375690806f4807c7edbb8caa8d00d67`
Status: **METADATA QUALIFICATION ONLY / NO PRE / REAL CORRECTNESS UNKNOWN**

## Scope and immutable boundaries

Resumed from the canonical checkpoint, Search 21 and the budget checkpoint. No candidate audio or onset payload was opened; no model, scoring, calibration or archived pipeline was run. `S AND E AND O AND K` is unchanged. `091CGAFP` remains excluded. All historical outcomes and authorization flags remain unchanged.

## Exact MINST annotation identities without payload access

At source commit `5847ac421522a393df77ca2a43acdc326f7d64e8`, `minst/sources/rwc.py` uses the extension-free original basename to generate an identifier. `minst/utils.py` defines this as `rwc` plus the first eight hexadecimal characters of MD5 of the UTF-8 basename. Source blobs are respectively `8b92d3dc242be4a4192822eceef7ae5b28c10f19` and `ac421cc409304bb1f9b07a62ee62e72eac993053`.

The recursive Git tree was not truncated. Computing these filename hashes locally and checking tree entries established the following file identities. CSV contents, event counts and timestamps were NOT read. All paths are relative to `data/onsets/rwc/`.

| RWC basename | MINST CSV | Git blob SHA |
|---|---|---|
| `091CGAFP` (excluded) | `rwc5619bf62.csv` | `4cb24267b5ab5c60f212d7047eeee9e30344a62b` |
| `091CGAFM` | `rwc13c61c9f.csv` | `3129ba0c8f26838185d0aa8b26c1d82140b9c3a0` |
| `091CGAFF` | `rwc2fb41c68.csv` | `c73b0e6d44bb67062f0466c11e55a9568694ac39` |
| `092CGAFP` | `rwc81dcb120.csv` | `9a4d30136e897113d317d80fe61a494b81ef8cba` |
| `092CGAFM` | `rwcf6a6e74f.csv` | `2906f332c3471fc704452622b3d6fa3638dba78e` |
| `092CGAFF` | `rwca4062c1d.csv` | `8d231cba54c88005d55bf90b65e13831504169eb` |
| `093CGAFP` | `rwcff7f6aa7.csv` | `5dd0c30fd61d53cd329f046ca5bea4ece2cc0759` |
| `093CGAFM` | `rwc053701da.csv` | `3c3a3e62e71f4c435761c1f936de2ba3a6e4e49a` |
| `093CGAFF` | `rwc14957a7f.csv` | `daf3bde900f503b0fb814d506b38f8ec020a9b8d` |

Source links:
- [RWC filename mapper](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/minst/sources/rwc.py)
- [Identifier and pathname helpers](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/minst/utils.py)
- [Tree metadata only](https://api.github.com/repos/ejhumphrey/minst-dataset/git/trees/5847ac421522a393df77ca2a43acdc326f7d64e8?recursive=1)

The tree also lists `data/notes/091CGAFM_11.flac`, blob `26a03669798f73eb551281904fd418ec6af9601d`. No bytes from that audio blob were requested. Its upstream presence is not proof of prior project exposure, but this derivative identifier must be included in the lineage audit. Do not run MINST's test suite or clone/check out its full data tree during metadata qualification.

## Onset authority and annotation-rights questions remain open

The [MINST README](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/README.md), blob `cc89c6b313e05262c04e3cc3be81203a2fe850b0`, describes human correction of estimated onsets to obtain useful segmentation points. Its stated purpose includes roughly splitting recordings into notes. This supports human involvement, but does not establish the exact note-birth convention, annotation error bounds, or review completion for each candidate file.

The [collector](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/scripts/collect_onsets.py), blob `d4de26b4fa90802daf51b20615fa0207b9f3839d`, documents collecting corrected files from the RWC annotation workflow. It sorts the `time` column and clamps negative values to zero. The [splitter](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/scripts/split_audio_to_clips.py), blob `b2478290e301c8fd2082fbd5fca1112672ec8ae8`, uses saved times as clip boundaries and the following boundary as the end. These are code-level semantics, not observations of candidate annotation values.

Do not conflate Szczupak's reported reviewed marks with MINST's independently collected marks. Their equality or common annotation lineage has not been established. The historical Szczupak finding is unchanged; its existence alone does not certify the identified MINST files.

The [MINST license](https://github.com/ejhumphrey/minst-dataset/blob/5847ac421522a393df77ca2a43acdc326f7d64e8/LICENSE), blob `ddd9b9cc73d0a463419796ebc5050775ebe6d5ed`, expressly grants permissions for software. This pass did not establish an explicit annotation-data license or its scope. Do not assume the separate Zenodo audio license covers independently produced onset data. This is an unresolved qualification question, not a legal determination that annotation use is prohibited.

## Tuning research

Re-read the [official English AIST acquisition description](https://staff.aist.go.jp/m.goto/RWC-MDB/rwc-mdb-i.html) and [Japanese original](https://staff.aist.go.jp/m.goto/RWC-MDB/rwc-mdb-i-j.html). The English page supports the previously recorded general ascending-pitch protocol. The Japanese page additionally says details of playing styles, pitches and dynamics were provided separately after distribution media arrived. That points toward original companion documentation as a useful metadata target; it does not establish that such material is publicly available today.

Neither page supplied the exact six open-string pitches for the nine named recordings. General guitar-tuning search results do not close that source-lineage gap. Exact tuning and file-specific ordering remain prerequisites; no candidate pitch map was promoted to verified truth.

The prior Zenodo release identity is retained as historical checkpoint evidence. A follow-up browser request timed out, so no new release/license verification is claimed in this pass.

## Stronger but incomplete repository-history audit

Fetched advertised branch heads and pull-request heads into remote-tracking refs of a non-shallow, blob-filtered local clone. The working branch remained `songsterr-fresh-pipeline-v1`. No remote branch except the fresh branch is to be modified. Reading archived history for exposure evidence is not resuming its execution.

Coverage before this documentation update:

- 41 branch refs and 29 pull-request head refs;
- 8,808 unique reachable commits (fresh-branch ancestry alone: 8,174);
- merge-aware, root-inclusive historical raw-diff inventory: 11,344 distinct old/new blob identities;
- 6,705 selected documentation/source blobs with extensions `.md`, `.py`, `.js`, `.ts`, `.yml`, `.yaml`, `.sh`, `.mjs`, `.toml`;
- 818 available selected blobs scanned for content; 5,887 remained unavailable;
- no historical pathname contained the case-insensitive strings `091cg`, `092cg`, `093cg`, `minst`, or `rwc`;
- five scanned blobs matched the exact identifier search: only the canonical checkpoint and metadata-search documents 15, 17, 20 and 21.

The search included all nine basenames, computed MINST IDs and annotation blob hashes, the upstream sample-audio filename/hash, `RWC-MDB-I-2001`, `RWC-I`, `RWC Instruments`, DOI identifier `17170844`, `MINST`, `Szczupak`, and `ejhumphrey/minst`. Output was limited to matching identifiers, paths and blob identities, not surrounding payload lines.

Reproducible inventory command:

```sh
git log --all --full-history -m --root --format= --raw --no-abbrev --no-renames
```

Collect both nonzero old/new object IDs and their paths from the raw records; select the stated source/document extensions; check local availability with `GIT_NO_LAZY_FETCH=1 git cat-file --batch-check`; scan available blobs with literal case-insensitive identifiers above. Do not expand into annotation/media payloads during this phase.

Batch retrieval of missing historical blobs failed with `bad revision` / `did not send all necessary objects`. Smaller Markdown batches also failed. Therefore this is a bounded historical-content audit, **not a clean full-history certificate**. It does not cover unavailable blobs, excluded formats, workflow artifacts/logs, issue/PR discussion bodies, deleted/unadvertised refs, external caches or uncommitted prior work. No candidate is declared untouched and no subset is frozen.

## Next exact resume point

1. Resolve the inaccessible historical objects or use commit/path-based GitHub reads to complete the missing source/document audit; retain the explicit coverage limits.
2. Include hashed MINST IDs, annotation blob identities and the upstream audio derivative in future exposure searches.
3. Locate source-lineage tuning/acquisition companion documentation without retrieving audio or onset values.
4. Establish timing convention and file-specific review authority for the actual annotation source to be used; establish annotation-data usage rights separately from audio rights.
5. If all gates clear, choose a prospective untouched subset and freeze an exact PRE; then stop for fresh post-freeze authorization as the canonical checkpoint requires. No PRE is justified now.

State: candidate audio opened `0`; candidate onset payloads opened `0`; model/correctness runs `0`; candidate/threshold changes `0`; archived pipeline execution `0`; new PRE `none`; real correctness `unknown`.
