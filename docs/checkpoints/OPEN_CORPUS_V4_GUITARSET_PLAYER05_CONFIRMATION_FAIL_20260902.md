# Open-Corpus V4 GuitarSet Player-05 Confirmation — FAIL

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Terminal scientific boundary

The preregistered one-shot player-`05` confirmation for **`H72-D035`** completed and **failed** the frozen confirmation gate.

Status: **`V4_PLAYER05_CONFIRMATION_FAIL`**.

This is a scientific failure, not a mechanical/runtime failure. The V4 hypothesis is terminal. Do not rerun, weaken the confirmation gate, try a different V4 family member on player `05`, or tune `H72-D035` using this confirmation result.

Prospective GuitarSet players `00/01/03` remain sealed and must not be opened for V4.

## Frozen confirmation contract

Preregistration:
- `docs/checkpoints/OPEN_CORPUS_V4_GUITARSET_PLAYER05_CONFIRMATION_PREREGISTRATION_20260902.md`;
- creation commit `3759e73563c5fc93f67407e5e3f9ea37a4e3d584`.

Frozen rule tested:
- config `H72-D035` only;
- ordinary V2 octave-down exactly 12 semitones;
- baseline MIDI pitch >=72;
- Basic Pitch event duration <=0.35 s.

Frozen confirmation scorer:
- `validation/open_corpus/confirm_guitarset_v4_player05.py`;
- blob `794011aa78524226ec47e74ca8dd91008eef629a`.

Frozen gate required all:
1. event-count identity;
2. at least one changed pitch;
3. primary macro F1 gain >0 pp;
4. primary combined micro F1 gain >0 pp;
5. strict50 combined micro non-regression;
6. no player-05 track with negative primary TP delta.

## Run identity and guards

Real one-shot confirmation workflow:
- workflow creation commit `ae536a761e388e902dbacb0f740305517a81f2a7`;
- run `33584451308`;
- job `100105524472`;
- job conclusion: **SUCCESS**.

The workflow succeeded mechanically and produced the intended scientific classification.

Pre-reference guards passed:
- original frozen candidate artifact identity reverified;
- candidate manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83` reverified;
- all 177 candidate JSON hashes reverified before references;
- player-05 candidate count = 60;
- candidateRegenerated=false;
- Basic Pitch not importable;
- no audio/WAV files.

Reference boundary:
- verified GuitarSet `annotation.zip` identity;
- exactly 60 player-05 JAMS extracted;
- no `02/04/00/01/03` JAMS in the confirmation reference workspace;
- prospective players remained unread.

## Exact confirmation result

Confirmation population:
- tracks: **60**;
- reference note events: **8,715**;
- baseline predicted events: **9,778**;
- changed pitches under `H72-D035`: **91**;
- event-count identity: **true**.

Primary 100 ms baseline:
- TP: **7,306**;
- macro F1: **82.56410344391738%**;
- combined micro F1: **79.01368085221435%**.

Primary 100 ms `H72-D035`:
- TP: **7,301**;
- macro F1: **82.49393805207504%**;
- combined micro F1: **78.95960633753313%**.

Exact primary deltas:
- TP: **-5**;
- macro F1: **-0.0701653918423375 pp**;
- combined micro F1: **-0.05407451468121849 pp**.

Strict50 baseline:
- TP: **7,180**;
- macro F1: **81.02444064016599%**;
- combined micro F1: **77.65100308224734%**.

Strict50 `H72-D035`:
- TP: **7,175**;
- macro F1: **80.95427524832364%**;
- combined micro F1: **77.59692856756611%**.

Strict50 combined micro delta: **-0.0540745146812327 pp**.

Primary track-level TP direction counts:
- positive tracks: **1**;
- neutral tracks: **56**;
- negative tracks: **3**.

## Gate outcome

Passed:
- event-count identity;
- at least one pitch changed.

Failed:
- primary macro gain strictly positive;
- primary combined micro gain strictly positive;
- strict50 combined micro non-regression;
- no-player05-track-primary-TP-loss.

Overall qualification: **false**.

## Frozen report identities

- confirmation report SHA256 `3feb63042c670690221901906045520f17faa01d02a461c01b805ea68867d722`;
- artifact name `guitarset-v4-player05-confirmation`;
- artifact ID `9829578804`;
- artifact ZIP SHA256 `556d301e3466a9f6064d52ccd3e37410b492fac147e20e7833ed8bde65dff300`.

## Consequence

V4 is **CLOSED / TERMINAL** for this hypothesis.

Forbidden:
- rerun player-05 confirmation;
- lower/alter the frozen gate;
- promote `H72-D025` or `H72-D030` after `H72-D035` failed;
- use player-05 confirmation outcomes to retune V4 and call it confirmation;
- open `00/01/03` for V4.

A future **new** development phase may explicitly reclassify `02/04/05` as development and reserve `00/01/03` as the untouched prospective test set, but that must be declared as a new version/methodological boundary before player-05 outcomes are mined for new model design.

## Counters at closure

- exact V4 discovery-family score calls: **1**;
- player-05 V4 reference read: **true**;
- player-05 V4 confirmation score calls: **1**;
- V4 confirmation status: **FAIL / TERMINAL**;
- GuitarSet prospective evaluation processed: **false**;
- GuitarSet prospective evaluation score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GPU/CUDA/Modal: **none**;
- `main` / Production: **untouched**.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
