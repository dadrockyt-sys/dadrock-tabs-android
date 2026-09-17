# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 18

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance and scrapeable text/manifest discovery only

## Frozen boundary

- No successor PRE or model/correctness run is authorized.
- Do not resume archived V143/Gomyway.
- Closed/exposed corpus families remain closed and cannot become "untouched" through mirrors/repackaging.
- No successor audio/media or annotation payload is to be opened before a candidate clears source/rights/reference/provenance gates and a new PRE is frozen.
- Required reference remains deterministic actual-performance onset + integer MIDI pitch tied to the recording and independent of Basic Pitch or other AMT/pitch estimation.

## Highest-value hunt — Benetos/Dixon hand-edited RWC guitar ground truth

Primary literature was re-checked for the manually edited RWC ground truth used by Emmanouil Benetos and Simon Dixon.

Confirmed from the 2011 ICASSP paper and Benetos PhD thesis:

- Twelve RWC classical/jazz excerpts were used for transcription evaluation.
- The original RWC MIDI was considered unsuitable because of note errors/omissions and unrealistic durations.
- Aligned ground-truth MIDI was created for the first 23 seconds of each recording using Sonic Visualiser for spectrogram visualization and MIDI editing.
- Evaluation compared system output to those ground-truth MIDI files at a 10 ms scale.
- RWC Jazz Nos. 6, 7, 8 and 9 are identified as guitar in the published test set; J007 and J009 overlap the strongest current-public RWC scrapeable candidates.

Public-location hunt performed across:

- QMUL/EECS Emmanouil Benetos transcription examples page;
- City Research Online publication records;
- QMUL thesis repository;
- MIREX multiple-F0 result pages/archives;
- general web/GitHub-indexed searches using distinctive RWC IDs, paper titles and the 23-second description.

The Benetos examples page publicly exposes original/synthesized example audio for RWC J007 and J009, but no hand-edited GT `.mid` files are linked. City/QMUL records expose papers/thesis, not the data artifact. MIREX public pages expose results and task metadata, not these GT MIDI files.

Status remains:

`TECHNICALLY_STRONG_MANUAL_23S_GUITAR_GT / EXACT_PUBLIC_GT_FILE_NOT_LOCATED / RIGHTS_FOR_DERIVED_GT_NOT_YET_ESTABLISHED / NOT_PRE_READY`

No audio or GT MIDI payload was opened.

## MIREX score-following reference format — ideal semantics, no new guitar corpus found

MIREX score-following documentation specifies reference alignment rows containing:

1. performed note onset time in the reference audio (ms),
2. note start time in the score (ms),
3. MIDI note number.

This is very close to the exact frozen truth semantics required here, and some MIREX score-following sets use human-generated or extensively manually corrected alignments.

However, the documented public evaluation populations surfaced in this pass are piano, woodwind/quartet and orchestral excerpts rather than a new qualifying guitar population. Guitar-specific score-following searches primarily resurfaced GAPS, which is already closed/exposed and was not reopened.

Status:

`REFERENCE_FORMAT_TECHNICALLY_IDEAL / NO_NEW_UNTOUCHED_QUALIFYING_GUITAR_POPULATION_FOUND`

## Scrapeable Hugging Face repackaging — not a successor

`ryangowe/guitar-chord-mix` is a current public CC-BY-4.0 Hugging Face package with WAV/JAMS pairs and six per-string `note_midi` annotation streams. Its dataset card explicitly marks `strum_annotated=true` when timing/duration are precise strum timing and false when onset was obtained by an unreliable energy-threshold path.

Its real-recording sources are GuitarSet, Guitar-TECHS, EGFxSet and Isolated Guitar Chords. GuitarSet, Guitar-TECHS and EGFxSet are closed/exposed historical families for this project and cannot regain untouched status through this repackaging.

The Isolated Guitar Chords source is a genuinely public CC-BY-4.0 real acoustic-guitar dataset with a structured strumming/fingering protocol, but its public source metadata supplies chord classes/protocols rather than authoritative note-by-note performed onset timestamps. The derived `guitar-chord-mix` card alone is not enough to prove that any precise per-string timing for those clips came from an independent authoritative manual reference.

Status:

`USEFUL_SCRAPEABLE_SCHEMA_AND_AUXILIARY_DATA / NOT_AN_UNTOUCHED_SUCCESSOR / ISOLATED_CHORD_NOTE_ONSET_PROVENANCE_NOT_ESTABLISHED`

No JAMS or audio payload was opened.

## TapToTab re-check

`TapToTab: A Pitch-Labelled Guitar Dataset for Note Recognition` describes real guitar notes played across strings/frets in clean/distorted conditions with manual note/pitch labels.

Publicly surfaced metadata still does not establish authoritative performed note-birth timestamps for each sample. Therefore it remains useful for pitch classification metadata but not for the frozen onset+pitch correctness requirement.

Status:

`AUXILIARY_PITCH_LABEL_DATA / NO_AUTHORITATIVE_PERFORMED_ONSET_TRUTH`

## State after Search 18

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Priority order after this pass

1. Continue exact-file hunting for the Benetos/Dixon 23-second hand-edited RWC guitar GT, especially J007/J009.
2. Continue validating RWC J007/J009/J010 current-public annotation timing authority without opening MIDI/audio payloads.
3. Search public score-following/alignment repositories specifically for guitar populations whose reference rows already encode performance-onset + MIDI note.
4. Keep Arty and GM on release/license watch.
5. Use scrapeable derivative corpora only as schema/source-discovery aids; do not treat mirrors as untouched successor provenance.
