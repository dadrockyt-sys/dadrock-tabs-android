# Songsterr Fresh — Reference-Blind Structural Audit V1.1 Preregistration Correction 1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE IMPLEMENTATION / CORRECTS ONE CONTRACT LITERAL ONLY

## Authority corrected

Original V1.1 preregistration:
`docs/checkpoints/SONGSTERR_FRESH_REFERENCE_BLIND_STRUCTURAL_AUDIT_V1_1_PROVENANCE_RESULT_BRIDGE_PREREGISTRATION_2026-09-14.md`
commit `d69defc153d06afe69ad6d1a9eb681f2ba1ff24a`.

No V1.1 implementation or V1.1 official result was executed before this correction.

## Correction

The original preregistration incorrectly named the accepted Provenance V1 validation-result `contract` literal as:

`songsterr-fresh-purpose-built-reference-calibration-package-provenance-v1`

The actual already-frozen Provenance V1 validator/result contract, as implemented at commit `3dd1140650070342ab9fc4e177870fd39940a4e0` and used by the completed result checkpoint `c57156fec7c5000563552c8cb128366956b8c95b`, is:

`songsterr-fresh-purpose-built-reference-calibration-package-v1`

Therefore every occurrence in the V1.1 preregistration that requires the exact accepted provenance-result contract must be interpreted as:

`songsterr-fresh-purpose-built-reference-calibration-package-v1`

## Everything else remains frozen

No other V1.1 preregistration rule changes. In particular:

- the original four-source V1 boundary remains unchanged;
- the fifth provenance-result byte stream must still be hash-verified before parse;
- V2.2 provenance-result SHA and package-binding SHA declarations remain required;
- parsed result must still have `contractValid:true`, `errors:[]`, a canonical package binding, false firewall flags, inherited timing <= `0.025 s`, and valid decoder identities;
- V1 note events, timing, MIDI, overlap, provenance and zero-anomaly rules remain unchanged;
- V1.1 population identity still binds V1 population SHA + verified provenance result SHA + verified package binding SHA;
- all authorization remains false/zero.

This correction is frozen before V1.1 implementation and synthetic CI.
