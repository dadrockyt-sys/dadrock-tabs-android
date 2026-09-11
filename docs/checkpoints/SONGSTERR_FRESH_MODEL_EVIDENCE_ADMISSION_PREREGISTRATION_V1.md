# Songsterr Fresh — Model-Evidence Admission Research Preregistration V1

Status: preregistered research plan; **not an admission authority**

## Why this exists

Policy C-S solved reproducibility for one exact Codespaces boot/session surface, but the qualified-session review demonstrated that reproducibility does not imply model correctness. In particular, the historical MIDI-55 boundary event was exactly reproducible while the already-existing independent CQT diagnostic did not strongly support its selected pitch.

The already-observed CQT rank/margin values for the current song MUST NOT be used to choose or tune a new admission threshold. This plan therefore freezes a new method before that method is evaluated on the authorized song.

## Hard scope

This research must remain:
- reference-blind with respect to any tab/transcription reference for the authorized song;
- independent of the archived V143/Gomyway scorer and all professional/reference scorer logic;
- independent of Basic Pitch activation values, Basic Pitch onset/decision surfaces, Basic Pitch note-span amplitude/confidence, and Basic Pitch decoded note ends;
- duration-free;
- non-promotional until a later explicit policy review;
- event-identity preserving: raw Basic Pitch events remain intact even when independent corroboration fails.

The method may consume only:
- the exact isolated-guitar WAV bound to the model evidence;
- each candidate event's already-selected MIDI identity and source-start time;
- frozen structure identity for provenance/binding only.

It may not use downstream duration evidence or customer output as a correctness signal.

## Candidate independent corroborator

V1 will combine two independently computed audio-domain views over a fixed post-onset window. Neither view has yet been evaluated against the current song's two observed mismatch events.

### Channel A — harmonic-stack spectral competition

For each event, compute a fixed-window spectral representation from the isolated-guitar waveform and score the selected MIDI against a fixed competitor set:

`selectedMidi + {-12, -2, -1, +1, +2, +12}`

Competitors outside the playable MIDI range are omitted. The selected MIDI and every competitor are scored with the same fixed harmonic-stack function using the candidate fundamental plus a fixed number of integer harmonics and fixed harmonic weights. No Basic Pitch activations or decision values enter this score.

The exact FFT/window length, harmonic count, harmonic weights, bin/interpolation rule, and tie behavior must be frozen in code before any run on the authorized song.

### Channel B — time-domain periodicity/subharmonic competition

Using the same fixed audio window but an independent time-domain calculation, compare periodic support for the selected MIDI against the same fixed competitor set. The implementation may use normalized autocorrelation or an equivalently explicit deterministic periodicity calculation, but its lags/interpolation/tie behavior must be frozen before authorized-song execution.

This channel exists specifically so spectral-harmonic dominance alone cannot become the sole correctness authority.

## Candidate corroboration semantics

Before authorized-song execution, the implementation must freeze a conservative rule with these properties:
- both independent channels must identify the selected MIDI as the unique best candidate among the fixed comparison set;
- an exact or numerically unresolved tie fails closed;
- missing/insufficient audio support fails closed;
- disagreement between the two channels fails closed;
- no observed authorized-song margin may become a tolerance;
- the current historical CQT values for MIDI 55 or MIDI 64 may not determine any numeric cutoff.

Initial research output classifications are limited to:
- `independently-corroborated-candidate`
- `not-independently-corroborated`
- `insufficient-evidence`

These labels are research outputs only. They do not delete/change the upstream event and do not set customer eligibility.

## Controlled-fixture requirement before authorized-song execution

The method must first pass a deterministic synthetic/controlled fixture suite with known generated pitch content. The suite must be committed before its results are used to change the method.

Minimum fixture families:
1. isolated monophonic plucked-string-like tones spanning low/mid/high playable MIDI;
2. octave-confusion cases with deliberately strong second harmonics;
3. neighboring-semitone adversarial cases;
4. fixed dyads and triads to expose conservative failure under polyphony;
5. deterministic low-level-noise and low-support cases that must fail closed rather than invent certainty.

The controlled suite must use fixed seeds and exact fixture identities. Failing fixtures may cause the research method to be revised, but any revision requires a new preregistration version before that revised method is tested on the authorized song.

## CI / execution boundary

Hosted CI may exercise only controlled fixtures and contract/self-tests. Hosted CI results are not authority for the authorized song.

The authorized song may be evaluated with this new method only after:
1. implementation is frozen in a branch commit;
2. controlled-fixture CI is green;
3. hard non-promotion tests are green;
4. a **new** Policy C-S Codespaces epoch is enrolled and qualified on that frozen commit.

The currently live qualified C-S epoch at source commit `b2f246769340e4f7f6929e679692956c731efd93` must not pull the new code or be reinterpreted as authority for it.

## Promotion boundary

Even a fully green controlled suite plus a green authorized-song corroboration run does **not** automatically set `modelValidationComplete:true`.

A separate explicit policy review must decide whether the new independent corroboration contract is sufficient to authorize a customer-eligible subset. Until that decision:
- `modelValidationComplete:false`
- customer eligible events: `0`
- `mayAdvanceDelivery:false`
- duration research remains paused.
