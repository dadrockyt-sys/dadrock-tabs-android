# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 16

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only; no evaluation payload access

## Frozen boundary

- Candidate remains exactly `S AND E AND O AND K`.
- No successor PRE or correctness/model run is authorized.
- Do not resume archived V143/Gomyway.
- Do not reopen closed/exposed historical corpus families as untouched.
- Do not open/download candidate audio or annotation payloads before a new exact PRE and fresh post-freeze authorization.
- Required reference remains deterministic actual-performance note onset plus integer-MIDI pitch, independent of Basic Pitch or any other AMT/pitch-estimation output.

## RWC 2.0 — exact public annotation identities locked

Without opening the MIDI payloads, the public GitHub directory metadata establishes immutable current blob identities for the three strongest guitar-only Jazz candidates in `rwc-music/rwc-annotations`:

- `01_annotations_preprocessed/MIDI_aligned/RWC-J/RWC_J007.mid`
  - blob `fcc51bc1e0eaa6ef1c22be45a15b04e81b31353c`
  - size `12814` bytes
- `01_annotations_preprocessed/MIDI_aligned/RWC-J/RWC_J009.mid`
  - blob `c983338f9d95d1bf91b3e8e2389708fa9d50bafd`
  - size `10707` bytes
- `01_annotations_preprocessed/MIDI_aligned/RWC-J/RWC_J010.mid`
  - blob `9ea85986d63af889ce2ebcd35fd084b831f410b9`
  - size `7268` bytes

Repository head observed during this pass: `0a1a6c31dbe73a7f5d44f7caef8cd0999402a4c2`.

No MIDI payload was fetched or parsed.

## RWC 2.0 — alignment provenance clarified

The 2026 RWC Revisited paper states:

- the original symbolic MIDIs were transcribed after production by professional karaoke-industry transcribers;
- the later AIST annotations included manually aligned MIDI made with dedicated editing tools;
- the 2026 re-release systematically refines/re-aligns MIDI using SyncToolbox audio–MIDI synchronization;
- first-onset and last-offset anchors were manually annotated for every audio recording;
- all tracks were listening-verified by the authors via sonification;
- additional manual anchor points were added in difficult cases;
- the authors explicitly acknowledge that some note-level missing/incorrect/additional-note discrepancies can remain and that a systematic quantitative note-level evaluation remains future work.

This improves provenance and establishes human review, but it does **not** by itself prove that every note onset in J007/J009/J010 is authoritative exact performed-note birth. In particular, the current timing can include algorithmic audio–MIDI warping rather than independent per-note manual onset placement.

Therefore the current RWC 2.0 status remains:

`STRONG_PUBLIC_SCRAPEABLE_CANDIDATES / RIGHTS_AND_FILE_IDENTITY_CLEAR / HUMAN_TRANSCRIBED_PITCH_TRUTH / CURRENT_PER_NOTE_ONSET_AUTHORITY_NOT_YET_STRONG_ENOUGH_FOR_PRE / FULL_HISTORY_PROVENANCE_NOT_YET_PROVEN`

This is intentionally stricter than treating absence from the public issue #258 problem table as affirmative correctness evidence.

## Older Benetos/Dixon manual RWC guitar ground truth — stronger semantics

A stronger historical reference artifact was confirmed from the primary Benetos/Dixon transcription literature.

For the RWC transcription test set, the papers identify Jazz pieces No. 6, 7, 8 and 9 as guitar recordings. They explicitly state that the supplied non-aligned MIDI contained note errors/omissions and unrealistic durations, and therefore **aligned ground-truth MIDI was created for the first 23 seconds of each recording using Sonic Visualiser for spectrogram visualization and MIDI editing**. Evaluation used the resulting ground truth on a 10 ms time scale.

This applies directly to:

- RWC-MDB-J-2001 No. 6
- RWC-MDB-J-2001 No. 7
- RWC-MDB-J-2001 No. 8
- RWC-MDB-J-2001 No. 9

For this project, J007 and J009 are especially interesting because they overlap the strongest current guitar-only public candidates while offering substantially stronger documented manual ground-truth semantics than the modern automatically re-warped MIDI.

Current status:

`TECHNICALLY_STRONG_MANUAL_23S_GUITAR_GT / EXACT_PUBLIC_GT_FILE_NOT_LOCATED / RIGHTS_FOR_DERIVED_GT_NOT_YET_ESTABLISHED / NOT_PRE_READY`

Searches for obvious public filenames, mirrors, and download pages did not locate the actual hand-edited 23-second MIDI files. The papers demonstrate that the artifacts existed and were used, but publication of the papers is not a public data release.

## Additional scrapeable-data pass

### Virtuoso Strings

A newer dataset with 746 tracks and 68,728 onset annotations was inspected because its semi-automatic + human-QC annotation process is potentially valuable. Public metadata describes string ensembles (quartet/trio/duet/solo) and one annotated string instrument per track. The surfaced material does not establish a qualifying guitar population or integer-MIDI pitch truth paired with those onsets.

Status:

`AUXILIARY_ONSET_DATA / NO_QUALIFYING_GUITAR_PLUS_INTEGER_MIDI_REFERENCE ESTABLISHED`

### Hugging Face mirrors/collections

Searches surfaced mirrors of GuitarSet, GAPS, FLGD and mixed AMT collections. These are useful as scrapeable schema/metadata references, but the underlying corpus families are already closed/exposed in this project and were **not** reconsidered as untouched evaluation data.

The GuitarSet mirror is notable as a parser/schema fixture because its dataset viewer exposes note rows shaped like `{onset_s, offset_s, midi, string}` without requiring local audio download. This may be useful later for tooling tests, but must remain segregated from correctness evidence because GuitarSet is closed/exposed here.

## Full-history provenance remains unresolved

Current GitHub/code/commit searches can establish current-tree occurrences and commit-message matches, but commit-message search is not a full-history content proof. No claim of untouched lineage is made for RWC J007/J009/J010 yet.

A valid PRE still requires a defensible full-history provenance audit that covers corpus names, track IDs, DOI/record IDs, source repository identifiers, and distinctive file identities.

## State after Search 16

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Correctness scores: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Highest-value next steps

1. Continue searching archives, author pages, old QMUL/City research resources, supplementary files, code repositories and web archives for the **Benetos/Dixon hand-edited 23-second RWC guitar ground-truth MIDIs**, especially J007 and J009.
2. Search RWC 2.0 repository history/issues/PRs for affirmative per-track J007/J009/J010 timing-quality evidence rather than relying on absence from issue #258.
3. Continue public metadata-only discovery for other real-guitar corpora with manually authored/directly captured per-note onset + integer-MIDI truth.
4. Resolve full-history lineage before any RWC candidate can become PRE-ready.
5. Preserve current no-payload boundary.
