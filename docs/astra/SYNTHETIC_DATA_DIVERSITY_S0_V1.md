# Astra synthetic data diversity Phase S0 V1

Date: 2026-09-27  
Status: decision-ready design only. No corpus rendered. No optimizer work executed. P3 remains sealed.

## Question

Can a small, provenance-clean procedural guitar corpus provide enough supervised diversity to justify one bounded temporal-context training pilot, without using noncommercial sample libraries or pretending synthetic success proves real-world transcription quality?

The answer is currently **unresolved**. This document defines one testable hypothesis and a hard budget.

## Existing eight-capture development inventory

All eight are already-exposed P1/P2 development evidence. They are not untouched validation.

Frozen representation used in the tiny-fit work: 22,050 Hz, hop 512, 200 frames, so each selected crop is approximately **4.644 s**.

| Capture | Selected start frame | Selected duration | Raw/scorable reference events known from committed receipts | Unresolved selected labels | Full capture duration | Full source-event total | Additional launch-ready windows |
|---|---:|---:|---:|---:|---|---|---|
| P1 chords Drop3_7 directinput | **unknown** | 4.644 s | 6 | 0 | **unknown** | **unknown** | **unknown** |
| P1 scales Ab directinput | **unknown** | 4.644 s | 8 | 0 | **unknown** | **unknown** | **unknown** |
| P1 singlenotes allsinglenotes directinput | **unknown** | 4.644 s | 1 | 0 | **unknown** | **unknown** | **unknown** |
| P1 techniques PalmMute directinput | **unknown** | 4.644 s | 1 | 0 | **unknown** | **unknown** | **unknown** |
| P2 chords Drop3_7 directinput | 0 | 4.644 s | 4 | 0 | **unknown** | **unknown** | **unknown** |
| P2 scales Ab directinput | 336 | 4.644 s | 8 raw; 7 in prior scored screen | 0 | **unknown** | **unknown** | **unknown** |
| P2 singlenotes allsinglenotes directinput | 163 | 4.644 s | 1 | 0 | **unknown** | **unknown** | **unknown** |
| P2 techniques PalmMute directinput | 21526 | 4.644 s | 2 | 0 | **unknown** | **unknown** | **unknown** |

Evidence sources include `TINY_FIT_PILOT_REAL_RESULT_V3.json`, `P2_CROSS_PERFORMER_SCREEN_RESULT_V1.json`, `P1_P2_ACTIVATION_DIAGNOSTIC_RESULT_V1.json`, and `P1_P2_COMBINED_DIAGNOSTIC_RESULT_V1.json`.

The missing full-duration/event/window totals are deliberately left unknown. They cannot be recovered honestly from code alone, and this S0 work does not reopen or download source media merely to fill the table.

The crop selector searches source-driven repeated-attack and individual-attack candidates and chooses the earliest launch-ready window, not necessarily frame zero. More possible windows inside the same performance would increase crop count but **not** independent-performer diversity.

## Recommended generator: repo-owned Karplus-Strong / short digital-waveguide family

Use one small procedural plucked-string generator written for this repository, with no sample pack, learned generator, external impulse response, or copyrighted song MIDI.

Core signal model:

- six virtual strings with standard tuning;
- delay-line / Karplus-Strong excitation with per-example damping, dispersion approximation, pick position, excitation color, pickup position, and body/amp filtering;
- exact command timeline records intended string, fret, attack, release/damp command, and technique parameter;
- render at 44.1 kHz internally, deterministic resample to 22.05 kHz, with all event times rounded only at the final sample grid;
- synthetic cabinet/body coloration must be generated from analytic filters or repo-authored coefficients, not third-party IR assets.

This is a **hypothesis generator**, not an acoustic truth engine.

### Label semantics

Generator control commands are exact provenance labels. They do not automatically prove that the rendered waveform contains uniquely recoverable string/fret information.

- Pitch and commanded onset are the first feasibility target.
- String/fret labels may be used for diagnostics because the generator has string-specific physical parameters, but success must not be interpreted as real-guitar string-identification validity.
- Same-pitch unisons on different strings are deliberately included; pitch-onset scoring collapses acoustically identical simultaneous pitch onsets while string multiplicity remains separately recorded.
- Palm mute is modeled by stronger bridge damping, shorter effective decay, altered high-frequency loss, and optional low-level percussive excitation. A short envelope by itself is **not** called realistic palm muting.

### Attack, sustain, release and retrigger rules

Each rendered event stores:

- command attack time;
- realized first excitation sample;
- commanded damping/release time;
- signal tail end;
- string/fret/pitch provenance;
- whether it is a same-fret retrigger;
- whether another note is already ringing.

Training onset target uses the realized excitation time, not a guessed crop edge. Offset targets use the damping/release command plus a documented tail policy; both command and acoustic-tail times are retained.

Repeated same-string/same-fret attacks must explicitly re-excite the string while prior energy may remain. Polyphonic attacks can share a sample time.

### Required negatives

At least 35% of training windows contain one or more negative structures, not just digital silence:

- active sustain with no new attack;
- long decay tail;
- ringing strings while another string attacks;
- same pitch continuing through a crop boundary;
- muted/percussive excitation with weak or intentionally absent pitched sustain;
- low bounded pink/white/electronic noise;
- pick/finger-like transient without a valid fret label;
- true silence.

Negative event generation is independent of pitch/template identity so the model cannot identify labels from a generator shortcut.

## Diversity and split

Templates are algorithmic exercises, never excerpts of copyrighted songs.

Template families:

1. isolated notes over all playable pitch classes;
2. ascending/descending scales with variable interval patterns;
3. dyads/triads/tetrads with voicing changes;
4. repeated attacks including same-fret reattacks;
5. legato-like sustain transitions without new pluck labels;
6. palm-mute hypothesis examples;
7. mixed positive/negative windows.

Split **before rendering** by template family instance and all derived relatives:

- train 70%;
- synthetic validation 15%;
- synthetic test 15%.

All transpositions, tempo variants, noise variants and timbre variants of one underlying phrase stay in the same split. Related reversed/shifted variants are grouped conservatively.

In addition, reserve disjoint parameter bands for validation/test for at least pick position, damping, body-filter resonance and noise level. Different RNG seeds alone do not count as independence.

Unsupported or weakly supported in S0: bends, vibrato intonation trajectories, slides with realistic fret noise, harmonics, tapping, pick scrapes, feedback, amp distortion dynamics, bass, mixed-song source separation, and microphone-room variation.

## Rights/provenance check

The proposed pilot intentionally has no third-party audio assets.

Verified from official project pages on 2026-09-27:

- NumPy is distributed under a modified/BSD-style permissive license: https://numpy.org/about/
- Python 3 uses the Python Software Foundation License Version 2: https://docs.python.org/3/license.html

This is enough to avoid a noncommercial dependency for the proposed generator implementation, but **software licenses do not determine ownership or commercial rights in generated audio**.

Therefore:

- no external sample libraries or cabinet IRs are permitted in S0;
- no copyrighted melodies/tabs are used as templates;
- each example records generator version, seed, parameters and source template ID;
- any future addition of samples, IRs, pretrained generators, or external compositions requires a separate rights review;
- this document is not a legal opinion and does not claim the synthetic output is commercially cleared beyond its controlled provenance.

Rejected alternatives:

- noncommercial guitar corpora: incompatible with the intended product path;
- commercial sample libraries: licensing/output redistribution conditions vary and add avoidable provenance uncertainty;
- neural audio generators: materially higher compute and weaker exact event-label provenance;
- full physical finite-element/string-body simulation: excessive implementation/render cost for this hypothesis test.

## Hard S0 pilot ceiling

No pilot is authorized by this document. If separately authorized:

- maximum rendered examples: **3,000**;
- maximum rendered audio: **6,000 seconds** total;
- clip length: 1.0-3.0 s, mean <= 2.0 s;
- PCM storage ceiling: **350 MB** including audio + metadata;
- render wall clock: **20 CPU minutes**;
- sample rate stored for training: 22.05 kHz mono;
- fixed root seed: **20260927**;
- automatic retries: **0**;
- paid compute: **$0**;
- P1/P2 media access during synthetic render/train: **none**;
- P3: sealed.

## One candidate and one comparator

Candidate: **5-frame temporal-context MLP**

- input: five consecutive 192-bin CQT frames, centered on target frame;
- encoder: `Linear(960,128) + ReLU`;
- state head: same six x 21 classes;
- onset head: same six onset logits;
- no recurrence, attention, pretrained weights, or architecture sweep.

Comparator: current per-frame `Linear(192,128)+ReLU` with the same heads/objective.

Both use the exact same synthetic split, fixed seed, decoder thresholds and optimizer budget.

Prospective fit ceiling:

- at most **500 optimizer steps per model**;
- at most **2 models total**;
- at most **60 CPU minutes total** including evaluation;
- fixed learning rate and loss weights frozen before launch;
- no threshold search;
- no post-result epoch extension;
- no automatic retry.

## Numeric advancement gates

These answer only whether the synthetic/temporal hypothesis merits another bounded development step.

### Synthetic held-out gate

All required:

- pitch-onset precision >= 0.90;
- pitch-onset recall >= 0.90;
- pitch-onset F1 >= 0.90;
- onset+offset F1 >= 0.80;
- repeated same-fret attack recall >= 0.85;
- false-positive rate on negative-only audio <= 0.10 events/second;
- each supported template family onset F1 >= 0.80;
- unresolved/nonfinite label count = 0.

### Candidate-vs-comparator gate

On the same synthetic test split:

- candidate onset F1 must exceed comparator by >= 0.03 **or**
- candidate repeated-attack recall must exceed comparator by >= 0.10 without losing >0.02 onset precision.

Otherwise the temporal-context candidate is stopped; no architecture sweep follows automatically.

### Later P1/P2 development transfer gate

This requires a **separate real-media authorization** and a frozen V2 evaluator/manifest. No P1/P2 access is authorized by S0.

If later authorized, all required before claiming useful real transfer:

- aggregate pitch-onset F1 >= 0.60;
- aggregate precision >= 0.55;
- aggregate recall >= 0.60;
- each of chords/scales/singlenotes/techniques pair-macro onset F1 >= 0.45;
- repeated-attack recall >= 0.60 where denominator > 0;
- report onset+offset F1 and real negative/sustain false-positive denominators;
- candidate must not trail the same-budget comparator in aggregate onset F1;
- thresholds remain frozen prospectively.

Passing this gate means only “worth another bounded development iteration.” It is not product readiness, unseen-performer generalization, bass validation, source separation validation, or customer-delivery approval.

## Stop conditions

Stop immediately on any of:

- provenance or license uncertainty requiring an unreviewed external asset;
- storage/render/time ceiling reached;
- malformed/nonfinite labels;
- split contamination by template relatives;
- candidate/comparator gate failure;
- need for threshold rescue;
- any request to open P3;
- any need to reuse P1/P2 media without a fresh scoped authorization.

## Decision

The smallest justified next experiment is the synthetic-only S0 pilot above. It tests two things cheaply: whether procedural diversity can support the event task at all, and whether explicit five-frame context improves attack handling over the current per-frame comparator.

It does **not** test real-guitar transfer until a separate P1/P2 authorization is granted.
