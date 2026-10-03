# YAMNet Zero-Shot Recognizer Result V1

Date: 2026-10-02
Run ID: 37081779592
Status: **SUCCESSFUL ZERO-SHOT FEASIBILITY PASS**

Artifact:
- id: 11258687346
- digest: `sha256:b097366a43d0e1ee4d095234065fe0ced4d5c1861666df3d0fcc467a34b8ae33`

## Summary

- 6 guitar fixtures
- 6 bass fixtures
- 2 controls
- guitar vs bass evidence correct on guitar: **6/6**
- bass vs guitar evidence correct on bass: **5/6**
- control guitar evidence mean: **0.000543**
- control bass evidence mean: **0.000286**

The controls are orders of magnitude below most real guitar/bass fixtures.

## Strong guitar examples

- G09: guitar 0.3614 vs bass 0.0087
- G10: guitar 0.1546 vs bass 0.0282
- G14: guitar 0.2113 vs bass 0.0152
- G21: guitar 0.1340 vs bass 0.0043
- G23: guitar 0.4072 vs bass 0.0582

G13 is an important low-evidence guitar counterexample:
- guitar 0.0000995
- bass 0.0000390
- correct relative winner, but absolute evidence is close to the controls.

## Bass examples

Correct bass winners:
- B01: bass 0.5499 vs guitar 0.4116
- B06: bass 0.1845 vs guitar 0.1009
- B08: bass 0.2690 vs guitar 0.1906
- B20: bass 0.3573 vs guitar 0.2398
- B26: bass 0.7338 vs guitar 0.5968

Ambiguous/missed bass:
- B12 picked bass note: guitar 0.1557 vs bass 0.1390

This is a useful counterexample: a hard winner-take-all guitar/bass rule would misclassify it.

## Controls

- N01 drums: guitar 0.000797, bass 0.000566
- N04 speech: guitar 0.000288, bass 0.000007

These are very low compared with most true string-instrument fixtures, supporting an absolute-evidence concept for "other".

## Decision

YAMNet is promising as an **independent evidence source**, but V1 is not sufficient for a hard three-way gate.

Do not use only:
- guitar > bass => guitar;
- bass > guitar => bass.

Instead the next gate should combine:
1. absolute string-instrument evidence;
2. guitar-vs-bass margin;
3. separator-output diagnostics;
4. an explicit uncertain state.

Proposed qualitative behavior:
- very low guitar and bass evidence -> other / low-confidence;
- strong absolute evidence + clear margin -> class agreement;
- strong absolute evidence + small margin -> uncertain guitar/bass;
- low absolute evidence but expected target exists -> preserve raw stem, do not destructively suppress;
- recognizer disagreement alone is not enough to delete a stem.

B12 is the key ambiguous-bass fixture.
G13 is the key low-evidence true-guitar fixture.
N01/N04 are useful low-evidence controls.

No numeric cleanup gate threshold is frozen by this result.
