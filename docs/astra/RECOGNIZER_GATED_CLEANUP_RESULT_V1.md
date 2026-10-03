# Recognizer-Gated Cleanup Result V1

Date: 2026-10-02
Run ID: 37082340739
Status: **SUCCESSFUL CONSERVATIVE-GATE PASS**

Artifact:
- id: 11259456727
- digest: `sha256:90ac2d210d8df9a0ee1b9b9d6ae3e09041acedaf477aeaa564d07c2445627b5d`

## Summary

- mixtures: **12**
- cleanup applied: **0 stems**
- mean target SI-SDR change: **0.000 dB**
- worst target change: **0.000 dB**
- best target change: **0.000 dB**

The gate prevented every destructive cleanup action from the earlier blanket-cleanup experiment.

## Interpretation

This V1 gate is safe but too conservative.

It correctly refused to modify:
- near-silent absent-target stems;
- low-confidence true targets;
- ambiguous guitar-vs-bass cases;
- S0M10 false guitar, because YAMNet judged it bass-leaning but with only a small margin.

Key cases:
- S0M03 guitar: true target, separator nearly silent, YAMNet 0/0 -> preserve raw
- S0M11 bass: true target, separator nearly silent, YAMNet 0/0 -> preserve raw
- S0M10 guitar: false target, guitar 0.2053 vs bass 0.2171, small margin -> uncertain, preserve raw
- S0M12 bass: true bass, guitar 0.3390 vs bass 0.3313, small margin -> uncertain, preserve raw

## Decision

Keep the **preserve-by-default** principle.

Do not loosen the gate simply to force cleanup actions on the same 12 fixtures.

The next experiment should distinguish two different problems:

1. **Target-preserving bleed cleanup**
   - only useful when the target is actually present and contaminated.

2. **False-stem suppression / reassignment**
   - for cases where the separator emits a substantial stem for an instrument that is not present.
   - S0M10 guitar is the main development example.

For false-stem handling, the next evidence source should compare:
- claimed-stem YAMNet class evidence;
- strongest competing stem class evidence;
- energy/reconstruction consequences if the claimed stem is reassigned rather than spectrally attenuated;
- downstream note-transcription behavior.

A false stem should not be deleted merely because another class narrowly wins.

V1 recognizer-gated cleanup therefore passes the safety objective but does not yet improve separation quality.
