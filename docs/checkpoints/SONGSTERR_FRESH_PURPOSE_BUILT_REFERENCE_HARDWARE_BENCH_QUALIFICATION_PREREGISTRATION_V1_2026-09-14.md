# Songsterr Fresh — Purpose-Built Reference Hardware Bench Qualification Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN PROSPECTIVE BENCH/DOCUMENT SCREEN / NO HOLDOUT CAPTURE AUTHORITY**

## 1. Purpose

Freeze the hardware-neutral evidence requirements used to screen, purchase/build, and calibrate a future physical reference apparatus. This gate exists so a later device cannot redefine performed truth merely because of what its vendor API happens to expose.

This document is prospective and reference-only. It does not authorize real holdout capture, Basic Pitch, V6, correctness, customer use, Production use, or protected-song material.

## 2. Non-negotiable semantic architecture

A qualifying architecture must provide all four frozen domains without using evaluated-DI/model inference to create reference truth:

1. evaluated clean magnetic guitar DI for the eventual frozen V6 path;
2. physical string + nominal fret/contact state;
3. independent event-birth/excitation evidence able to distinguish same-pitch rearticulation;
4. common-clock evidence or immutable hardware synchronization evidence sufficient to establish reference time without audio-content alignment.

A candidate that provides only acoustically/electrically inferred MIDI is not authoritative pitch truth unless a separate qualifying physical string/fret reference exists.

## 3. Phase A — document/API pre-screen before purchase

Reject a candidate architecture from authoritative-reference use if public/obtained documentation cannot plausibly establish each applicable item below.

### A1. Physical pitch-state provenance

The candidate must expose physical evidence sufficient to identify:
- string identity;
- open/fretted state;
- nominal fret/contact identity or a raw physical-position/contact signal from which a frozen deterministic mapping can derive it;
- timestamp/tick;
- sensor status;
- configuration/calibration identity.

Opaque note/MIDI output produced by pitch detection is insufficient by itself.

### A2. Independent event-birth evidence

The architecture must expose raw or minimally processed physical excitation/rearticulation evidence independent of evaluated DI and model output. It must be plausible to distinguish repeated attacks while string/fret state remains unchanged.

### A3. Raw-data availability

Raw physical/reference observations must be exportable and retainable. A cloud-only or opaque corrected-event interface that does not expose sufficient raw provenance fails.

### A4. Clock/sync capability

The architecture must provide either:
- a common hardware clock/timebase for relevant reference/evaluated channels; or
- timestamped clocks plus a hardware marker/pulse path from which a deterministic preregistered transform can be computed.

No candidate may rely on waveform correlation, spectrogram alignment, evaluated-audio onset detection, DTW, Basic Pitch/model activation alignment, or manual waveform nudging.

### A5. Configuration identity

Hardware, firmware, software and calibration configuration must be bindable to immutable identities/hashes or equivalently specific version/configuration records sufficient to detect change.

### A6. Offline determinism

The architecture must permit deterministic offline regeneration of the canonical reference projection from preserved raw inputs plus a frozen decoder/configuration.

### A7. Health/status visibility

The architecture must expose enough raw/status information to identify, prospectively and without musical/model judgement, missing streams, disconnects, dropout, saturation/stuck-state conditions and sync failure.

A candidate that definitively fails any mandatory document-level criterion must not be purchased merely to reconfirm that failure.

## 4. Phase B — NON-HOLDOUT bench qualification after a candidate is acquired/built

All bench/calibration material is permanently `NON_HOLDOUT`. It may never enter the later correctness population.

### B1. Identity and reproducibility

Record and hash:
- hardware identities;
- firmware/software versions;
- wiring/topology/configuration;
- calibration fixture identity;
- raw logger/decoder code blob and configuration;
- all raw bench streams;
- derived bench outputs.

Re-running the frozen decoder on identical raw bytes must reproduce the canonical derived output deterministically.

### B2. Six-string physical identity matrix

Exercise every string and every fret/range intended for the later capture plan, including open strings. Establish whether the raw pitch-state plane can resolve physical string + nominal fret/contact without evaluated-DI/model inference.

Any unsupported string/fret range must be prospectively excluded from the later plan or the architecture fails qualification for that plan.

### B3. Same-pitch rearticulation

On each planned string/range, perform repeated same-string/same-fret and repeated open-string attacks in NON_HOLDOUT calibration. The excitation plane must provide independently distinguishable births while pitch state remains unchanged.

The decoder must never require evaluated audio or model output to decide whether the reattack occurred.

### B4. Chord/polyphony separability

Exercise near-simultaneous multi-string births. Preserve separate per-string physical births/timestamps; do not quantize them to one convenient chord time.

### B5. Technique capability matrix

For every technique class proposed for the future holdout, bench calibration must declare one of:
- `SUPPORTED_BY_FROZEN_PHYSICAL_RULE`;
- `PROSPECTIVELY_EXCLUDED_FROM_HOLDOUT_PLAN`;
- `ARCHITECTURE_NOT_QUALIFIED`.

No unsupported technique may be captured first and classified later from evaluated audio/model behavior.

### B6. Hardware-only timing proof

Use a hardware event/marker observable by the relevant clock domains to measure the complete reference timing path without audio-content alignment.

The resulting hardware/reference declaration and sync proof must be capable of truthfully satisfying the already-frozen structural-audit requirement:
- `maxAbsoluteReferenceTimingErrorSeconds <= 0.025`;
- `maxAbsoluteErrorSeconds <= 0.025`;
- no sync loss.

The `0.025 s` bound is inherited unchanged; this document does not tune it. Empirical drift/jitter/dropout acquisition-QA thresholds remain to be derived only from NON_HOLDOUT engineering calibration and frozen before any holdout attempt.

### B7. Failure-mode stress tests

Prospectively induce/observe bench-only failures sufficient to characterize objective machine-observable conditions such as:
- disconnected/missing reference channel;
- missing sync evidence;
- clock drift/jitter excursions where the setup permits controlled induction;
- sensor dropout;
- sensor saturation;
- sensor stuck state;
- malformed/truncated reference stream;
- configuration mismatch;
- calibration mismatch;
- missing/corrupt raw output.

The purpose is to define objective acquisition-QA detection, not to learn which holdout takes are inconvenient.

### B8. Ambiguity must fail closed

Conflicting/unknown physical states must emit an explicit ambiguous/unknown state in calibration rather than being guessed from evaluated DI. The eventual holdout structural policy remains zero-anomaly where already frozen by structural-audit V1.

## 5. Calibration information firewall

During reference calibration:
- no future admitted holdout exists;
- Basic Pitch/V6/correctness feedback may not set or revise reference thresholds;
- no model output may decide whether a physical event is valid;
- evaluated future-holdout DI is unavailable;
- any optional engineering instrumentation used for calibration must be explicitly NON_HOLDOUT and cannot become an alternate post-hoc truth source for the later holdout.

Thresholds/hysteresis/debounce/technique rules may change only during this NON_HOLDOUT calibration phase. Once calibration is frozen and the first holdout take begins, those values are immutable for that population.

## 6. Qualification result

A candidate architecture receives one of:

- `DOCUMENT_REJECTED` — public/obtained documentation proves a mandatory semantic requirement cannot be met;
- `BENCH_REQUIRED` — documentation is plausibly compatible but empirical proof is required;
- `BENCH_FAIL` — acquired/built apparatus fails one or more mandatory bench requirements;
- `BENCH_PASS_LIMITED_SCOPE` — apparatus qualifies only for a prospectively declared restricted range/technique scope;
- `BENCH_PASS` — apparatus supports all frozen planned scope and can produce a calibration package suitable for later binding.

No result above establishes structural suitability of a future holdout population or authorizes correctness.

## 7. Evidence package required before holdout-plan lock

A later bench PASS must freeze at least:
- architecture/topology description + immutable identity;
- hardware/firmware/software configuration identities;
- raw reference schema/version;
- physical string/fret mapping calibration;
- excitation/birth calibration;
- technique capability matrix;
- common-clock/sync configuration and hardware-only timing proof;
- empirically justified objective acquisition-QA thresholds and code version;
- calibration raw-source hashes;
- deterministic decoder/configuration blob hashes;
- deterministic derived calibration output hashes;
- declaration `calibrationUsedHoldoutData:false`;
- declaration `calibrationUsedModelOutputs:false`;
- declaration `calibrationDerivedFromEvaluatedAudio:false` for the authoritative reference calibration path.

Only after this package is frozen may the project lock a real capture roster/population and consider holdout capture authorization.

## 8. Procurement/contact rule

Procurement or vendor contact becomes objectively necessary only when a candidate survives the document/API pre-screen but a mandatory criterion cannot be established without a physical bench sample or non-public technical information.

Any purchase/contact must be traceable to the exact unresolved criterion. Do not buy multiple speculative devices merely because the route is authorized.

## 9. Authority boundary

This preregistration authorizes only current documentation screening and, once objectively required, non-holdout bench qualification under the user's existing purpose-built authorization. It does not authorize real holdout recording.

Downstream authorization remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
