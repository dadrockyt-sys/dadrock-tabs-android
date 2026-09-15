# Songsterr Fresh — Purpose-Built Reference-Blind Structural Audit V1 — Synthetic CI PASS

Date: 2026-09-14 America/Toronto (GitHub run completed 2026-09-15 UTC)
Branch: `songsterr-fresh-pipeline-v1`

## Frozen authority

Structural-audit preregistration: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_BLIND_STRUCTURAL_AUDIT_PREREGISTRATION_V1_2026-09-14.md`
Frozen preregistration commit: `067875e3aa1538ff5483b74cc9071b00e9e82b07`

The implementation below preserves the preregistered reference-blind boundary. It accepts exactly four independent JSON byte streams — hardware/reference configuration, birth/dynamics, pitch-latch, and clock/sync — plus expected SHA-256 identities. Exact raw bytes are SHA-256 checked before JSON parsing or semantic audit. There is no evaluated-DI/audio, Basic Pitch, V6, correctness, score, or model-output input path.

Frozen independent-reference timing bound remains exactly `0.025 s`.

## Implementation frozen by successful CI head

Integration commit / workflow head: `8f4b41ce2cff075a6e7be25032142a0e8288b7be`
Integration tree: `6dfce1a944332f3339bfbc1ae347c8418cad1e7c`

Implementation:
- path: `scripts/songsterr-fresh/purpose_built_reference_blind_structural_audit_v1.py`
- Git blob SHA: `18e1344b7feb3977208b97146c9882c0d0299ea9`
- exact local/repository byte identity was independently checked before recording this checkpoint

Synthetic tests:
- path: `scripts/songsterr-fresh/test_purpose_built_reference_blind_structural_audit_v1.py`
- Git blob SHA: `eed135e275da2257797c62e5d99a4158afb02eaf`
- local pre-commit result: `24/24 PASS`

Workflow:
- path: `.github/workflows/songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.yml`
- Git blob SHA: `35fbbcda5c40bfd107d5c4136c6a68afa4d396f4`
- runner: `ubuntu-latest`
- Python: `3.12`
- external holdout data: none
- GPU: none

## GitHub-hosted CPU result

Workflow name: `Songsterr Fresh Purpose-Built Reference-Blind Structural Audit V1`
Run: `34912172056`
Job: `104201857367`
Head: `8f4b41ce2cff075a6e7be25032142a0e8288b7be`
Run attempt: `1`
Status: `completed`
Conclusion: `success`

The successful job completed both frozen-source compilation and the synthetic structural-audit contract test suite.

## Synthetic coverage frozen at PASS

The 24-test suite covers at least:
- nominal structural PASS;
- exact SHA-256-before-JSON short-circuit;
- exactly four source streams and expected hashes;
- malformed JSON fail-closed after matching raw-byte identity;
- hardware/configuration/calibration declaration failures;
- forbidden holdout/model/evaluated-audio calibration provenance;
- clock-sync loss and timing-bound violation;
- inclusive `0.025 s` timing boundary;
- ambiguous pitch state;
- unmatched birth and unmatched latch;
- multiple latches for one birth;
- birth/latch physical-string mismatch;
- birth/latch timing-delta violation;
- nonmonotonic and equal birth timestamps;
- nonmonotonic and equal pitch-latch timestamps;
- duplicate birth IDs and duplicate latch IDs;
- invalid fret/string/derived MIDI;
- same-string overlap, including proof that a separate latch anomaly cannot hide birth-side same-string overlap;
- same-key overlap across physical strings;
- forbidden model/evaluated-audio provenance in reference streams;
- ambiguous latch remains linked for anomaly accounting but cannot produce derived pitch truth;
- deterministic canonical result bytes for identical inputs;
- PASS still preserves every downstream authorization boundary.

## Authorization boundary remains closed

A synthetic structural-audit PASS establishes only that the implementation can enforce the frozen reference-side contract on synthetic inputs. It does **not** establish structural suitability of any real holdout population and it does not authorize model/correctness execution.

Even when the structural auditor returns PASS, it must leave:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

No real purpose-built calibration or holdout media was accessed for this implementation/CI milestone. No evaluated audio, model output, correctness matches, or correctness scores were exposed.

## Scope integrity

The archived V143/Gomyway pipeline was not resumed or modified. Guitar-TECHS rescue, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, and protected-song execution remain closed.

## Next allowed decision

With reference-blind structural-audit tooling and synthetic GitHub CPU CI now passing, the next step is **not** correctness. First decide whether real purpose-built hardware/procurement/contact/calibration is objectively necessary to instantiate the already-frozen validation plan. Before any real holdout recording, freeze any remaining candidate-specific capture/calibration/population-binding details required by the existing design authority. Calibration must remain non-holdout, reference-only, model-blind, and preserve immutable raw reference logs/hashes. Any real admitted population must pass this reference-blind structural audit before Basic Pitch/V6/correctness can even be considered under the later separate governance gates.
