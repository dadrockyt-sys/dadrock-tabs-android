# Songsterr Fresh V6 — Purpose-Built Capture QA + Structural Gate Matrix V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **DESIGN ONLY / NO CAPTURE AUTHORITY**
Parent design: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`
Physical semantics: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`
Canonical state: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## 1. Purpose

Assign every known failure class in a future purpose-built untouched holdout to a single prospective authority boundary so that a defect cannot be relabeled after capture to obtain a convenient retake, repair, or exclusion.

The four mutually exclusive decision stages are:

1. **PRE-CAPTURE BLOCKER** — capture must not begin for the affected slot/session/population.
2. **ACQUISITION QA FAIL / RETAKE PERMITTED** — an objective transport/hardware failure occurred during the attempt; the failed attempt remains in chronology and the frozen slot may be retried.
3. **REFERENCE-BLIND STRUCTURAL FAIL / NO RETAKE RESCUE** — a transport-valid admitted take/population later proves structurally unsuitable under frozen reference-only rules; the affected population closes rather than being repaired or substituted.
4. **CORRECTNESS-STAGE OUTCOME** — reached only after governance + structural pass; scored once under frozen V6 and never converted into a retake/tuning reason.

This document does not activate new failure codes, set numeric hardware thresholds, authorize capture, or modify the existing v1 governance code.

## 2. Core anti-relabeling rule

The stage at which a condition is observable and the consequence attached to it must be frozen before real holdout capture.

A condition cannot be moved from structural failure to acquisition-QA failure merely because the admitted take later becomes inconvenient. Conversely, an objective acquisition failure cannot be promoted to an admitted take in order to increase sample size.

The existing v1 first-valid-take rule remains binding:

- failed attempts remain in chronology;
- only frozen objective acquisition failures permit another attempt;
- the first attempt that passes acquisition QA must be admitted;
- no later attempt may exist after that first pass for the same slot;
- musical quality, model behavior, correctness, ease/difficulty, or performer preference are never retake reasons.

## 3. Decision hierarchy

For each planned slot/session:

1. Verify pre-capture authorization and immutable configuration identities.
2. Begin the attempt only if no pre-capture blocker exists.
3. During/at the immediate end of capture, evaluate only frozen acquisition-QA observables that do not require model/correctness or semantic repair.
4. If acquisition QA FAILS, retain provenance and retry the same frozen slot only under the frozen failure code.
5. If acquisition QA PASSES, admit that first passing attempt irrevocably.
6. After the complete preregistered population is captured/bound, perform the reference-blind structural audit.
7. If structural audit FAILS under the preregistered population-level rule, close the affected candidate population; do not retake/repair/substitute.
8. If structural audit PASSES, run the no-real-correctness synthetic harness and then exactly one official correctness run under the already-frozen V6/scoring framework.
9. Correctness outcome is final evidence under the frozen decision rule; it never loops back into capture/reference tuning.

## 4. Pre-capture blockers

These prevent real holdout capture from starting for the affected scope.

| Condition | Scope | Decision | Retake? | Model/audio-content needed? | Required evidence |
|---|---|---|---|---|---|
| User authorization for spending/contact/recording absent | whole program | PRE-CAPTURE BLOCKER | No capture may start | No | explicit authorization boundary |
| Performer/product-validation rights not executed/bound | player/session | PRE-CAPTURE BLOCKER | N/A | No | rights document ID + SHA |
| Protected-song or otherwise disallowed content in planned material | slot/population | PRE-CAPTURE BLOCKER | N/A | No | frozen provenance/rights plan |
| Capture plan/slot roster not preregistered and Git-bound | population | PRE-CAPTURE BLOCKER | N/A | No | exact plan hash + Git proof |
| Hardware configuration not frozen | session/population | PRE-CAPTURE BLOCKER | N/A | No | configuration SHA |
| Calibration artifact not frozen or is derived from holdout/model outcomes | population | PRE-CAPTURE BLOCKER | N/A | No | calibration IDs/SHAs + provenance |
| Reference decoder/state machine not frozen | population | PRE-CAPTURE BLOCKER | N/A | No | decoder/config SHA |
| Clock/sync architecture not frozen | population/session | PRE-CAPTURE BLOCKER | N/A | No | clock configuration SHA |
| Objective acquisition-QA criteria/thresholds not frozen | population | PRE-CAPTURE BLOCKER | N/A | No | versioned plan/criteria |
| Structural-audit criteria/tolerances not frozen | population | PRE-CAPTURE BLOCKER | N/A | No | structural preregistration |
| Required reference plane cannot independently support a planned technique | affected slot class | PRE-CAPTURE BLOCKER unless prospectively excluded in plan | N/A | No | technique-capability declaration |
| Operator/model blinding boundary not in place | population | PRE-CAPTURE BLOCKER | N/A | No | role/access attestation/proof where feasible |
| Storage/hashing/retention path for raw truth not ready | population/session | PRE-CAPTURE BLOCKER | N/A | No | frozen storage/provenance configuration |

A blocker discovered before capture may be corrected prospectively before any holdout take under a newly frozen preregistration. It is not a “retake” because no admitted holdout attempt has yet occurred.

## 5. Existing v1 acquisition-QA failure codes

The current `purpose_built_capture_preregistration_binding_v1.py` permits only this frozen objective vocabulary:

- `ABSENT_REFERENCE_CHANNEL`
- `CLIPPING_LIMIT_EXCEEDED`
- `DEVICE_DISCONNECT`
- `MALFORMED_MIDI_STREAM`
- `MISSING_OR_CORRUPT_FILE`
- `TRANSPORT_FAILURE`
- `WRONG_SAMPLE_RATE_OR_FORMAT`

Their exact criteria must be present in the frozen capture plan. This document does not change those codes.

For a future physical-sensor design, `MALFORMED_MIDI_STREAM` may no longer describe the authoritative physical reference representation. The solution is a prospectively versioned contract/plan, not reinterpretation of the existing v1 string after capture.

## 6. Proposed V2 acquisition-QA classes — DESIGN ONLY

The following are **proposed future classes**, not active failure codes. Each requires an exact machine-observable criterion, numeric limit where applicable, versioned implementation, and synthetic tests before real capture.

| Proposed class | Intended objective condition | Stage | Retake permitted? | Hard restriction |
|---|---|---|---|---|
| `MISSING_HARDWARE_SYNC_EVIDENCE` | required sync marker/clock stream absent for attempt | acquisition QA | Yes | cannot be inferred from evaluated audio |
| `CLOCK_DRIFT_LIMIT_EXCEEDED` | hardware-only measured clock drift exceeds prospectively frozen limit | acquisition QA | Yes | limit frozen on non-holdout calibration |
| `CLOCK_JITTER_LIMIT_EXCEEDED` | hardware-only sync residual/jitter exceeds frozen limit | acquisition QA | Yes | no waveform alignment |
| `REFERENCE_SENSOR_DROPOUT_LIMIT_EXCEEDED` | raw physical reference dropout exceeds frozen capture-QA limit | acquisition QA | Yes | objective sensor-health metric only |
| `REFERENCE_SENSOR_SATURATION_LIMIT_EXCEEDED` | reference sensor saturation exceeds frozen limit | acquisition QA | Yes | objective raw sensor status only |
| `REFERENCE_SENSOR_STUCK_STATE` | device health indicates frozen/stuck channel under frozen rule | acquisition QA | Yes | cannot be inferred from musical plausibility |
| `REFERENCE_STREAM_MALFORMED` | raw physical reference stream fails frozen schema/transport validation | acquisition QA | Yes | schema/transport only, not event semantics |
| `CONFIGURATION_IDENTITY_MISMATCH` | actual hardware/firmware/config hash differs from preregistered value at capture boundary | acquisition QA or pre-capture blocker depending when detected | Yes only if attempt actually began and code was prospectively classified that way | classification frozen before capture |
| `CALIBRATION_IDENTITY_MISMATCH` | attempt bound to wrong calibration artifact | acquisition QA or pre-capture blocker depending when detected | same rule as above | never repaired by rebinding after viewing data |
| `REQUIRED_RAW_REFERENCE_STREAM_MISSING` | required pitch/excitation/clock raw file absent/corrupt immediately at capture finalization | acquisition QA | Yes | file presence/integrity only |

### 6.1 Numeric thresholds remain deliberately TBD

This document does **not** choose values for:

- clipping limit;
- clock drift;
- clock jitter/sync residual;
- allowed sensor dropout duration/fraction;
- sensor saturation duration/fraction;
- stuck-state duration;
- debounce/hysteresis;
- excitation threshold.

Those values must come from prospective non-holdout calibration/engineering requirements and be frozen before real holdout capture. They must never be chosen by examining holdout data or V6 outcomes.

## 7. Acquisition-QA exclusions — explicitly NOT retake eligible

These conditions may **not** be used to fail acquisition QA or obtain another take:

| Condition | Why not |
|---|---|
| performer played a wrong note relative to an intended exercise | the holdout measures real performance; musical correctness is not transport QA unless the prospective design defines a non-holdout instruction-compliance boundary before capture, and such a boundary must not depend on audio/model interpretation |
| performance was messy, slow, fast, weak, noisy, difficult, or stylistically undesirable | subjective/cherry-picking risk |
| same-pitch repetitions look difficult for model | model-informed selection forbidden |
| DI sounds musically poor but is within frozen technical QA | subjective retake forbidden |
| reference contains unusual but structurally valid technique | hard examples cannot be discarded |
| Basic Pitch/V6 disagrees with reference | correctness is never acquisition QA |
| expected score/tab does not match performed event | score-following is not authoritative performed truth |
| operator prefers another take | first objective QA pass must be admitted |
| after-the-fact concern that a technique may hurt precision | model-informed selection forbidden |
| a valid take yields fewer/more events than expected | event count is not a transport failure unless a prospectively frozen hardware-health rule independently fails |

If instruction compliance is ever needed for content coverage, it must be designed prospectively using a method that does not allow evaluated-audio/model-informed cherry-picking. The safest current direction is to define slots by requested material/category while treating the independently measured actual performance as truth.

## 8. Reference-blind structural failures — non-rescuable

These are evaluated only after a take has already passed acquisition QA and been irreversibly admitted. They do **not** permit a new take for the same slot.

| Structural condition | Decision | Retake? | Manual repair? | Evaluated audio/model allowed? |
|---|---|---|---|---|
| admitted roster differs from preregistered slot roster | STRUCTURAL FAIL | No | No | No |
| multiple admitted passes for one slot | STRUCTURAL FAIL | No | No | No |
| take after first acquisition-QA PASS exists | STRUCTURAL FAIL | No | No | No |
| duplicate attempt/event/population identity | STRUCTURAL FAIL | No | No | No |
| simultaneous view/effect/reamp/crop counted as an independent performance | STRUCTURAL FAIL | No | No | No |
| required raw source hash missing/mismatched | STRUCTURAL FAIL | No | No | No |
| decoder/config/calibration identity mismatch not caught at acquisition boundary | STRUCTURAL FAIL | No | No | No |
| derived reference cannot be regenerated under frozen decoder/provenance | STRUCTURAL FAIL | No | No | No |
| event cites evaluated DI/model-derived evidence | STRUCTURAL FAIL | No | No | No |
| clock transform requires waveform/spectral/onset/model alignment | STRUCTURAL FAIL | No | No | No |
| frozen hardware-only clock map invalid/unresolvable | STRUCTURAL FAIL | No | No | No |
| impossible reference state transition under frozen semantics | STRUCTURAL FAIL according to preregistered tolerance | No | No | No |
| unresolvable pitch/string/event-birth ambiguity exceeds frozen tolerance | STRUCTURAL FAIL | No | No | No |
| unmatched note-on/note-off condition exceeds frozen tolerance | STRUCTURAL FAIL | No | No | No |
| same-key overlap violates frozen reference-state semantics | STRUCTURAL FAIL | No | No | No |
| reference event lacks required raw physical provenance | STRUCTURAL FAIL | No | No | No |
| rights/provenance binding is invalid for captured material | INADMISSIBLE / STRUCTURAL-GOVERNANCE FAIL | No correctness rescue | No | No |
| calibration material leaks into holdout population | STRUCTURAL-GOVERNANCE FAIL | No | No | No |
| protected/disallowed composition contaminates captured population | INADMISSIBLE | No correctness rescue | No | No |
| operator/model blinding boundary was breached | GOVERNANCE/STRUCTURAL FAIL | No | No | No |
| raw physical state was manually rewritten after capture | STRUCTURAL FAIL | No | No | No |
| a needed truth decision can only be resolved by listening/looking at DI | STRUCTURAL FAIL | No | No | No |

The exact tolerance policy for any condition that is not zero-tolerance must be frozen before real capture. Until then, no numeric tolerance is implied by this document.

## 9. Whole-population versus local structural failure

A critical item to freeze before capture is the **scope of rejection**.

To avoid post-hoc salvage, the structural preregistration must state in advance which failures:

- reject the whole candidate population;
- reject a complete preregistered unit such as a session/player only if that unit-level rule was frozen before capture; or
- are permitted only under a frozen numeric tolerance without deleting individual events/takes.

The safest default for integrity-breaking defects—roster mismatch, provenance/hash failure, use of evaluated-audio/model truth, post-capture manual editing, duplicate population inflation, broken preregistration—is whole-population rejection.

No “drop just the bad event/take and continue” rule may be invented after structural inspection.

## 10. Structural audit must remain reference-blind

Allowed evidence:

- manifest/plan/preregistration bytes and hashes;
- Git/GitHub attestation evidence already defined by governance;
- raw physical reference streams;
- raw clock/sync streams;
- hardware/firmware/configuration/calibration identities;
- deterministic derived reference;
- rights/provenance records where relevant;
- objective file/schema/identity data.

Forbidden evidence:

- evaluated DI waveform/content for truth repair;
- spectrograms derived from evaluated DI for truth repair;
- evaluated-DI onset detectors;
- waveform/audio cross-correlation for reference alignment;
- Basic Pitch output;
- V6 output;
- correctness matches/errors;
- precision/recall/TP/FP/FN;
- protected-song results;
- any model-informed judgement of which take/event should survive.

## 11. Correctness-stage outcomes

Only a population that passes all earlier gates can reach correctness.

At correctness stage:

- use the immutable bound population;
- use the already-frozen V6 method and external scoring framework;
- run the no-real-correctness synthetic/contract harness first;
- run exactly one official ordinary-GitHub-CPU correctness evaluation;
- preserve all model estimates/events as required by frozen V6;
- apply only the already-frozen statistical gates;
- do not tune, re-record, repair, drop events, redefine strata, alter tolerance, or rerun because of observed performance.

Possible result classes conceptually include frozen pass/fail outcomes under the existing scoring preregistration. This document does not add a new success threshold or redefine V6.

A correctness failure is **not** evidence that capture/reference hardware was defective unless a defect was independently established under a frozen non-correctness gate. Correctness cannot retroactively authorize a retake.

## 12. Phase/authority matrix

| Phase | May inspect raw physical reference? | May inspect evaluated DI content? | May inspect model output? | May retake? | May change thresholds? |
|---|---:|---:|---:|---:|---:|
| paper design | no real holdout exists | N/A | No holdout output | N/A | design values may be proposed prospectively |
| non-holdout calibration | Yes, calibration only | only if a prospectively defined engineering task requires it, never for future holdout truth and never with holdout data | No holdout model feedback | calibration data is not holdout | Yes, before freeze only |
| pre-capture authorization | identity/provenance only | No holdout content | No | N/A | No after freeze |
| acquisition QA | health/transport/status only | technical transport metrics only if frozen; not musical/truth inspection | No | Yes only on frozen objective FAIL | No |
| admitted population binding | hashes/identities | No content | No | No | No |
| reference-blind structural audit | Yes | No for truth/alignment/repair | No | No | No |
| synthetic no-real-correctness harness | synthetic fixtures only | no real holdout correctness | No real holdout model output | No | No |
| official correctness | reference + evaluated DI through frozen pipeline | pipeline executes frozen analysis | Yes, one official reveal | No | No |
| post-correctness decision | frozen outputs | as already generated by official workflow | Yes | No | No |

## 13. Proposed configuration identity checks

Before future capture, decide and freeze exactly when each identity is checked:

- hardware configuration SHA;
- firmware versions;
- reference-decoder blob SHA;
- decoder configuration SHA;
- calibration artifact IDs/SHAs;
- clock/sync configuration SHA;
- capture software/workflow version;
- evaluated-DI path identity;
- pitch-reference path identity;
- excitation-reference path identity.

Recommended design direction:

- verify identity before session start;
- record identity in every attempt;
- verify again at capture finalization;
- mismatch discovered before attempt start is a pre-capture blocker;
- mismatch arising/detected during an attempt may be a retake-eligible acquisition failure **only if prospectively codified**;
- mismatch discovered only later in a passed/admitted take becomes non-rescuable structural failure, not permission to substitute another take.

## 14. Clock/sync failure partition

This boundary is especially important.

### Retake-eligible only when immediately machine-observable under frozen QA

Examples, subject to future frozen numeric rules:

- required hardware sync stream absent;
- sync marker count below frozen minimum;
- device reports clock unlock;
- hardware-only drift/jitter metric exceeds frozen QA threshold;
- clock stream corrupt/malformed.

### Non-rescuable when discovered after admission as a semantic/alignment problem

Examples:

- required time mapping cannot be reconstructed under frozen algorithm despite all streams having passed QA;
- reference timestamps are internally contradictory under frozen semantics;
- alignment would require waveform cross-correlation/audio onset/model assistance;
- a post-hoc different fit/model would be needed to make events align.

The latter must close the candidate under its preregistered structural rule rather than trigger a better take.

## 15. Sensor failure partition

### Prospective acquisition-QA failures

Only objective device/transport health conditions with frozen thresholds, e.g.:

- channel absent;
- sensor health flag invalid;
- dropout above frozen limit;
- saturation above frozen limit;
- stuck-state detector above frozen limit;
- stream malformed;
- device disconnect.

### Structural failures

Once an attempt has passed acquisition QA, semantic problems such as these cannot become retake reasons:

- conflicting but transport-valid sensor states;
- an event whose string/fret cannot be resolved under frozen decoder;
- technique state that the decoder cannot classify;
- impossible event ordering;
- unexplained same-key overlap;
- derived event without complete physical provenance.

This distinction prevents “the reference looked wrong on a hard note” from being rebranded as sensor failure.

## 16. Rights/provenance failure partition

Before capture, missing or inadequate rights are a blocker.

After capture, if an executed/bound rights record is later shown not to authorize the captured performance for product validation, the affected data is inadmissible. It cannot be replaced selectively after correctness exposure. Any prospective recollection would constitute a new separately preregistered population and must remain isolated from prior model outcomes.

Protected-song contamination follows the same fail-closed direction.

## 17. Population-count integrity

The following never multiply independent evidence:

- reamps;
- effects/presets;
- microphone variants;
- DI plus amp views;
- crops/windows of the same take;
- transformed/augmented copies;
- repeated exports/encodings;
- raw versus processed reference views.

The independence unit remains the underlying admitted real performance/take as frozen in the slot roster.

Any derived views may be retained for engineering diagnostics if separately authorized and clearly non-counting, but they cannot inflate the >=1,000 V6-positive evidence requirement.

## 18. Synthetic-test obligations before any V2 code becomes authoritative

If the proposed physical-reference acquisition classes are implemented, synthetic/contract tests must prove at least:

- each proposed failure code is rejected unless present in the prospectively frozen plan vocabulary;
- every code has a nonempty frozen criterion;
- thresholds/config identities are plan-bound and cannot be changed in the final manifest;
- first-pass admission still holds;
- later attempts after first pass still fail;
- sensor/sync failure cannot be asserted from model/correctness fields;
- structural ambiguity cannot be relabeled as acquisition failure;
- capture roster remains exact;
- no model/correctness observation field can enter the manifest/plan;
- new physical-reference file identities are required for admitted attempts;
- raw physical reference, excitation reference, and clock/sync provenance are distinct from evaluated DI where the design requires distinct channels;
- fail-closed authority remains: passing governance still authorizes at most the future reference-blind structural audit.

The existing passed artifact-proof trust boundary should be reused, not rewritten, unless new code creates a concrete new loophole.

## 19. Freeze checklist before real capture authorization

This matrix is not capture-ready until all blanks are prospectively resolved:

- exact V2 failure-code names, if V2 is adopted;
- exact machine-observable criteria for every code;
- numeric clipping limit;
- clock marker requirements;
- drift/jitter limits;
- sensor dropout/saturation/stuck limits;
- exact configuration-check timing;
- exact structural zero-tolerance versus numeric-tolerance policy;
- exact whole-population/unit-level rejection scope for every structural condition;
- exact technique support/exclusion policy;
- exact rights/provenance forms and hashes;
- exact operator/blinding controls;
- synthetic tests proving anti-relabeling behavior.

All must be frozen before the first real holdout attempt. None may be chosen from holdout outcomes.

## 20. Current authority state

This document advances paper governance only.

Current state remains `DESIGN_ONLY`:

- no procurement/spending;
- no performer/vendor contact or hiring;
- no calibration recording;
- no holdout recording;
- no data acquisition;
- no candidate-media access;
- no Basic Pitch/V6 correctness;
- no Modal/Vercel heavy-GPU/L4;
- no Production/customer promotion.

Fail-closed outputs remain:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected-song embargoed

The next design-only step, if continuing, is to translate the now-frozen semantic/matrix direction into a **proposed V2 manifest/plan schema and synthetic-test plan** without activating it, purchasing hardware, or recording data.
