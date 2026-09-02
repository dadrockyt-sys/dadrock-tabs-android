# Open-Corpus P3 Reference-Blind Octave Correction — Preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Scientific question

Can the frozen V2 harmonic octave selector improve a real **reference-blind audio-to-note proposal stream** when it is no longer handed a reference-centered candidate neighborhood?

This is the bridge between the controlled 558/558 V2 result and an actual transcription pipeline. The experiment is V169-style public-corpus development only and cannot modify V168.

## Freeze timing / unseen evidence statement

This preregistration is created after a **metadata/path-only** inventory of `P3_music.zip` but before:
- any P3 MIDI file is extracted or parsed;
- any P3 reference note event is read;
- any P3 Basic Pitch inference is run;
- any P3 baseline/corrected candidate is generated;
- any P3 transcription score is computed.

Metadata inventory checkpoint: `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P3_METADATA_INVENTORY_20260902.md`.

## Dataset and complete fixed evaluation set

Public Guitar-TECHS, Zenodo record `14963133`, P3 musical excerpts.

Archive:
- `P3_music.zip`
- official MD5 `071ba80aecf00f4a31fbd167b3f22198`
- observed SHA256 `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`
- public project site states CC BY 4.0.

Use **all 12** indexed works `01` through `12`. No work may be excluded after seeing a candidate or score unless a pre-existing file-integrity failure prevents decoding. Any such integrity failure is reported and the experiment becomes inconclusive rather than silently changing the set.

For each work evaluate both public capture chains:
- `directinput_XX.wav`;
- `micamp_XX.wav`.

Reference binding is fixed by the same two-digit index to `midi_XX.mid`.

Total planned capture-work units: **24**.

Ego/exo MP3 captures are out of scope for this first bridge and cannot be substituted after results.

## Reference-blind proposal engine — frozen before P3 inference

Baseline proposal engine: **Spotify Basic Pitch 0.4.0**, CPU/TFLite.

Required model SHA256:
- `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.

Python: 3.10.x. TFLite runtime: 2.14.0.

Use Basic Pitch 0.4.0 `predict(...)` defaults exactly:
- onset threshold `0.5`;
- frame threshold `0.3`;
- minimum note length `127.70 ms`;
- minimum frequency `None`;
- maximum frequency `None`;
- multiple pitch bends `False`;
- melodia trick `True`;
- MIDI tempo default `120` (not outcome-relevant to note-event seconds).

No P3-derived threshold change is allowed.

For each Basic Pitch note event preserve:
- start time seconds;
- end time seconds;
- integer MIDI pitch;
- amplitude/confidence.

Pitch-bend arrays are not used in this bridge. They may be retained as metadata but cannot affect correction/scoring.

## Frozen V2 octave correction

The scoring implementation must be imported from the frozen V2 evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`.

The shared harmonic helper must remain blob:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`
- Git blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

For each already-generated Basic Pitch event of pitch `p`:
1. define audio-only candidates `{p-12, p, p+12}`;
2. use the frozen V2 `best_candidate_window(...)` / candidate score with **alignment = 0.0 seconds**, because Basic Pitch event times are already expressed in the same audio timeline;
3. preserve the frozen V2 frame deltas, FFT bands, harmonic weights, root exponent, lower-odd penalty, and score formula unchanged;
4. select maximum V2 score; exact ties choose the smallest MIDI pitch, as in frozen V2;
5. replace only the event MIDI pitch with the selected candidate;
6. preserve event start, end and amplitude unchanged;
7. do **not** add, delete, merge, deduplicate, split or time-shift events.

Therefore baseline and corrected streams must have exactly identical event counts per capture-work unit.

## Hard reference-isolation boundary

Candidate generation and scoring must be separate jobs/process boundaries.

Candidate job:
1. download and verify the exact P3 archive;
2. extract **only** the 24 DI/micAmp WAVs;
3. remove the source ZIP before any candidate-generation Python process starts;
4. run Basic Pitch + frozen V2 correction using audio only;
5. write baseline and corrected JSON note-event streams;
6. hash every prediction file and a canonical freeze manifest;
7. upload the frozen candidate artifact.

No MIDI/reference file is extracted in the candidate job.

Scoring job:
1. starts only after the candidate artifact is finalized;
2. downloads the candidate artifact and verifies every frozen candidate hash;
3. separately downloads and verifies the exact P3 archive;
4. extracts **only** the 12 `midi_XX.mid` reference files;
5. scores the already-frozen baseline and corrected streams without modifying them.

The scoring job does not rerun Basic Pitch or V2 candidate generation.

## Reference scorer — frozen rules

Aggregate all non-drum notes across all instruments/strings in each `midi_XX.mid` reference.

Primary note correctness:
- MIDI pitch must match exactly;
- one-to-one onset matching;
- note offsets are ignored for this first bridge;
- no global or per-song reference-driven time shift is permitted.

Report two onset tolerances:
- **100 ms primary**, chosen prospectively because Guitar-TECHS documents capture/MIDI misalignment up to approximately 100 ms;
- **50 ms strict secondary**.

For a fixed MIDI pitch, matching must maximize one-to-one cardinality between sorted predicted and reference onset sequences within the tolerance. Each predicted/reference note may be matched at most once.

Per capture-work unit report TP/pred/ref, precision, recall and F1 for baseline and corrected streams at both tolerances.

Aggregate report:
- micro precision/recall/F1 over all events;
- macro F1 as the unweighted mean of the 12 work F1 values separately for DI and micAmp;
- combined macro F1 as the unweighted mean over all 24 capture-work units;
- count of changed pitches;
- event-count identity check.

## Prospectively frozen success classification

At **100 ms** let `deltaMacroPP = corrected combined macro F1 - baseline combined macro F1`, in percentage points.

Status = `REFERENCE_BLIND_OCTAVE_CORRECTION_PASS` only if ALL are true:
1. `deltaMacroPP >= +0.25pp`;
2. corrected 100 ms micro F1 is not below baseline separately on DI and micAmp;
3. corrected 50 ms combined micro F1 is not below baseline;
4. event counts are exactly identical baseline vs corrected in every unit;
5. every candidate/reference artifact/hash guard passes.

Status = `REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL` if ANY is true:
- corrected 100 ms combined macro F1 is more than `0.25pp` below baseline;
- corrected 100 ms micro F1 is more than `0.10pp` below baseline on either capture chain;
- corrected 50 ms combined micro F1 is more than `0.10pp` below baseline;
- event-count identity fails;
- a frozen identity/reference-isolation guard fails.

Otherwise status = `INCONCLUSIVE_NO_MATERIAL_GAIN`.

No threshold may be changed after any P3 candidate/score is observed.

## Interpretation limits

A PASS would establish that the frozen V2 harmonic signal can improve a **reference-blind Basic Pitch proposal stream** on previously unused polyphonic musical excerpts from a third guitarist/capture setup. That would be substantially closer to the DadRock `/ai-tab` goal than the controlled single-note ranking result.

It still would not equal complete tablature transcription: this bridge does not solve string/fret assignment, note-duration scoring, rhythmic notation, bends/articulations, source separation, or full Guitar Pro rendering.

A FAIL/INCONCLUSIVE result cannot be repaired by tuning on P3. Any V3 must be separately preregistered and should move to fresh evidence where possible.

## V168 isolation / safety

- V168 prospective reference-facing score calls: **0** before this experiment and must remain 0 throughout;
- V168 Policy A/B modified: **false**;
- GOAT holdout selection modified: **false**;
- GOAT restricted bytes read: **false**;
- GPU/CUDA/Modal: **forbidden without fresh explicit user authorization**;
- `main` / Production: **must remain untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
