# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 9

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only

## Frozen boundary

No successor PRE/run is authorized. No candidate media/annotation payload is to be opened before the prospective gates are met. Archived V143/Gomyway remains untouched.

## New lead — Guitar Single-Note Recordings (Hugging Face `collegefishiesd/guitar-fretboard-notes`)

Public dataset-card metadata states:

- 390 isolated single-note guitar recordings;
- standard tuning, all six strings, frets 0–12;
- two players;
- acoustic and electric guitar sources, including clean electric recordings;
- raw 44.1 kHz / 32-bit float WAV recordings;
- labels include string, fret, note name, MIDI number, frequency and nominal clip duration;
- labels are derived from the filename convention `{source}_{string}_{fret}.wav`.

Prospective correctness status:

`REJECT_NO_AUTHORITATIVE_PERFORMED_ONSET_TRUTH`

The metadata provides intended string/fret/pitch identity but no deterministic timestamp for the actual note birth in each recorded waveform. A clip-level label or nominal clip duration is not an exact performed onset reference. Under the frozen gate, pitch identity alone is insufficient.

No dataset audio/payload was opened/downloaded.

## Other HCI / sensing / score-following results

### Smart-Guitar-Fretboard visual dataset

A 2025 Roboflow dataset/model surfaces fretboard images and segmentation classes such as fret bars, nut/capo and inlays. It is a computer-vision fretboard geometry dataset, not a guitar-audio corpus with performed-note onset+pitch truth.

Status: `REJECT_NO_PERFORMANCE_AUDIO_NOTE_REFERENCE`.

### AutoTab visual dataset

The surfaced AutoTab project uses a visual dataset for hand/fretboard/string object detection and then combines audio/vision in an application. The dataset itself does not provide a qualifying real guitar-audio corpus with authoritative exact note-birth + MIDI-pitch annotations.

Status: `REJECT_NO_QUALIFYING_AUDIO_NOTE_REFERENCE_DATASET`.

### MIREX score-following data

MIREX score-following pages document audio-to-score evaluation corpora with MIDI scores and reference alignments, including some human/manual alignment. However, the surfaced sets are general classical/orchestral/piano/ensemble data rather than a qualifying guitar population; the reference alignment task also does not by itself establish an eligible untouched guitar corpus for this boundary.

Status: `REJECT_NON_GUITAR / NOT_A_NEW_ELIGIBLE_GUITAR_POPULATION`.

### Web-score-following / ConcertCue dataset

The surfaced WAC 2024 project provides downbeat annotations for 18 external recordings and does not provide note-level performed onset + MIDI-pitch truth for a guitar population.

Status: `REJECT_DOWNBEAT_LEVEL_ONLY_AND_NON_GUITAR`.

### Hexaphonic guitar proof-of-concept projects

A surfaced hexaphonic-pickup project explicitly converts string signals to MIDI using YIN pitch detection. Even if recordings were packaged as a dataset, that MIDI would fail the frozen independent-reference gate for the same reason as GIHME/DoMP: pitch-estimation output is not independent correctness truth.

Status: `REJECT_REFERENCE_METHOD_NOT_INDEPENDENT`.

## Closed/exposed families not reopened

Search results also resurfaced GuitarSet, AG-PT-set, GAPS, GOAT and IDMT-family data. Their prior closed/exposed status is unchanged; none was reopened as untouched.

## GM watch

No authoritative GM Dataset release/version/file manifest or dataset-specific data license/research-use grant surfaced in this pass. GM remains unresolved and not PRE-ready.

## State after this pass

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Next discovery direction

Continue metadata-only search for datasets where the *reference acquisition mechanism itself* is independent of audio pitch estimation: direct fret/string electrical contacts, optical finger/string state with calibrated timestamps, manually reconciled per-note performance annotation, or other direct physical note-state sensing. Require an explicit actual-performance onset timestamp plus integer MIDI pitch before treating any isolated-note collection as a correctness candidate.
