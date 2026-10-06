# Guitar-FL integration Stage B reference architecture V1

Date: 2026-10-06
Branch: `astra-work`
Status: **PRE-CAPTURE ARCHITECTURE FROZEN — NO PROCUREMENT / CONTACT / CAPTURE AUTHORIZED**

## Governance reuse

Stage B must reuse, not fork, the existing purpose-built governance stack:

- `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_3.py`
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`
- existing calibration-package binding and structural-audit input-binding semantics.

The Stage-B integration study adds only:
- frozen comparator/intervention identities;
- frozen lead/rhythm slot role;
- six-performer/five-category population floors;
- Stage-B numerical gate;
- intervention-specific Stage-A adapter identity;
- explicit disjointness from every consumed corpus.

No existing anti-cherry-picking or structural-fail behavior is weakened.

## Three-plane architecture

### Plane A — evaluated audio

Required:
- clean magnetic-guitar DI;
- no amp/cab/effect/denoise/source-separation processing in the authoritative evaluated path;
- immutable source bytes + SHA-256;
- recording format/configuration frozen before capture.

This is the only audio supplied to Basic Pitch and guitar-fl.

### Plane B — physical pitch/string-fret identity

Required properties:
- independent of Plane A audio;
- six-string identity;
- open/fretted state;
- fret identity or equivalent deterministic physical-position state;
- raw timestamps on the reference clock;
- configuration/firmware/calibration identities retained.

A pitch estimator operating on Plane A cannot substitute for Plane B.

### Plane C — independent event-birth evidence

Required properties:
- detects excitation/rearticulation independently of Plane A;
- can distinguish same-string/same-fret repicks;
- records raw event timestamps before any derived note-event projection;
- supports the frozen technique semantics for picked notes, hammer-ons, pull-offs, tapping, slides and chord births.

Plane C may be a physical trigger/dynamics sensor or another independently justified sensing path. Exact hardware is not selected by this document.

## Clock topology

Preferred:
- one hardware clock / one capture timeline for all three planes.

Permitted fallback:
- separate clocks with immutable hardware sync markers visible to both capture systems.

Forbidden:
- waveform cross-correlation to DI;
- spectrogram alignment;
- audio onset detection;
- DTW to DI;
- transcription-model activation alignment;
- manual waveform nudging.

Any clock transform must be frozen before capture and derived solely from hardware sync markers.

## Role declaration

Every frozen capture slot declares exactly one role:
- `lead`
- `rhythm`

Role is part of the capture plan and performer instruction.

Neither Basic Pitch nor guitar-fl may infer or alter the role.

The same role value is passed to both downstream paths.

## Reference decoder boundary

The decoder operates only on Planes B/C plus hardware clock/sync data.

It must not read:
- evaluated DI;
- Basic Pitch outputs;
- guitar-fl outputs;
- downstream fretboard output;
- correctness metrics.

It emits immutable reference note births with:
- event ID;
- timestamp;
- string;
- fret/open state;
- projected nominal MIDI;
- technique class where applicable;
- raw-source provenance.

## Existing manifest V2.3 mapping

Each admitted Stage-B performance must bind the existing V2.3 fields:

- `hardwareSourceSha256`
- `birthStreamSha256`
- `pitchLatchStreamSha256`
- `clockSyncSourceSha256`
- configuration identity;
- instrument setup identity;
- calibration identity;
- clock-sync identity;
- reference artifact identity;
- structural-audit input identity.

Stage B additionally requires:
- frozen role;
- category;
- performer ID;
- content/exercise ID;
- rights-manifest entry ID;
- comparator/intervention version identities;
- Stage-A adapter blob identity.

## Acquisition QA versus structural audit

### Acquisition QA may permit retake only for frozen objective infrastructure failures

Examples are transport/device/file-format/sync-channel failures whose thresholds were frozen before capture.

### First transport-valid take is irrevocably admitted

After admission, the take cannot be replaced for:
- playing mistakes;
- difficult technique;
- sparse/extra sensor events;
- model disagreement;
- reference/model mismatch;
- low scores;
- unattractive output.

### Structural failure never becomes a retake reason

If the later reference-blind structural audit fails, the preregistered population closes under its frozen rule. It is not repaired by dropping inconvenient takes or replacing performers.

## Rights boundary

No session may begin until its rights-manifest entries are complete and hash-bound.

Required:
- performer release;
- recording ownership/use grant;
- content/composition provenance;
- product-validation permission;
- protected-song exclusion;
- redistribution/storage restrictions;
- document SHA-256.

## Current blocker

Exact hardware/vendor selection is intentionally **not** frozen here because doing so would require a separate procurement/feasibility decision.

No vendor contact, performer contact, purchase, deposit, rental, recording, or calibration is authorized by this architecture.
