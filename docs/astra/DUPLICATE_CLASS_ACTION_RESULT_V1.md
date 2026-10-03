# Duplicate-Class Action Result V1

Date: 2026-10-02
Run ID: 37087791658
Status: **SUCCESSFUL CORRECTED ACTION PASS**

Artifact:
- id: 11260744333
- digest: `sha256:54c0717f54147c0473f5db2b1bace917aac61c9a0e157e901a6a202922ed02c5`

## Key result

Only one duplicate-class candidate was detected: **S0M10 duplicate_bass_candidate**.

Correct interpretation:
- false duplicate stem: guitar
- true companion stem: bass
- guitar target actually absent: true
- bass target actually present: true

### Raw

- bass SI-SDR: **0.0728 dB**
- false guitar energy: **0.0049346**
- reconstruction max absolute error: **0.008216**

### Mute false guitar

- bass SI-SDR: **0.0728 dB**
- false guitar energy: **0**
- reconstruction max absolute error: **0.329865**

Muting removes the false stem but does not recover its useful bass content and badly damages mixture reconstruction.

### Merge false guitar into bass

- bass SI-SDR: **30.5695 dB**
- false guitar energy: **0**
- reconstruction max absolute error: **0.008216**

This is a **+30.497 dB** improvement in the true bass stem relative to raw while preserving the original reconstruction error.

## Interpretation

For this frozen S0 case, BS-Roformer did not merely hallucinate an independent false guitar signal. It **split one bass source across two guitar/bass output stems**.

That explains why:
- YAMNet saw both stems as bass-like;
- the two stems had similar energy;
- they were mutual strongest overlap competitors;
- muting failed;
- merging succeeded dramatically.

## Decision

The most promising post-separator correction discovered so far is **duplicate-class consolidation**:

1. classify guitar+bass outputs as a pair;
2. if both substantial stems strongly support the same instrument class;
3. if they are mutually overlapping and energy-compatible;
4. consolidate the incorrectly labeled companion waveform into the correct-class stem;
5. zero the false-class stem;
6. otherwise preserve raw output.

Do **not** generalize this from one S0 duplicate case to production audio yet.

Next evidence needed:
- more duplicate-class synthetic cases in both directions (bass split into guitar and guitar split into bass);
- controlled split ratios and overlap conditions;
- verify pair detector precision before any automatic consolidation on real recordings.

This result does not support blanket cleanup, threshold suppression, or production deployment.
