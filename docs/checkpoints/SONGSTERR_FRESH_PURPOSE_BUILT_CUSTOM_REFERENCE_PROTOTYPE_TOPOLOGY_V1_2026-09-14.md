# Songsterr Fresh — Purpose-Built Custom/Hybrid Reference Prototype Topology V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN PROSPECTIVE NON-HOLDOUT BENCH TOPOLOGY / NO HOLDOUT CAPTURE AUTHORITY**

Parent authority:
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_HARDWARE_BENCH_QUALIFICATION_PREREGISTRATION_V1_2026-09-14.md`
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_HARDWARE_DOCUMENT_SCREEN_V1_2026-09-14.md`

## 1. Decision

The initial document screen found no complete off-the-shelf authoritative-reference qualifier. The bench prototype will therefore use a **hybrid/custom architecture** with four deliberately separate evidence planes.

This topology freezes the information flow and bench questions. It does **not** freeze a final vendor/BOM, authorize a holdout population, or declare any candidate component qualified before bench evidence exists.

## 2. Four-plane prototype architecture

### Plane A — evaluated DI

- One conventional clean magnetic guitar DI channel.
- Captured as an ordinary raw audio channel.
- Never used to create, repair, align, threshold, or disambiguate reference truth.
- Basic Pitch/V6/correctness remain forbidden during bench calibration.

### Plane B — physical string/fret/contact state

Use a custom physical sensing plane whose raw observations establish string identity plus open/fretted/contact position without estimating pitch from evaluated audio or from per-string vibration frequency.

The first prototype may evaluate either or both of these physical approaches:

**B1 — multiplexed conductive string/fret scanning**
- electrically conductive steel strings are individually addressable;
- frets/contact network provide a physical code for contacted fret;
- one string is actively interrogated at a time while other string channels are placed in a non-driving/high-impedance state where practical;
- raw per-string samples/ticks are logged before any debouncing or semantic projection.

**B2 — electrically isolated per-string fret/contact sensing**
- segmented conductive/capacitive/contact regions provide per-string/per-fret sensing without relying on one continuous fret as a shared electrical node;
- raw per-region/string state and timestamps are logged.

B1 is cheaper/easier to prototype but is **not assumed valid**. A normal continuous metal fret can electrically couple multiple strings, especially when multiple strings contact the same fret. Cross-string/chord ambiguity is therefore a mandatory qualification test. If B1 cannot resolve chords and multi-contact states deterministically without evaluated-audio/model inference, it receives `BENCH_FAIL` for authoritative use and B2 or another electrically isolated topology becomes required.

Open string is represented as no qualifying fret contact under the frozen physical mapping. Unknown/conflicting states must remain explicit ambiguity; they may not be guessed from audio.

## 3. Plane C — independent event-birth / excitation evidence

Use six physically separate per-string vibration/excitation channels whose purpose is event-birth/rearticulation evidence, not pitch estimation.

Preferred prototype class:
- one piezo bridge/saddle signal per string, or another raw per-string physical vibration/force/acceleration sensor;
- preserve the six raw analog waveforms/status streams;
- derive only attack/birth evidence under NON_HOLDOUT calibrated rules;
- do **not** use signal frequency to derive string/fret/MIDI identity.

A Graph Tech Ghost-style six-saddle piezo/hexaphonic architecture is a plausible component class because its saddles produce six discrete electrical string signals. The external pitch-to-MIDI conversion path is not authoritative and is not needed for this prototype. Direct/raw six-channel access and conditioning remain bench/integration questions rather than assumptions.

## 4. Plane D — clock and hardware synchronization

Preferred prototype timing architecture:

1. Capture all analog channels used for evaluated DI and physical excitation on **one multichannel audio-interface sample clock**.
2. The physical fret/contact logger keeps its own monotonically increasing raw hardware ticks.
3. The fret/contact logger emits a deterministic hardware sync pulse/marker sequence.
4. A safely conditioned copy of that hardware marker is captured on one channel of the multichannel audio interface.
5. The only permitted digital-logger-to-audio clock transform is computed from those immutable hardware markers under a prospectively frozen algorithm.

Forbidden alignment remains:
- evaluated-DI waveform correlation;
- excitation-to-DI musical onset matching for clock recovery;
- spectral/DTW alignment;
- Basic Pitch/model alignment;
- manual waveform nudging.

The final hardware-only timing proof must be able to truthfully satisfy the already-frozen structural bound `<= 0.025 s`. The prototype should target materially better engineering performance, but this topology does not change or tighten the frozen admission threshold.

## 5. Eight-channel common-audio-clock budget

A practical first bench configuration can fit the core analog evidence into eight simultaneous analog inputs:

1. magnetic evaluated DI;
2. string 1 excitation/piezo;
3. string 2 excitation/piezo;
4. string 3 excitation/piezo;
5. string 4 excitation/piezo;
6. string 5 excitation/piezo;
7. string 6 excitation/piezo;
8. conditioned hardware sync marker from the physical-state logger.

An 8-input interface is therefore sufficient for the minimum bench topology if it can capture all eight inputs simultaneously on one hardware sample clock and preserve raw files without automatic content-dependent processing.

Current Focusrite Scarlett 18i20 4th Gen documentation confirms eight line inputs, two instrument inputs, 24-bit/192-kHz conversion and 26x26 simultaneous I/O. This makes it a **document-compatible interface-class example**, not a frozen purchase choice.

Source: https://focusrite.com/products/scarlett-18i20

## 6. Physical-state logger requirements

The prototype logger must have enough deterministic real-time I/O to:
- interrogate/receive all six string contact states;
- retain raw pre-debounce observations;
- timestamp observations with monotonic hardware ticks;
- emit sync markers;
- record immutable raw logs locally or losslessly to the host;
- expose firmware/configuration identity;
- support deterministic offline decoding.

PJRC Teensy 4.1 is a **document-compatible microcontroller-class example** because current official specifications list a 600-MHz Cortex-M7, 55 digital I/O pins, 18 analog inputs and onboard microSD/SDIO. These specs plausibly support six-string scanning, raw local logging and sync-marker generation. It is not qualified until bench evidence exists.

Source: https://www.pjrc.com/store/teensy41.html

## 7. Front-end/conditioning rules

No sensor or microcontroller output may be connected to a logger/interface in a way that exceeds input electrical limits or compromises player/instrument safety.

The bench implementation must document:
- input voltage/current limits;
- piezo buffering/impedance requirements;
- DC blocking where needed;
- sync-pulse attenuation/conditioning/isolation;
- common-ground/isolation topology;
- ESD/transient protection where relevant;
- whether the physical fret scan injects any signal that is measurable in the evaluated magnetic DI.

Any fret-scan interference into evaluated DI that cannot be eliminated prospectively is a bench failure for that topology; it may not be removed later using holdout-aware signal processing.

## 8. Minimum NON-HOLDOUT bench sequence

The first physical prototype must remain entirely NON_HOLDOUT and execute, in order:

1. **Electrical/safety sanity check** with no admitted performance.
2. **Raw logger determinism check** — identical stored raw bytes reproduce canonical decoded output.
3. **Open-string state check** on all six strings.
4. **Every planned fret/string identity matrix** using physical contacts only.
5. **Chord/multi-contact crosstalk matrix**, including same-fret and different-fret multi-string combinations.
6. **Repeated same-string/same-fret attacks** and repeated open-string attacks using the excitation plane.
7. **Near-simultaneous chord attacks**, retaining separate string births.
8. **Hardware-marker clock proof** and residual/error characterization.
9. **Dropout/saturation/stuck/missing-marker/malformed-stream/config-mismatch stress cases**.
10. **Technique capability matrix** for any technique proposed for later holdout scope.

At no step may evaluated DI content or a transcription model be used to resolve reference ambiguity.

## 9. Release/termination note

The frozen structural-audit birth stream includes `releaseSeconds`. The prototype must therefore establish a deterministic reference-only release/termination rule during NON_HOLDOUT calibration before any real holdout plan is locked.

Potential physical evidence can include the raw excitation/vibration decay state, subsequent independently established birth on the same string, or separately sensed mute/contact state, but the exact rule is **not yet frozen here**. It must never be chosen by comparing candidate releases to evaluated DI/model output. Duration correctness remains paused and this release field is structural state, not a new duration-scoring authority.

## 10. Technique scope rule

Baseline prototype qualification should first prove the simplest physical cases:
- picked fretted notes;
- picked open strings;
- repeated same-pitch attacks;
- multi-string chords/near-simultaneous births.

Hammer-on, pull-off, tapping, slide, bend and vibrato support remains conditional on an independently defensible physical rule. Each class must eventually be `SUPPORTED_BY_FROZEN_PHYSICAL_RULE`, prospectively excluded, or make the architecture unqualified for a proposed plan. No technique is rescued after holdout capture by listening to DI.

## 11. Procurement consequence

The topology now establishes that a real bench prototype cannot be completed by software alone. Procurement becomes justified only for the **minimum components needed to answer the frozen bench questions**, not for a speculative commercial MIDI-guitar ecosystem.

Before recommending a concrete purchase list, perform one more document-level BOM screen for:
- 8-channel simultaneous audio-interface options;
- six-channel raw piezo/bridge or equivalent excitation options;
- physical fret/contact prototype materials/topology;
- real-time microcontroller/logger;
- safe analog conditioning/sync-marker interface.

Prefer reusable, low-cost, openly documented components where they satisfy the same frozen evidence requirements. Do not infer that the example Scarlett/Teensy/Graph Tech components are mandatory simply because they are compatible on paper.

## 12. Authority boundary

This is a NON_HOLDOUT bench topology only.

It does not authorize:
- admitted holdout recording;
- Basic Pitch/V6/correctness;
- model-informed calibration;
- performer recruitment;
- protected-song material;
- Production/customer promotion.

Keep:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Archived V143/Gomyway remains untouched and closed.
