# Astra real-domain failure localization proposal V1

Date: 2026-09-28
Status: **DESIGN ONLY — NEW P1/P2 ACCESS NOT AUTHORIZED**

## Purpose

Separate the two failure mechanisms revealed by the completed synthetic/real domain diagnostic:

1. P1 candidate pitch/state identity collapse;
2. P2 onset/attack localization collapse shared by baseline and candidate.

No model training or threshold changes are permitted.

## Frozen inputs

Use only:
- exact four P1 prepared direct-input crops;
- exact four P2 prepared direct-input crops;
- exact S9/S11 synthetic test population;
- frozen V3 baseline;
- frozen transfer candidate from run 36381769369.

P3 remains sealed.

## Diagnostic A — P1 state/pitch localization

At each eligible reference onset, for both models record:

- true string/fret/pitch;
- highest-probability active string/fret/pitch;
- true-state probability;
- silence probability;
- true-state rank among active fret classes;
- semitone error between true pitch and highest-probability predicted pitch;
- same-string fret error;
- whether the correct pitch appears on a wrong string;
- top-5 active-state candidates.

Aggregate:
- exact-string/fret accuracy;
- pitch-only accuracy ignoring string;
- median absolute semitone error;
- wrong-string/correct-pitch rate;
- true-class top-1/top-3/top-5 rates.

This determines whether P1 collapse is primarily pitch transposition, string assignment, fret identity, or general state uncertainty.

## Diagnostic B — P2 onset localization

For each eligible reference attack, for both models:

- onset probability at the annotated frame;
- maximum onset probability in +/- 1, +/- 2, +/- 4 frames;
- frame offset to the local maximum;
- whether threshold 0.50 is crossed anywhere in those fixed windows;
- local CQT frame-difference norm;
- positive spectral flux over 1, 2 and 4 frames;
- state correctness at the annotated frame and at the local onset-probability maximum.

Compare the same quantities on synthetic and P1 reference attacks.

This distinguishes:
- timing offset;
- weak attack novelty in P2 features;
- onset-head representation failure despite visible attack novelty.

## Guards

- optimizer steps: 0;
- model weights frozen;
- thresholds fixed 0.50 / 0.50;
- no threshold search or retuning;
- no normalization fed into either model;
- no model/seed selection;
- no automatic retry;
- no P3;
- no production claim.

## Decision branches

- **P1 mostly pitch-correct but wrong-string:** investigate string-conditioned state representation offline.
- **P1 systematic semitone/fret offset:** investigate synthetic fret/pitch mapping and feature alignment offline.
- **P1 diffuse low true-class ranks:** synthetic state representation is not real-domain compatible.
- **P2 local onset maxima appear near references but shifted:** timing/attack alignment problem.
- **P2 spectral novelty is weak relative to P1/synthetic:** input attack-domain mismatch.
- **P2 novelty is strong but onset logits remain weak:** onset representation/objective mismatch.
- **Mixed:** freeze mixed; do not tune on eight examples.

## Authorization boundary

Any execution requires fresh explicit P1/P2 access authorization.

P3 remains sealed.
