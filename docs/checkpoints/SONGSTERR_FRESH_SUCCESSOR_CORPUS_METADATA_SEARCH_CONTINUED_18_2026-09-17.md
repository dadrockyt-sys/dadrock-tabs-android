# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 19

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: targeted legacy filename / author-server metadata search only

## Frozen boundary

- No successor PRE or correctness/model execution is authorized.
- Do not resume archived V143/Gomyway.
- No successor audio or annotation payload was opened.

## Benetos/Dixon legacy filename hunt

The public Emmanouil Benetos transcription examples page exposes these example names:

- RWC-MDB-J-2001 No. 7: `data4.mp3`, `data4_synthTrans.mp3`.
- RWC-MDB-J-2001 No. 9: `sample3.mp3`, `sample3_synthTrans.mp3`.
- RWC-MDB-J-2001 No. 9: `ex1_original.mp3`, `ex1_synthTrans.mp3`.

Targeted indexed searches were run for those stems combined with RWC IDs and likely ground-truth MIDI suffixes such as `gt.mid` / `groundtruth.mid` / `.mid`, including author-server scoped searches.

Result: no public hand-edited GT MIDI artifact was located. The author server continues to expose thesis/papers and the example MP3 page, but no indexed `.mid` corresponding to the manually edited 23-second ground truth surfaced.

Status unchanged:

`BENETOS_DIXON_23S_RWC_GUITAR_GT = TECHNICALLY_STRONG_MANUAL_REFERENCE / PUBLIC_FILE_NOT_LOCATED / RIGHTS_UNRESOLVED / NOT_PRE_READY`

## Additional observation

Simon Dixon's current public page confirms the historical Benetos work remains hosted in the QMUL webspace and lists newer guitar-transcription research, but no legacy RWC GT download is exposed from the surfaced page.

## State after Search 19

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Next high-value search direction

Rather than repeat filename guesses, search for:

1. archived directory indexes / web snapshots of the Benetos/QMUL transcription workspace;
2. supplementary-file repositories tied to the 2011/2012 Benetos-Dixon publications;
3. later code/data releases by Benetos/Dixon that may have copied the old RWC GT under neutral numeric filenames;
4. current RWC J007/J009/J010 issue/PR/history evidence that could independently establish per-note onset authority;
5. newly public guitar score-following datasets with explicit performed-onset + MIDI-note reference rows.
