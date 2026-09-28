# Independent Real-Development Evaluation V1

Date: 2026-09-28  
Status: **NEW PROJECT VERSION — PROSPECTIVE DESIGN FROZEN BEFORE REAL-DATA ACCESS**

## Authorization

The user explicitly selected and authorized option 1 on 2026-09-28: a new **independent real-development evidence program**.

This project is not A2, not an A1 rescue, and not a reopening of P1/P2/P3.

## Question

Can the current frozen candidate family demonstrate useful real-domain transcription behavior on a **new, independently collected development set** that has not informed prior model, threshold, sampler, decoder, architecture, or gate decisions?

The goal is product-relevance evidence, not another synthetic mechanism study.

## Candidate boundary

No new model training is authorized by this project.

The evaluation is limited to already-frozen candidates:
1. frozen S11 clean-control candidate;
2. frozen A1 dual-encoder candidate package only if a durable checkpoint/weight identity is available without retraining;
3. otherwise, the highest-priority already-frozen candidate with durable weights and exact source/runtime identity.

A missing durable A1 weight artifact is **missing evidence**, not permission to retrain A1.

No candidate may be selected after looking at the new real-development results.

## Data independence rule

The new development set must be created or sourced **after this design is frozen** and must not include:
- P1;
- P2;
- P3;
- audio previously inspected, annotated, tuned against, or used to choose thresholds/architecture/loss/sampler/decoder settings;
- clips copied from the synthetic corpus or source-domain challenge.

The intake manifest must record provenance and an explicit no-overlap declaration before inference.

## Minimal capture scope

The smallest useful first tranche is **24 short clips**, prospectively partitioned before inference:

- **18 positive clips** containing guitar notes/events;
- **6 negative-only clips** containing no target guitar note events.

Positive clips should cover at least:
- 2 different physical instruments or clearly distinct capture chains;
- 2 different players or playing styles where practical;
- single-note material;
- repeated attacks;
- legato;
- palm-muted attacks;
- simple dyads/chords;
- at least one clean and one distorted/overdriven capture condition.

Target duration:
- 4–10 seconds per clip;
- total positive audio at least 90 seconds;
- total negative-only audio at least 30 seconds.

If these minima cannot be satisfied, stop and record the shortfall rather than weakening the contract after seeing results.

## Annotation contract

Before model inference, freeze for every positive clip:
- clip identity and SHA-256;
- target part (guitar/bass if applicable);
- event start time;
- pitch;
- string/fret when unambiguous and intentionally part of the annotation;
- optional offset only where reliably annotatable;
- annotator confidence flag.

Ambiguous string/fret labels are excluded from exact string/fret scoring but may remain eligible for pitch-onset scoring if pitch/onset are reliable.

No annotation may be edited in response to model output. Corrections for clear clerical mistakes must be versioned with a reason and occur before the affected result is interpreted.

## Evaluation slices

Primary:
1. pitch-onset precision;
2. pitch-onset recall;
3. pitch-onset F1;
4. negative-only false-positive events/sec.

Secondary:
5. exact string/fret top-1 at annotated events where label confidence is high;
6. pitch-only top-1 at those same events;
7. repeated-attack recall;
8. onset timing error distribution;
9. pitch-onset-offset F1 where offsets are reliable.

Report every numerator/denominator and total eligible audio duration.

## Frozen thresholds and processing

For any candidate whose historical contract used:
- state threshold 0.50;
- onset threshold 0.50;

retain those exact thresholds.

No:
- threshold sweep;
- calibration on the new set;
- gain-normalization experiment beyond the frozen frontend;
- decoder-window tuning;
- test-time augmentation;
- seed selection;
- candidate selection after results.

Preprocessing must use the exact frozen candidate frontend/source pin. Any incompatibility is a technical failure/limitation, not permission to alter the frontend mid-study.

## Admission interpretation

This V1 program does **not** define a production launch gate. It is a development evidence gate.

A result is considered **decision-useful** only if all of the following are true:
- all planned clips are present or any missing clips are explicitly declared before inference;
- exact candidate/source/runtime identities are recorded;
- thresholds and preprocessing are frozen;
- no overlap with P1/P2/P3 is found;
- all required metrics are finite and include counts/durations;
- no annotation was changed after seeing model output;
- every attempted candidate is reported.

Scientific interpretation is descriptive. Do not call this a product pass solely because one summary metric is high.

## Hard safety / cost boundary

Allowed under this project:
- design/spec/manifests;
- hashing and metadata checks;
- annotation tooling that does not inspect model output;
- bounded CPU inference on the frozen development set once the intake package is complete and independently verified;
- model-free validation/tests.

Not allowed without a new explicit decision:
- training or fine-tuning;
- A2;
- synthetic rescue experiments;
- P1/P2 reuse;
- P3 access;
- paid inference;
- production deployment;
- main mutation.

## Required pre-inference package

Before any real clip is run through a model, create and freeze:
- `docs/astra/INDEPENDENT_REAL_DEVELOPMENT_INTAKE_V1.json`;
- exact file hashes and durations;
- provenance/no-overlap declaration;
- annotation counts and confidence summary;
- candidate identity/source/runtime pins;
- exact evaluation script/source pins;
- a pure intake validator;
- an offline verification receipt with **0 model inferences**.

Only after that package passes may one bounded real-development evaluation be run.

## Stop rules

If intake independence fails:
- freeze failure;
- do not substitute P1/P2/P3;
- do not silently replace clips after seeing results.

If runtime identity or durable candidate weights are unavailable:
- freeze the limitation;
- do not retrain to recreate them.

After one evaluation:
- freeze all results;
- do not tune on the same set;
- do not automatically run a second real-development set;
- do not open P3.

## Current next task

Build the **intake package only**. Do not access or infer on real audio yet.

The next missing ingredient is a genuinely new real-development clip set satisfying this prospective contract. Once those files exist, hash and annotate them under the frozen intake schema, verify independence, and stop for the pre-inference verification checkpoint.
