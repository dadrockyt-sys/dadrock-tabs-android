# Songsterr Fresh — Independent Corroboration V1 Policy Review

Recorded: 2026-09-11 America/Toronto

Status: **REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**

## Decision

Independent Corroboration V1 must not be promoted into a customer-admission authority.

The first authorized-song execution completed successfully under a qualified Policy C-S epoch and produced research labels for all 1,140 qualified events, but the preregistered prospective stress review failed to provide the discrimination needed for promotion.

## Evidence considered

Authorized-song aggregate research result:

- 471 `independently-corroborated-candidate`
- 667 `not-independently-corroborated`
- 2 `insufficient-evidence`
- 1,140 total qualified events
- session verified before and after research

These aggregate labels were preregistered as research outputs only and were never customer-eligibility decisions.

### Prospective stress case: MIDI 64 near 79.6261406 s

Before the V1 authorized-song run, this event had already been identified as the stronger of two cross-surface semantic mismatch cases because an earlier independent CQT diagnostic ranked the selected pitch first against nearby semitone and octave alternatives.

Under frozen Independent Corroboration V1, the event failed the two-channel corroboration rule:

- classification: `not-independently-corroborated`
- reason: `CHANNEL_DISAGREEMENT_OR_NON_UNIQUE_SELECTED`
- Channel A (spectral harmonic stack): selected MIDI 64 was **not** unique best; best competitor MIDI 52; selected score `5.474197256333346`; best competitor score `6.228767267035149`; margin `-0.7545700107018032`
- Channel B (time-domain periodicity): selected MIDI 64 **was** unique best; selected score `0.5568231769085561`; best competitor MIDI 65; best competitor score `0.4897826856809774`; margin `0.06704049122757871`

The frozen V1 contract requires both channels to identify the selected MIDI as unique best. Therefore the event correctly fails closed under V1.

## Interpretation

This is not treated as a code failure, model failure, or authority failure. Policy C-S reproducibility remained valid and the research evaluator completed as designed.

It is a **policy adequacy failure for promotion**: the preregistered V1 corroborator does not yet have enough demonstrated external/controlled validity to justify using its positive subset as customer-eligible truth.

The result must not be repaired by relaxing Channel A, changing competitor offsets, changing harmonic weights, changing the tie tolerance, or choosing a new margin from the observed authorized-song values. Doing so would be post-hoc tuning to the evaluation song.

## Consequences

- Independent Corroboration V1 remains frozen and retained for provenance/research diagnostics.
- The 471 `independently-corroborated-candidate` events remain research labels only.
- No V1 result may delete, rewrite, or silently change upstream event identity.
- `modelValidationComplete:false` remains unchanged.
- customer-eligible events remain `0`.
- `mayAdvanceDelivery:false` remains unchanged.
- duration authority remains unchanged and duration research stays paused.
- No GOAT/V143/reference/professional scorer path is reopened by this result.

## Future research boundary

Any successor corroborator must be a new preregistration/version. It must not be tuned to make the observed MIDI-55 or MIDI-64 authorized-song cases pass. Those events are now evaluation history and may be used only as retrospective stress diagnostics for future frozen methods.

A successor may be developed only from independently justified signal-processing principles and/or predeclared controlled/public validation data that are separate from the authorized song. Any new thresholds, competitor definitions, harmonic weighting, time-domain rule, or channel-combination policy must be frozen before the successor is evaluated on the authorized song.

Until such a successor passes its own controlled validation and separate policy review, V1 does not authorize customer delivery.
