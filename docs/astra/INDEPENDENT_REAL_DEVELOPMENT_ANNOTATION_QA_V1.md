# Independent Real-Development Annotation QA V1

Date: 2026-09-28  
Status: **PRE-INFERENCE QA REQUIRED — DO NOT RUN CANDIDATE MODEL**

## What passed

The populated intake is structurally valid under the frozen V1 validator:
- 24 clips;
- 18 positive;
- 6 negative-only;
- 145.415094 s positive evaluation audio;
- 41.366531 s negative-only evaluation audio;
- all seven required coverage categories present;
- candidate/source/threshold pins present;
- 0 model inference;
- 0 optimizer steps;
- P1/P2/P3 remain closed.

The model-free annotation draft contains 105 pitch/onset labels:
- 81 high-confidence;
- 5 medium-confidence;
- 19 low-confidence.

## Why scientific inference is still blocked

The draft annotation method uses spectral-flux onset detection plus YIN fundamental estimation. YIN is monophonic.

That is acceptable for drafting single-note labels, but it can under-annotate or misrepresent simultaneous notes in chordal/polyphonic guitar. A structurally valid manifest is therefore **not yet a scientifically complete reference set**.

Mandatory human QA is required at minimum for the explicitly chordal/polyphonic clips:
- P01 — dry riff / chord material;
- P02 — clean funky/rock material;
- P05 — clean Midwest-emo melodic/chordal phrase;
- P06 — alternate Midwest-emo phrase;
- P07 — hard-rock guitar jingle;
- P10 — Bossa Nova electric-guitar chord sequence;
- P13 — Em guitar chord strum;
- P16 — electric guitar strumming.

Additional conservative review is recommended for clips with very sparse machine annotations relative to duration:
- P03;
- P08;
- P11;
- P12;
- P18.

## Human QA contract

Review audio **without viewing candidate-model output**.

For each true target onset:
1. add every reliably audible pitch;
2. use MIDI pitch;
3. preserve onset time relative to the frozen evaluation crop;
4. mark confidence high / medium / low;
5. add string/fret only when unambiguous;
6. do not infer a fingering merely because a pitch is playable in one location.

For chordal events, simultaneous pitches should have the same onset time when appropriate.

If a pitch cannot be labeled reliably, keep it out and document the ambiguity. Do not use candidate output to resolve uncertainty.

## Current decision

**Structural intake validation: PASS.**  
**Scientific annotation completeness: NOT YET PASSED.**  
**Candidate-model inference authorization: BLOCKED by the frozen pre-inference QA rule.**

No threshold tuning, candidate selection, retraining, A2, P1/P2 reuse, or P3 access is permitted as part of this QA.

## Next action

Complete human QA of the reference annotations, then:
1. freeze the corrected annotation file;
2. update the intake;
3. rerun the pure validator;
4. freeze a zero-inference verification receipt with both structural and scientific readiness marked true;
5. only then run the single bounded real-development evaluation.
