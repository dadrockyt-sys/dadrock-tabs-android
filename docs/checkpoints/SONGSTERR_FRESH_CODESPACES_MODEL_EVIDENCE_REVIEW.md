# Songsterr Fresh — Qualified Codespaces Model-Evidence Review

Recorded: 2026-09-11 America/Toronto

## Scope

This record captures the reference-blind review of the already-qualified Policy C-S Codespaces session. It is measurement-only and non-promotional.

Hard boundaries remain unchanged:
- `modelValidationComplete:false`
- customer eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged / duration research paused
- no reference tab
- no professional scorer
- no archived V143/Gomyway scorer logic
- no threshold sweep

## Qualified session

- source commit: `b2f246769340e4f7f6929e679692956c731efd93`
- session fingerprint SHA-256: `665db72ea170c6ebc51ad34348158bb12a5ded423068519f0281f4c67121ccef`
- session remained verified before and after the review: `true`
- qualified-session event count: `1140`
- hosted observation A baseline event count: `1138`
- semantic count mismatches: `2`
- decoder mechanism counts in qualified session:
  - threshold-onset-pass: `1012`
  - melodia-residual-pass: `128`

## Semantic mismatch 1 — historical MIDI-55 boundary event

- frozen structure slot: `46.151111111111106`
- selected MIDI: `55`
- hosted A count: `0`
- qualified-session count: `1`
- source start: `46.20240952380952`
- Basic Pitch note-span amplitude / legacy onsetConfidence field: `0.4281298518180847`
- decoder mechanism: `threshold-onset-pass`

Independent audio-domain pitch support:
- local semitone rank: `2`
- octave rank: `2`
- selected pitch above floor: `34.8091625213623 dB`
- selected minus best semitone neighbor: `-0.09838294982910156 dB`
- selected minus best compared alternative: `-10.063761711120605 dB`

Interpretation: reproducible on the qualified C-S surface, but the independent CQT support probe does not strongly support the selected MIDI against nearby/compared alternatives. This event must not be treated as validated merely because it is reproducible or because it passed Basic Pitch's threshold-onset decoder path.

## Semantic mismatch 2 — MIDI-64 event

- frozen structure slot: `79.60816326530613`
- selected MIDI: `64`
- hosted A count: `0`
- qualified-session count: `1`
- source start: `79.62614058956916`
- Basic Pitch note-span amplitude / legacy onsetConfidence field: `0.39093825221061707`
- decoder mechanism: `threshold-onset-pass`

Independent audio-domain pitch support:
- local semitone rank: `1`
- octave rank: `1`
- selected pitch above floor: `48.00846176147461 dB`
- selected minus best semitone neighbor: `3.947506904602051 dB`
- selected minus best compared alternative: `3.947506904602051 dB`

Interpretation: this event has materially stronger independent audio-domain support than the MIDI-55 boundary event, but the descriptive support probe is not an admission contract and therefore does not by itself validate or promote the event.

## Current conclusion

Policy C-S has demonstrated reproducible execution on the live Codespaces boot session, but reproducibility and model correctness are separate claims. The MIDI-55 event is the concrete counterexample: it is reproducible on the qualified session while independent audio-domain support is weak/contradictory. Therefore `modelValidationComplete` must remain `false`.

No numerical threshold may be back-fit from these two examples. The next model-validation step must be independently specified before observing additional candidate outcomes, and must remain reference-blind with respect to the archived V143/Gomyway scorer/tab path.
