# Guitar-TECHS Label, Alignment and Training Contract V1

Status: **frozen design; no Guitar-TECHS archive body downloaded or opened; no model trained**
Date: 2026-09-21
Candidate: `astra_guitartechs_tabcnn_v1`
Receipt: `docs/astra/GUITARTECHS_LABEL_ALIGNMENT_TRAINING_CONTRACT_V1.json`
Receipt SHA-256: `09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f`

## Label semantics

The pinned TabCNN source defines six independent softmax groups. With a 19-fret GuitarProfile, each string has 21 classes: frets 0–19 plus one silence class. The pinned `SoftmaxGroups.get_loss()` converts tablature silence state `-1` to the final class, therefore:

- tablature states: `-1` = silence, `0..19` = fret;
- softmax targets: `0..19` = fret, `20` = silence;
- total logits: `6 × 21 = 126`.

Astra must not assume the upstream default E2/A2/D3/G3/B3/E4 tuning for Guitar-TECHS. That default is only evidence about the source model, not evidence about each dataset performance. Before pitch-to-fret conversion, the actual six-track-to-string mapping and tuning must be verified from authoritative metadata or the later P1/P2 development archives.

Missing/invalid tuning, out-of-range frets, or simultaneous overlapping pitches on one physical string **abstain/mask**. They are never clipped or relabeled as silence.

## Technique scope for v1

Primary fret-state training may use chords, scales, ordinary single notes and palm-mute material once file semantics are verified.

Vibrato, pinch harmonics, natural harmonics and bendings remain auxiliary/held-out until their MIDI/pitch-bend semantics are inspected. Technique metadata cannot silently override fret truth.

## Alignment policy

Zenodo warns of up to 100 ms signal misalignment. P3 may not influence alignment design.

For each verified P1/P2 recording-session + capture-path group:

- aggregate six-track MIDI note onsets;
- derive a deterministic audio onset envelope;
- search integer lag from -100 to +100 ms at 1 ms steps;
- require at least 30 MIDI onset groups;
- after correction, require >=80% matched within 20 ms and median absolute residual <=10 ms;
- perform five deterministic bootstrap/stratified lag estimates and require lag MAD <=5 ms;
- never apply >100 ms absolute correction;
- if any gate fails, exclude that recording group and record alignment abstention rather than force a shift.

The exact implementation still requires a receipt once P1/P2 media are authorized and acquired.

## Initial training contract

The first development contract follows the pinned TabCNN training source where useful: Adadelta, learning rate 1.0, batch size 32, and at most 2,500 iterations per performer-disjoint fold, with 50 validation checkpoints. Astra uses seed `20260921` and requires deterministic algorithms.

Runtime identity reuses the already frozen Linux/Python 3.10.15 / PyTorch 1.11.0+cpu stack and wheel manifest. Initialization is random only. The blocked GuitarProFX weights are forbidden.

No paid compute or real training is authorized by this contract. A CPU synthetic backward/optimizer smoke must pass first.

## Development evaluation

Both P1->P2 and P2->P1 folds must report:

- onset+string+fret precision, recall and F1;
- note-event completeness;
- frame string+fret accuracy;
- abstention rate;
- per-content-class results;
- cross-performer consistency.

Frame accuracy alone cannot establish success. Numeric acceptance thresholds are intentionally **not frozen yet**; they must be established from development baselines before P3 is opened. P3 remains sealed and cannot affect preprocessing, alignment, hyperparameters, threshold selection or early stopping.

No main/Production/customer-delivery authority is granted.
