# Songsterr Fresh Successor Research Charter V6

Status: **AUTHORIZED SUCCESSOR / SYNTHETIC + METADATA DEVELOPMENT ONLY**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Authorization and scope

The user authorized continued successor research on 2026-09-13 and established a standing compute rule: normal research, coding, GitHub work, CPU runs, checkpoints, tests, and ordinary Vercel work may proceed at assistant discretion; explicit user authorization is required before any Modal run, Vercel heavy-GPU run, or L4 GPU run.

This charter opens V6 successor research only. It does **not** reopen archived V143/Gomyway, GOAT/reference scoring, duration work, protected-song execution, Production, or any rejected V1-V5 admission line.

Authority remains fail-closed:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song remains embargoed.

## Closed / revealed correctness corpora

The following correctness evidence is already revealed or contaminated for successor method selection and MUST NOT be used to tune V6 constants, thresholds, feature choices, model-selection choices, matching rules, or admission gates:
- FLGD V5 official result;
- IDMT V4 correctness;
- GuitarSet V3 correctness;
- protected-song historical outcomes.

FLGD MUST NOT be rerun under the V5 preregistration and is not an untouched V6 admission holdout.

Historical results may be cited only to establish that prior method families failed and to prevent accidental repetition of those method families.

## Scientific gap motivating V6

V1/V2/V4/V5 are dominated by post-onset steady-state evidence. V5 in particular asks whether the selected MIDI is necessary to explain later polyphonic harmonic spectra across three post-onset windows.

V6 investigates a different physical question:

> Did the selected pitch acoustically **begin at the decoded onset**, producing a candidate-specific onset innovation that was not already present immediately before the event?

This is an onset-synchronous birth-signature problem, not a V5 threshold retune.

The motivation is grounded in established complex-domain onset-detection work: onset evidence can be represented by deviations of complex STFT magnitude/phase from predictions based on preceding frames, rather than by steady-state energy alone.

## Candidate family A — onset-synchronous complex-harmonic birth corroboration

Synthetic development may implement a reference-blind CPU method using only:
- mono audio;
- sample rate;
- existing event onset;
- existing selected integer MIDI.

It may compute short-time complex spectra spanning frames immediately before and after the event onset and measure candidate-specific harmonic innovation. Candidate design goals:
- require evidence localized to the event onset rather than merely persistent afterward;
- include the selected fundamental and multiple physically related harmonics;
- contrast post-onset innovation against pre-onset state;
- reject octave/harmonic aliases and already-present tones;
- preserve the Basic Pitch event identity and MIDI exactly;
- use no reference truth, filename/corpus identity, performer/style identity, Basic Pitch confidence/activation surface, duration/end, next-onset/future-event logic, or downstream string/fret decisions.

Exact frame sizes, hops, harmonic counts, score definitions, and decision rules are **not frozen by this charter**. They may be chosen or amended only from mathematical/signal-processing reasoning and deterministic synthetic fixtures before any new real-corpus correctness exposure. Once the V6 final method preregistration is frozen, no such tuning is permitted from its admission holdout.

## Candidate family B — independent guitar-model agreement

Synthetic/engineering development may also evaluate whether an independently trained guitar transcription model can serve as a second reference-blind evidence channel.

A candidate checkpoint is the MIT-licensed `xavriley/midi-transcription-models` GAPS guitar checkpoint (`guitar-gaps.pth`). It must be pinned by exact repository revision and model SHA-256 before use. Because that checkpoint is associated with the GAPS training/benchmark line, GAPS itself MUST NOT be used as an untouched admission holdout for any V6 method that uses that checkpoint.

Initial model engineering, if performed, is CPU-only unless the user separately authorizes Modal, Vercel heavy-GPU, or L4 execution.

No independent-model output may rewrite Basic Pitch events or MIDI. At most it may act as an admission corroborator under a later frozen V6 contract.

## Synthetic-development boundary

Before any V6 real-corpus correctness run, synthetic fixtures must exercise at least:
- clean monophonic notes across low/mid/high guitar range;
- detuning inside a semitone cell;
- attack noise;
- silence and low-level noise;
- truncated pre-onset and post-onset context;
- a pitch already sounding before the candidate onset (must not look newly born);
- a lower note whose harmonic coincides with the selected MIDI (octave/harmonic alias trap);
- a true selected note entering over an already-sounding lower note;
- simultaneous dyads and triads;
- neighboring-semitone competition;
- selected-note reattack;
- unrelated transient at the selected onset;
- exact event/MIDI identity preservation.

Synthetic fixtures may be expanded whenever a mathematically distinct failure mode is discovered, provided this occurs before real-corpus correctness exposure and is checkpointed.

Synthetic success is not admission evidence.

## Holdout selection boundary

No V6 real correctness corpus is selected by this charter.

Metadata/license inventory may be performed without correctness scoring. Current candidate:
- **Guitar-TECHS**: real electric-guitar performances, per-string MIDI annotations, CC BY 4.0. Its published materials note possible signal/MIDI misalignment up to 100 ms for some recording paths. Therefore it is only a candidate until a separate, reference-blind alignment-semantics/inventory audit can freeze an authoritative audio path and any permitted deterministic alignment correction before correctness scoring.

GuitarDuets is not currently preferred because note-level MIDI annotations are provided for synthesized duets rather than the real-recording subset used for the strongest external-realism claim.

GAPS is not adopted as a V6 holdout at this stage. Its public licensing statements are inconsistent across distribution surfaces, and it is also unsuitable as an untouched holdout if the GAPS-trained guitar model is used in V6.

Any future holdout must have:
- unambiguous permitted use;
- exact immutable source/version identity;
- real guitar audio if used for external admission;
- authoritative note-onset/pitch truth;
- frozen alignment semantics before correctness;
- no known overlap with successor model training when independent-model evidence is used.

## Required order before any V6 admission decision

1. freeze this successor research charter;
2. implement deterministic synthetic fixtures and candidate methods only;
3. run controlled synthetic/engineering CI with no new real-corpus correctness;
4. select one final V6 method and freeze its exact implementation/runtime;
5. select and inventory an untouched external holdout using metadata/structure only;
6. freeze alignment/reference semantics and exact scoring/matching/uncertainty/admission gates;
7. run one official external correctness evaluation;
8. write immutable result record before interpretation;
9. conduct a separate policy review.

## Explicit prohibitions

Until a later frozen checkpoint changes scope, do not:
- inspect FLGD event-level correctness to design V6;
- rerun/tune V5 on FLGD;
- rerun/tune V3 on GuitarSet or V4 on IDMT;
- lower the existing 0.9900 product-policy precision standard merely because prior methods failed;
- perform broad real-corpus threshold/optimizer sweeps;
- train/fine-tune on a proposed admission holdout;
- use protected-song results for successor design;
- resume duration research;
- resume archived V143/Gomyway/GOAT/reference scoring;
- promote any V6 event to customers before untouched external validation and separate policy approval;
- start a Modal, Vercel heavy-GPU, or L4 run without explicit user authorization.
