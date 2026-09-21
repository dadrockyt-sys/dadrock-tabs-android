# Astra Guitar-TECHS TabCNN Training Candidate V1

Status: **registered design only; no media downloaded; no model training**
Date: 2026-09-21
Candidate: `astra_guitartechs_tabcnn_v1`

## Why this candidate exists

The published GuitarProFX TabCNN checkpoint remains technically compatible but execution-blocked because its training lineage includes DadaGP-derived symbolic performances whose commercial-use basis is not established for Jimmy PAIge. Astra will not weaken that gate.

Guitar-TECHS provides a separate path: the official project and paper explicitly release the dataset/code under **CC BY 4.0**. It contains over five hours of electric-guitar material from three professional performers, diverse guitars/rooms/recording chains, techniques, chords, scales, single notes and musical excerpts, with synchronized MIDI annotations per string.

This candidate will create **new Astra-owned weights from random initialization**. It must not deserialize, initialize from, distill from or otherwise depend on the blocked GuitarProFX checkpoint.

## Frozen publication identity

Official record: `https://zenodo.org/records/14963133`
Version: `v1`
License basis to preserve with attribution: `CC-BY-4.0`

Published archives currently selected:

| Performer | Archive | Published MD5 | Role |
| --- | --- | --- | --- |
| P1 | `P1_chords.zip` | `be9ef8bbdceb1912d565254e607a6d94` | development |
| P1 | `P1_scales.zip` | `9c0b98e8fb42a522df727ea8bf545e4f` | development |
| P1 | `P1_singlenotes.zip` | `ca0c4674dde3805574685a313f7c39eb` | development |
| P1 | `P1_techniques.zip` | `18634a41a6db5a8de10d07eb3122a872` | development |
| P2 | `P2_chords.zip` | `eb6f74dd19162237189281688ad7ad2e` | development |
| P2 | `P2_scales.zip` | `96664853872f51e5f8aa4447313b7cf5` | development |
| P2 | `P2_singlenotes.zip` | `40fbf03d8b04bb2cf42df20f36dc2254` | development |
| P2 | `P2_techniques.zip` | `f4189251ce50be25f06a173b2c2bba00` | development |
| P3 | `P3_music.zip` | `071ba80aecf00f4a31fbd167b3f22198` | sealed final generalization gate |

Exact byte counts and Astra SHA-256 digests are intentionally **not claimed yet**. They must be acquired from the official record and frozen before training media can be used.

## Leakage-resistant split

Do not random-split clips or capture channels.

Development fold A:
- train on all P1 underlying performances;
- validate on all P2 underlying performances.

Development fold B:
- train on all P2 underlying performances;
- validate on all P1 underlying performances.

For every underlying performance, DI / amplifier microphone / egocentric / exocentric captures must remain in the **same split**. Multiple views of the same performance are correlated observations, not independent examples.

After architecture, preprocessing, alignment rules, hyperparameters and acceptance criteria are frozen from the two development folds, a final candidate may be fit on P1+P2.

**P3 remains sealed.** `P3_music.zip` contains the twelve full musical excerpts and is reserved for a single-use source-disjoint final generalization measurement. P3 must not influence feature tuning, checkpoint selection, thresholds, augmentation, early stopping or acceptance-rule design.

## Label and alignment contract

- Ground truth source: synchronized per-string MIDI.
- The official record warns that signals may exhibit up to **100 ms** temporal misalignment. Alignment correction must therefore be deterministic and receipt-backed before frame labels are trusted.
- Do not infer fret numbers until tuning metadata/assumptions are frozen and validated. If tuning is unknown or non-standard, fail closed rather than silently applying standard tuning.
- Preserve a silent class per string.
- Technique labels may be retained as auxiliary evidence later, but v1 note/fret training must not make technique accuracy an unmeasured acceptance claim.

## Model contract

- Architecture family: TabCNN-compatible six-string fret-state model.
- Initialization: random only.
- Starting preprocessing contract: the already reproduced 22,050 Hz / 192-bin CQT / 24 bins-per-octave / 9-frame path, subject to **development-fold-only** experiments.
- Any preprocessing change must be frozen before P3 opens.
- Lead-vs-rhythm identity remains outside this generic-guitar model and continues to come from Astra role evidence.
- Bass is out of scope for this candidate.

## Required next receipts before training

1. Official archive byte-count + MD5 + Astra SHA-256 manifest.
2. Extracted-file inventory and duplicate/content-group manifest.
3. Deterministic performance-group IDs and performer-disjoint split receipt.
4. Audio/MIDI alignment correction algorithm + measured correction receipt.
5. Tuning/string-order/fret-label conversion receipt.
6. Exact training runtime/package/wheel lock and deterministic seed policy.
7. Training authorization and bounded resource budget.
8. Frozen development metrics and P3 opening rule.

No main, Production, paid delivery, or customer-facing model change is authorized by this design.
