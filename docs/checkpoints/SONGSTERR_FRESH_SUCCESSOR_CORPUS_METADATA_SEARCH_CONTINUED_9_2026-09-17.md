# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 10

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only

## Frozen boundary

- No successor PRE or model/correctness run is authorized.
- Do not resume archived V143/Gomyway.
- Do not reopen closed/exposed GuitarSet, IDMT, FLGD/François Leduc, GAPS, GOAT, EG-IPT, Guitar-TECHS, AG-PT, EGDB, EGSet12 or other frozen historical lines as “untouched.”
- No successor corpus media or annotation payload may be opened before a candidate clears the prospective source/rights/reference/provenance gates and a new PRE is frozen.
- Reference truth must contain deterministic actual-performance note onset plus integer-MIDI pitch and must be independent of Basic Pitch or any other AMT/pitch-estimation output.

## New lead — Multimodal Electric Guitar Data (University of Oslo)

Public Zenodo metadata identifies `Multimodal Electric Guitar Data`, DOI `10.5281/zenodo.6470236`, version `v1`, with 36 student/semi-professional electric guitarists performing basic sound-producing actions and free improvisations. The dataset includes EMG, motion capture, video and audio and has a stable public Zenodo release.

Prospective correctness status:

`REJECT_NO_NOTE_LEVEL_ONSET_PLUS_MIDI_REFERENCE`

Reason: the public description and related work establish synchronized multimodal performance signals and action classes, but not deterministic note-by-note actual-performance onset timestamps paired with integer MIDI pitches. EMG/MoCap/audio synchronization alone does not create note correctness truth.

No dataset payload was opened/downloaded.

## New lead — University of Manchester AI guitar-assistant multimodal recordings

The 2025 Frontiers paper `Ground truths: challenges and opportunities in developing an AI guitar assistant` describes guitarist exercise recordings at the NOVARS Research Centre using two Myo armbands, frontal video and microphone audio, with custom Max patches for synchronized capture. Its data-availability statement says raw data supporting the article will be made available by the authors.

Prospective correctness status:

`REJECT_NO_PUBLIC_STABLE_NOTE_EVENT_DATASET_AND_NO_EXACT_NOTE_REFERENCE`

Reason: the paper describes exercise-level multimodal capture for technique/pedagogy research, not an authoritative public release with deterministic note onset + MIDI-pitch labels. The raw-data statement is not an immutable dataset/version/file manifest or note-event annotation specification.

No raw data was requested or opened.

## New lead — Fretiq (2026)

ArXiv `2607.18303`, `Fretiq: Browser-Native Electric Guitar String Classification via Engineered Spectral Features and Held-Out Free-Play Evaluation`, describes a single-guitar/single-player electric-guitar string classifier. The system records DI audio and evaluates string identity; pitch is detected in the pipeline using the McLeod Pitch Method/Pitchy and used to constrain candidate strings. A held-out free-play session has manual string labels.

Prospective correctness status:

`REJECT_TASK_REFERENCE_NOT_NOTE_BIRTH_PLUS_INDEPENDENT_MIDI_TRUTH`

Reason: the target labels are string classes, not exact note-birth + integer-MIDI note events. Pitch used by the system is itself audio pitch-estimation output, which cannot supply independent correctness truth under the frozen gate.

No Fretiq audio/training data was opened.

## New lead — 2026 MAAL annotated co-performance corpus

The July 2026 Organised Sound article `Personalising behaviours of the multi-agent autonomous looper with a corpus of annotated co-performances` describes audio recordings paired with binary segment-selection/looping-decision annotations from co-improvisation sessions.

Prospective correctness status:

`REJECT_ANNOTATIONS_ARE_LOOPING_DECISIONS_NOT_NOTE_EVENTS`

Reason: the corpus annotation `D[m]` represents whether a time segment should be selected for looping. It does not encode deterministic performed-note onset + MIDI pitch and the study population spans several instruments rather than a qualifying guitar note corpus.

No supplementary corpus payload was opened.

## Closed/exposed families resurfaced but not reopened

Fresh searches resurfaced:

- François Leduc Guitar Dataset / FLGD, including its newer Hugging Face distribution. The underlying high-resolution alignment method aligns commercial score transcriptions to transcription-model activations; FLGD also remains explicitly closed in this project.
- GAPS, including the 2026 Zenodo v2/Hugging Face update. GAPS remains historically exposed/closed and was not reconsidered as untouched.
- IDMT-SMT-Guitar and GuitarSet. Both remain closed historical families.
- GOAT, EG-IPT, AG-PT and EGDB-family records. Their frozen status is unchanged.

No payload from any closed/exposed family was opened.

## GM watch

No authoritative GM Dataset public package, immutable release/file manifest, or dataset-specific license/research-use grant was established in this pass. GM remains:

`UNRESOLVED_STABLE_PUBLIC_RELEASE_AND_DATASET_RIGHTS / REFERENCE_ALIGNMENT_POTENTIALLY_ACCEPTABLE_FROM_METADATA / NOT_PRE_READY`

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

Continue metadata-only discovery for datasets whose note reference is obtained independently of audio pitch estimation: direct fret/string contacts, optical or electrical finger/string state with calibrated timing, manually verified note-by-note performance annotation, or synchronized symbolic capture whose event source is demonstrably independent of AMT/pitch tracking. Prefer 2025–2026 institutional data repositories and supplements. If no such corpus exists, preserve the unresolved state rather than weakening the gate.
