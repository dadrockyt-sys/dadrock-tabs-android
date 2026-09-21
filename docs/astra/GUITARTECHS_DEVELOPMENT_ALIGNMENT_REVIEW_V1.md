# Guitar-TECHS P1/P2 development alignment evidence V1

Date: 2026-09-21  
Authoritative workflow run: `35565975272`  
Source commit: `f6c0d17d367b1a264529ffce66a0a6d919bfd147`

## Result

The frozen P1/P2 alignment policy completed across all eight authorized development archives without opening P3 or running model training.

Across 92 underlying performances and four capture paths per performance, the clean run evaluated **368 capture alignments**:

- **275 complete**
- **93 abstained**

V1 primary training content is chords, scales, ordinary single notes, and PalmMute. Within that primary subset:

- **336 candidate capture paths**
- **256 accepted**
- **80 abstained and excluded**

Per performer:

- P1: 136 / 168 primary paths accepted; 32 abstained.
- P2: 120 / 168 primary paths accepted; 48 abstained.

The primary abstentions were caused only by the already-frozen timing gates:

- `MAXIMUM_BOOTSTRAP_LAG_MAD_EXCEEDED`: 62 occurrences.
- `MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_EXCEEDED`: 47 occurrences.

No primary path failed minimum matched fraction or minimum MIDI onset-group count.

## Capture-view pattern

The gate reveals a meaningful robustness difference across capture paths without changing the policy after seeing results.

P1 primary accepted / 42:
- directinput 41
- micamp 41
- ego 33
- exo 21

P2 primary accepted / 42:
- directinput 39
- micamp 37
- ego 19
- exo 25

This does **not** justify loosening the alignment thresholds. The pre-frozen failure action is to exclude the individual recording-session + capture-path pair and abstain.

## Frozen downstream rule

The exact 80 primary abstentions are frozen in `docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_EVIDENCE_V1.json`.

All other capture paths belonging to the frozen primary-content universe are eligible for downstream V1 development, subject to every later gate. The receipt also freezes:

- authoritative run and source commit;
- per-archive Actions artifact digest;
- SHA-256 of each detailed alignment receipt;
- alignment implementation and script identities;
- accepted-primary-set digest;
- abstained-primary-set digest;
- exact runtime versions.

Frozen receipt SHA-256: **`8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae`**.

The four technique families Bendings, Harmonics, PinchHarmonics and Vibrato remain auxiliary/held out regardless of their alignment status.

## Gate decision

`ALIGNMENT_CORRECTION_NOT_VERIFIED` is cleared **only for the accepted primary capture set defined by this receipt**. It is not a claim that every Guitar-TECHS capture is aligned well enough to train.

No feature generation, model import, real training, P3 opening, Production change or customer-delivery authorization occurred.
