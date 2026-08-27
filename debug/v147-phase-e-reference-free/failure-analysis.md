# V147 Phase E — Reference-Free Failure Analysis

This is descriptive mechanism analysis only. It does not open Gold/reference content and does not construct a new candidate.

## Immutable identities
- Accepted family #10: 1144 events / `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`
- V147 candidate: 1144 events / `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`
- Preserved decisions: 1144 rows / file SHA256 `3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9`

## Change topology
- Changed events: **247** (137 down-one / 110 up-one)
- Changed onsets: **217**
- Singleton changed onsets: **106**
- Polyphonic changed onsets: **111**
- Changed events by accepted onset size: `{'1': 106, '2': 100, '3': 34, '4+': 7}`
- Changed notes per changed onset: `{'1': 190, '2': 24, '3': 3}`

## Structural effects
- Pitch-collision onsets introduced: **18**
- String-collision onsets introduced: **0**
- Same-string changed events: **198**; different-string changed events: **49**

## Frozen evidence margins
- Nearest decision-gate excess median: **4.166 dB**
- Nearest decision-gate excess p10/p90: **0.726 / 11.777 dB**
- Within 0.5 dB of at least one frozen gate: **17 / 247**
- Within 1.0 dB of at least one frozen gate: **30 / 247**
- Composite winners that were not fundamental-only winners: **2 / 247**

## Safety
- Gold/reference read: **NO**
- Audio read/decode or HPSS/CQT recompute: **NO**
- Modal/L4/GPU: **NO**
- Candidate construction/search/retuning: **NO**
- main/Production modification: **NO**
