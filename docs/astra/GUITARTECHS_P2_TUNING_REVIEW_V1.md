# Guitar-TECHS P2 tuning review V1

Date: 2026-09-21

## Question

Can Astra freeze P2's six open-string MIDI pitches without assuming standard tuning merely because it is common?

## Evidence

The already-authorized P1/P2 inventory receipt freezes the exact `allsinglenotes` MIDI structure. P1 exposes six explicit string tracks `e/B/G/D/A/E`; every track contains 23 consecutive semitone pitches spanning 22 semitones:

- e: 64–86
- B: 59–81
- G: 55–77
- D: 50–72
- A: 45–67
- E: 40–62

This establishes the dataset's P1 per-string "all notes" schema as open string plus 22 chromatic fret positions.

P2 uses the identical explicit string-track names. Five tracks match P1 exactly and also contain 23 consecutive pitches:

- e: 64–86
- B: 59–81
- G: 55–77
- A: 45–67
- E: 40–62

P2's D track is the sole exception: it has 22 note-ons and exactly the consecutive set 51–72. Relative to the same D-string schema, the only missing endpoint is MIDI 50. An alternative open D#3 interpretation would require the 22-fret endpoint MIDI 73, which is also absent and would contradict the track's explicit `D` identity plus the shared dataset pattern.

The Guitar-TECHS project page independently states that the Fishman Triple Play Connect captures MIDI notes independently from each string; the inventory does not use any model prediction or P3 material.

## Decision

P2 tuning is frozen as standard six-string tuning:

- low-to-high MIDI: `40, 45, 50, 55, 59, 64`
- pitches: E2 A2 D3 G3 B3 E4

The D3 conclusion is a **structural inference from a single missing open-note event**, not a claim that MIDI 50 was directly present in P2's file. This distinction is retained in the machine-readable receipt.

Receipt: `docs/astra/GUITARTECHS_P2_TUNING_EVIDENCE_V1.json`  
SHA-256: `5474eaccdf651c637dc7b3b2145098fe050714b77542b843742ac2f645702715`

No alignment, training, P3 access, model execution or customer-delivery authorization is granted by this review.
