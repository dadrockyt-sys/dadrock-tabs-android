# Songsterr Fresh V6 — Purpose-Built Untouched Holdout Expanded Design

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **DESIGN ONLY / NO CAPTURE AUTHORITY**
Canonical state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## 1. Scope and authority

This checkpoint expands the paper/protocol design for a future purpose-built untouched real-guitar V6 holdout. It does **not** authorize procurement, spending, performer/vendor contact, hiring, recording, data acquisition, candidate-media access, Basic Pitch, V6 correctness, Modal, Vercel heavy-GPU, L4 GPU, Production changes, customer promotion, or protected-song use.

Archived V143/Gomyway remains closed. Archived GOAT/reference scoring remains closed. The frozen V6 method and external-scoring framework are unchanged.

Existing purpose-built governance remains authoritative and is extended, not replaced:

- `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v1.py`
- `scripts/songsterr-fresh/purpose_built_capture_manifest_semantic_guard_v1.py`
- `scripts/songsterr-fresh/purpose_built_capture_preregistration_binding_v1.py`
- Git-history proof
- deliberate GitHub-hosted `workflow_dispatch` attestation
- GitHub server proof
- hardened workflow/generator blob integrity
- hosted attestation-artifact proof
- passed artifact-proof trust-boundary audit at `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_ARTIFACT_PROOF_TRUST_BOUNDARY_AUDIT_2026-09-13.md`

The passed artifact-proof boundary is not reopened here.

## 2. Objective

Design a future untouched validation population in which the evaluated signal is a normal real-guitar DI recording, while note identity and event timing are established through physical/reference channels that are independent of that evaluated DI and independent of the model being validated.

The design must make the following failure modes impossible or fail-closed:

- evaluated-audio-derived ground truth;
- model-derived or model-corrected ground truth;
- post-hoc waveform/spectrogram alignment;
- model-informed retakes or cherry-picking;
- manual deletion/repair of inconvenient events;
- duplicate/effect/view inflation of population evidence;
- rights ambiguity;
- changing reference semantics after holdout observation;
- changing V6/scoring settings after correctness exposure.

## 3. Three-plane capture architecture

The intended architecture has three logically separate evidence planes.

### Plane A — evaluated audio

- A conventional **clean magnetic guitar DI** is the only audio presented to the frozen external V6 validation path.
- The evaluated path must be captured directly from the real instrument performance, not synthesized from reference data.
- Any optional monitoring, room microphone, amplifier, effect, camera, or diagnostic channel is non-authoritative for V6 correctness unless separately preregistered for a non-correctness purpose.
- Multiple simultaneous views of one take remain one underlying performance and cannot multiply population evidence.

### Plane B — physical pitch identity

Preferred design: a physical string/fret-state reference that identifies which string is active and the fretting state without estimating pitch from the evaluated audio.

The pitch-reference plane should preserve raw state such as:

- string identity;
- open/fretted/muted state;
- fret/contact identity or continuous physical-position state when applicable;
- state-transition timestamp in the reference clock;
- sensor-health/status fields;
- calibration/configuration identity.

A deterministic, preregistered projection can map `(string, fret)` to nominal integer MIDI for the frozen V6 comparison. The richer physical state must remain preserved even when V6 consumes only the projected integer MIDI.

A pitch-to-MIDI product that infers pitch acoustically/electrically is weaker and must not be treated as infallible performed truth merely because it emits MIDI.

### Plane C — independent event-birth / excitation evidence

A separate physical trigger/dynamics path should establish excitation/rearticulation information independently from evaluated DI. Its role is especially important for repeated notes at the same string/fret state, where pitch-state transitions alone cannot establish a new onset.

Candidate physical mechanisms are design options only. No product selection or purchase is authorized. The authoritative property is independence from evaluated DI and from model inference, not a particular vendor.

## 4. Why pitch state and onset state must remain separate

A guitar onset is not always equivalent to a new fret state:

- repeated picking can rearticulate the same string/fret;
- an open string can be rearticulated without any fret transition;
- hammer-ons and pull-offs can create a new pitched event without a conventional pick attack;
- tapping can create fret-driven excitation;
- slides change physical pitch state continuously or stepwise without a new pick;
- bends/vibrato change sounding pitch after an onset;
- muting can terminate/suppress a sounding event without defining a new note birth.

Therefore a future reference decoder must use **predeclared technique semantics** rather than one generic “trigger equals onset” rule.

The future decoder must be deterministic and frozen on non-holdout calibration material before the first holdout take. It must not inspect evaluated DI or Basic Pitch/V6 outputs.

## 5. Reference-event semantics to freeze before capture

A future preregistration must define, at minimum, how raw physical states become immutable reference note events.

### 5.1 Picked/re-picked notes

A valid independent excitation event associated with a stable physical pitch state creates a new note birth. Same-pitch rearticulation remains a distinct event when independently triggered.

### 5.2 Hammer-ons / taps

A qualifying physical fret-state transition can create a note birth without a pick trigger when the preregistered technique/state machine says that transition is excitatory. The rule must be calibrated without holdout/model access.

### 5.3 Pull-offs

A qualifying transition from a higher stopped fret to a lower stopped/open state can create a new note birth under frozen physical-state rules. No audio-derived onset correction is permitted.

### 5.4 Slides

The preregistration must explicitly decide whether intermediate physical states are continuous pitch motion or new discrete reference births. The decision must be technique-driven and frozen before holdout capture; it cannot be changed because of model behavior.

### 5.5 Bends / vibrato

Raw physical reference should preserve bend/vibrato state if measurable. For frozen V6 correctness, the note's nominal integer-MIDI identity is projected under a rule fixed before capture. Pitch motion itself must not be retrospectively converted into convenient extra births.

### 5.6 Chords

Near-simultaneous independent per-string births remain distinct note events. A chord is not one event for note-level correctness. The reference must preserve each string/note identity and timestamp.

### 5.7 Muting and note termination

Termination/release state can be preserved in rich raw truth, but this purpose-built design does not alter the frozen V6 onset/pitch correctness framework. Duration authority remains unchanged/paused.

## 6. Timebase and synchronization

Reference timing must not be recovered by aligning to evaluated audio.

Preferred hierarchy:

1. **single shared hardware clock/timebase** for evaluated-audio timestamps and physical-reference timestamps; or
2. separate clocks tied by immutable hardware sync markers/pulses captured by both systems.

If separate clocks are unavoidable, any clock transform must be determined solely from preregistered hardware sync markers. A deterministic transform such as an affine clock map may be used only when its exact computation and QA limits were frozen before capture.

Forbidden synchronization methods include:

- waveform cross-correlation against evaluated DI;
- spectral alignment;
- onset-detector alignment from evaluated DI;
- DTW against evaluated audio;
- Basic Pitch/model activation alignment;
- manual waveform/spectrogram nudging.

Raw clock counters, raw sync-marker records, the derived clock map, configuration hashes, and QA results must all be preserved.

## 7. Calibration boundary

Calibration must be strictly separated from the untouched holdout.

A future calibration phase may establish:

- sensor thresholds and hysteresis;
- debounce/state-transition rules;
- per-string/fret mapping;
- physical excitation thresholding;
- sync-marker decoding;
- allowable clock drift/jitter;
- sensor dropout/saturation rules;
- deterministic reference-event state-machine semantics.

Calibration material must be explicitly marked **NON-HOLDOUT** and permanently excluded from later V6 correctness. Calibration cannot use Basic Pitch/V6 outcomes or any model-informed feedback. Once calibration is frozen, no threshold/state-machine change may be made from holdout observations.

The future capture plan must bind the calibration artifact IDs/hashes that are authoritative for every holdout take.

## 8. Acquisition QA versus structural audit

These are intentionally different gates.

### Acquisition QA — may permit a retake

Only objective, preregistered transport/hardware failures observable without model/correctness information may permit another attempt for the same frozen slot.

Existing v1 plan-binding code currently recognizes:

- `ABSENT_REFERENCE_CHANNEL`
- `CLIPPING_LIMIT_EXCEEDED`
- `DEVICE_DISCONNECT`
- `MALFORMED_MIDI_STREAM`
- `MISSING_OR_CORRUPT_FILE`
- `TRANSPORT_FAILURE`
- `WRONG_SAMPLE_RATE_OR_FORMAT`

For a future physical fret/trigger design, the vocabulary likely needs a **versioned pre-capture extension** for objective conditions such as:

- missing hardware sync marker;
- clock-drift/jitter limit exceeded;
- physical-reference sensor dropout;
- reference-sensor saturation/stuck state;
- configuration/firmware/calibration identity mismatch;
- missing required raw clock/reference stream.

These are design requirements, not newly authorized failure codes. If adopted, they must be implemented in a new versioned contract/plan layer with synthetic tests and frozen **before** any real holdout capture. They may never be invented post-capture to discard difficult takes.

### Reference-blind structural audit — cannot permit rescue

After capture is complete and the frozen population is bound, a separate reference-blind audit may inspect raw reference structure/alignment under its preregistered rules.

If that audit finds disqualifying anomalies, the outcome is dataset/corpus rejection. It may not:

- delete bad events;
- hand-fix events;
- substitute a later take;
- alter reference semantics;
- change thresholds;
- reopen the capture roster;
- use evaluated audio/model output to repair the reference.

This preserves the lesson from Guitar-TECHS: structural unsuitability must close the candidate before correctness, not trigger rescue.

## 9. Retake and anti-cherry-picking governance

Existing v1 governance already requires the first transport-valid attempt in a slot to be admitted and rejects later attempts after the first passing take. This remains binding.

Expanded policy:

- every attempt receives a stable attempt ID and timestamp;
- every failure retains its objective frozen reason code;
- failed/partial files are retained when technically possible and hashed;
- a pass cannot be voluntarily discarded for musical quality, cleanliness, difficulty, performer preference, “better feel,” or model performance;
- no one involved in capture may see model outputs for the holdout;
- no model output may influence whether a slot is repeated;
- capture roster and slot identity are frozen before capture;
- no replacement player/exercise/category can be inserted because a captured result looks hard or inconvenient.

## 10. Rights and content provenance

Before any real capture, every admitted performance must have an explicit product-validation rights chain.

Required future records include:

- performer release/license authorizing recording and product-validation use;
- content/composition provenance;
- confirmation that protected-song material is excluded;
- recording ownership/use grant;
- document ID and immutable SHA-256;
- effective date/version;
- session/player linkage.

Preferred performance material is original, commissioned with appropriate rights, public-domain where applicable, or otherwise explicitly rights-cleared. A vague “research use” or platform upload permission is insufficient for the frozen product-validation gate.

No performer/vendor contact or rights solicitation is authorized by this checkpoint.

## 11. Population and diversity design

The independence unit is the **underlying real performance/take**, not an effect render, reamp, microphone view, channel view, crop, augmentation, or file count.

The future population should deliberately vary real performance factors that could matter to transcription while keeping the evaluated path within the frozen isolated-guitar DI definition:

- multiple players;
- multiple instruments;
- different pickup/instrument setups compatible with clean DI;
- realistic playing dynamics;
- tempo/rhythm variety;
- fretboard/range coverage;
- polyphony density;
- repeated-note density;
- articulation/technique diversity;
- the frozen V6 categories: `chords`, `scales`, `singlenotes`, `techniques`, `music`.

No category/player allocation may be changed in response to model results.

The frozen external requirement remains **>=1,000 pooled V6-positive estimates**. Because V6-positive yield cannot be used to tune capture, the design should collect a much larger preregistered raw-reference population. The existing provisional planning scale of **>=20,000 raw reference notes across multiple players** remains a planning value, not a frozen validation rule.

A possible future planning matrix (not yet frozen) is to spread those raw events across every player/category cell rather than concentrate them in one easy style. Exact player count, slot count, and raw-event floors must be frozen before acquisition and must not be optimized from V6 outcomes.

## 12. Manifest/provenance expansion

A future real-capture manifest should bind, directly or through immutable referenced documents, at least:

### Corpus-level identity

- corpus name/version;
- capture-plan path/SHA;
- preregistration commit/proof;
- rights-document ID/SHA;
- hardware configuration SHA;
- firmware/software versions;
- calibration artifact IDs/SHAs;
- evaluated-audio path identity;
- pitch-reference path identity;
- excitation/reference path identity;
- clock/timebase configuration SHA;
- reference-decoder/state-machine version and SHA.

### Player/session identity

- pseudonymous stable player ID;
- session ID;
- instrument/setup ID;
- pickup/output configuration ID;
- tuning/capo configuration if allowed by plan;
- frozen category/exercise/slot identity;
- rights/release linkage.

### Attempt identity

- stable attempt ID;
- slot ID;
- attempt number;
- UTC capture time;
- acquisition-QA status/reason;
- evaluated-DI file path/SHA;
- raw pitch-reference file path/SHA;
- raw excitation/reference file path/SHA;
- raw clock/sync file path/SHA;
- configuration/calibration IDs;
- admitted boolean.

### Derived reference identity

Any deterministic derived reference must record:

- raw source hashes;
- decoder/state-machine blob SHA;
- decoder configuration SHA;
- calibration identity;
- deterministic output SHA;
- declaration that evaluated audio/model outputs were not inputs.

Raw reference data must never be discarded merely because a derived projection exists.

## 13. Reference-blind structural gates

Before any correctness/model execution, the future structural preregistration should fail closed on conditions including:

- missing expected raw/reference files;
- hash/schema/configuration mismatch;
- missing or invalid clock mapping;
- sync discontinuity outside frozen limits;
- unresolvable reference sensor states;
- unmatched note births/terminations under frozen semantics;
- impossible same-key overlaps when forbidden by the reference state machine;
- duplicate event IDs;
- duplicate population identities;
- admission of multiple views/renders as separate performances;
- reference decoder/configuration mismatch;
- unbound calibration identity;
- roster mismatch;
- rights/provenance mismatch.

Whether every anomaly above is a zero-tolerance corpus blocker or has an objective preregistered numeric tolerance must be decided **before** real capture. No threshold may be selected from holdout observations.

## 14. Blinding and role separation

A future real collection should use procedural separation even if the same organization owns all stages.

### Capture role

May see only what is needed to execute the frozen plan and objective acquisition QA. Must not see model outputs or correctness.

### Reference/governance role

May validate hashes, sensor/reference integrity, preregistration, and structural rules. Must not use evaluated-audio-derived timing or model outcomes to repair truth.

### Correctness role

Receives the immutable admitted population only after governance + structural pass. Runs the frozen ordinary-GitHub-CPU correctness workflow exactly once.

The strongest practical design is to make model/correctness artifacts unavailable to capture/reference operators until population binding is irreversible.

## 15. State machine

The future route should be treated as a one-way fail-closed state machine:

`DESIGN_ONLY`
→ `EXPLICIT_AUTHORIZATION_REQUIRED`
→ `CALIBRATION_ONLY`
→ `CAPTURE_PLAN_LOCKED`
→ `CAPTURE_AUTHORIZED`
→ `CAPTURED_UNSCORED`
→ `GOVERNANCE_VERIFIED`
→ `REFERENCE_BLIND_STRUCTURAL_AUDIT`
→ on pass only: `POPULATION_BOUND`
→ `NO_REAL_CORRECTNESS_SYNTHETIC_HARNESS`
→ `ONE_OFFICIAL_CORRECTNESS_RUN`
→ frozen decision

Failure at a non-rescuable gate closes that population. It does not silently loop back into tuning.

**Current state remains `DESIGN_ONLY`.** This checkpoint does not advance the state machine.

## 16. Threat model / mandatory defenses

| Threat | Defense |
|---|---|
| evaluated-audio-derived truth | physical reference planes; explicit `derivedFromEvaluatedAudio:false`; no audio alignment |
| vendor pitch detector treated as truth | require physical provenance/semantics; vendor MIDI never automatically authoritative |
| post-hoc timing repair | hardware timebase/sync-only mapping frozen pre-capture |
| model-informed retakes | capture operators blinded; first objective QA pass admitted |
| cherry-picking easy takes | exact frozen slot roster; no pass discard |
| per-event manual cleanup | immutable raw reference; structural failure rejects rather than repairs |
| effects/reamp/channel inflation | independence unit = underlying performance/take |
| calibration leakage | dedicated non-holdout calibration set; permanent exclusion |
| threshold tuning after capture | config/calibration hashes frozen in preregistration |
| rights ambiguity | explicit product-validation release/license hash per session/corpus |
| clock drift hidden by audio alignment | raw clocks + hardware sync + frozen drift QA |
| richer truth overwritten by V6 projection | retain raw reference; deterministic projection is separately hashed |
| protected-song contamination | content provenance + explicit exclusion in plan/rights record |

## 17. What must be frozen before asking for real capture authorization

Before any future request to spend/contact/record, prepare a complete paper package containing:

1. exact hardware architecture classes and independence argument;
2. evaluated-DI signal path;
3. physical pitch-reference specification;
4. independent excitation/event-birth reference specification;
5. common-clock/sync architecture;
6. calibration protocol and permanent calibration/holdout separation;
7. deterministic reference-event semantics for all allowed techniques;
8. exact acquisition-QA failure vocabulary and numeric criteria;
9. exact structural-audit gates/tolerances;
10. player/session/instrument/category/slot population plan;
11. rights/release requirements and content provenance rules;
12. manifest schema additions and immutable hashing rules;
13. operator blinding/role-access rules;
14. storage/retention rules for failed and admitted attempts;
15. versioned synthetic tests for every new governance rule;
16. a cost/BOM estimate **for approval only**, without purchase/contact;
17. an explicit authorization checkpoint where no action occurs until the user approves.

## 18. Immediate design-only next work

The highest-value next paper-only expansion is to formalize two specifications without selecting/purchasing hardware:

1. **Physical Reference Semantics v1** — exact raw states, event-state machine, technique handling, V6 projection, and forbidden data dependencies.
2. **Capture QA + Structural Gate Matrix v1** — every failure condition assigned to either retake-permitted acquisition QA or non-rescuable structural rejection, with the point in the pipeline at which it is observable.

A later code change may be justified to version the current acquisition-failure vocabulary for clock/sensor-specific failures, but only after those semantics are documented and covered by synthetic tests. The existing v1 trust-boundary chain should not be rewritten merely to add duplication.

## 19. Standing fail-closed policy

This expanded design leaves all authority unchanged:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song embargoed
- Basic Pitch/V6 correctness unauthorized
- real capture unauthorized
- spending/procurement unauthorized
- performer/vendor contact/hiring unauthorized
- Modal/Vercel heavy-GPU/L4 unauthorized

The design is intentionally stronger than “audio + MIDI”: the target is **real evaluated DI + independently measured physical note identity + independently measured event-birth evidence + preregistered hardware timebase + irreversible blinded governance**.
