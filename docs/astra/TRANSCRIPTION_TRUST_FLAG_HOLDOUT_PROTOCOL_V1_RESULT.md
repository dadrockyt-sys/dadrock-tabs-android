# Transcription Trust / Flag Holdout Protocol V1 — Admission Result

Date: 2026-10-02  
Branch: `astra-work`

## Status

The model-free holdout-study admission protocol is implemented and tested.

GitHub Actions run: `37093326513` — **success**  
Head commit: `91f9fdabb10a815f98039523b37d229843fe3f20`

Implementation:
- `astra_backend/trustFlagHoldoutProtocol.mjs`
- `astra_backend/tests/trustFlagHoldoutProtocol.test.mjs`
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1.md`
- `docs/astra/TRANSCRIPTION_TRUST_FLAG_HOLDOUT_PROTOCOL_V1.json`
- `.github/workflows/astra-trust-flag-holdout-protocol-v1.yml`

## Tested admission properties

The validator successfully proves that a future study manifest must:

- keep the trust/flag threshold undefined during admission;
- keep automatic correction unauthorized;
- keep production delivery unauthorized;
- contain at least 48 new calibration cases;
- contain at least 48 new sealed holdout cases;
- satisfy the required condition strata in both phases;
- use valid SHA-256 source identities;
- reject duplicate case IDs;
- reject source reuse between calibration and holdout;
- reject any source already used in prior development/S0 when those hashes are supplied.

Negative tests for threshold leakage, source leakage, underrepresented hard strata, duplicate IDs, and malformed hashes all passed.

## Current scientific boundary

No actual calibration or holdout cohort has been admitted yet.

No threshold exists.

No audio/model execution is authorized by this protocol.

The next required evidence is therefore not another tuning experiment. It is **new source-disjoint study material** sufficient to populate the 96-case minimum design.

Until that material exists and passes manifest admission:
- uncertainty presentation remains diagnostic/fail-closed;
- S0 remains development evidence only;
- no automatic trust/flagging decision may be introduced.
