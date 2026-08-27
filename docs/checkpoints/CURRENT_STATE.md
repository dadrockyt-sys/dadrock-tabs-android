# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm baseline preserved; Families #1–#14 fully consumed/sealed. V145 Rhythm Decoder is preregistered and its first CPU-only core + unit tests are implemented. CPU proof is the immediate next step. No Modal/L4/GPU without fresh explicit authorization.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU without fresh explicit authorization.
- V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`; render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark, not unseen holdout. V5 holdout permanently consumed.

## Permanent progress-percentage reporting
- Accepted family #10: **Pitch Content 35.4%** (`0.35406698564593303`), **Pitch + timing 6.7%** (`0.06698564593301436`), **String/fret + timing 5.5%** (`0.05454545454545454`), **Chord/voicing 5.8%** (`0.0580511402902557`), **Measure coverage 100%**, **PDF event fidelity 100%**.
- Keep dimensions separate; recompute only if accepted baseline changes.

## Accepted baseline — LOCKED / UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity1.0.
- Full gold critical1712; pitch0.35406698564593303; pitch/timing0.06698564593301436; string/fret/timing0.05454545454545454; chord/voicing0.0580511402902557; coverage1.0.

## V144 consumed state
- Families #1–#14 are consumed. Never replay/reselect/retune them or use their candidate rankings/outcomes to shape a successor.
- Family #14 run `33025902769` / job `98367025091`; no qualifying FIT rule; accepted baseline unchanged.
- Family #14 one-shot workflow deletion commit `443031fd2294e05b23290c71b0e2b712198d842a`.
- Family #14 trigger deletion commit `e9536f2b4c122741f50aa317e2bbd332d0a9d03b`.
- Family #14 report remains preserved at blob `a13df8e17ae2c813d4602dd10dd642327a5d2b75`; CPU proof blobs remain preserved.
- Current accepted-baseline FIT residual remains `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`, blob `b9794a7b8a882ba9ade5e8095f112d4be45e47e6`.

## V145 Rhythm Decoder — FROZEN CPU ARCHITECTURE
- Preregistration: `docs/v145-rhythm-decoder-preregistration.md`.
- Preregistration commit: **`5a5c59d305dffba16090bc7dc37d33ecbb17e295`**.
- Frozen architecture: **V5 Rhythm-separated events -> normalized evidence -> timing/onset lattice -> pitch lattice -> constrained guitar-state decoder -> candidate event stream -> existing scorer/render/PDF gates**.
- Protected input: current V5 Rhythm-separated output; V5 itself remains immutable.
- V5 is register-gated event separation, not waveform/stem separation. Current ranges: bass28-51, rhythm52-63, lead64-76.
- Initial timing lattice uses caller-supplied quantum and proposes nearest + neighboring grid points without reference data.
- Initial pitch lattice carries generated MIDI only; no new pitch invention in this proof.
- Standard tuning frozen initially to MIDI `(40,45,50,55,59,64)` strings6->1, max fret24.
- Runtime core may not accept gold/reference/FIT/validation/canary inputs.
- V145 remains separate from V144 Family #15.

## V145 CPU implementation — IMPLEMENTED / PROOF PENDING
- Core module: `modal/v145_rhythm_decoder.py`.
- Core implementation commit: **`17f08592ece48ee2519d3449f5f6f7d5ff8ffa39`**.
- Unit tests: `modal/tests/test_v145_rhythm_decoder.py`.
- Test creation commit: **`42cb52a86c4f364bdd042620ee13f65a8f43f971`**.
- Implemented deterministic generated-event normalization with frozen aliases/defaults and input immutability.
- Implemented explicit-grid timing candidates with raw-onset preservation, nearest + neighbor proposals, non-negative timing cost, deterministic selection.
- Implemented physically valid guitar-position enumeration for standard tuning and max fret.
- Implemented bounded simultaneous guitar-state enumeration: exact MIDI preservation, unique strings, fret-span guard, deterministic ranking.
- Implemented continuity-aware state selection using hand-position transition cost without changing MIDI.
- Implemented nearest-timing CPU proof decoder that groups simultaneous evidence, assigns valid guitar states, and leaves unplayable onsets undecoded rather than fabricating notes.
- Core has no Modal dependency.
- 12 unit tests cover aliases/defaults/invalid input, lattice construction, timing validation, MIDI preservation, unique strings, continuity, grouped decode, fail-closed unplayable events, >6-note refusal, runtime API label isolation, no Modal dependency, determinism.
- These tests have not yet been executed by a definitive branch CPU workflow at this checkpoint.

## Fixed dependency identities
- Residual analyzer `27ac8699279db8fc0208d067479ad3751da1a630`; singleton reconstruction search `70880d26418d907cc702233af37bcc4b643e3a57`; singleton policy `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Pitch-position shift `f69755b61bdcdf3a669847ce7e425289b4b0927f`; pitch shift `d9998c59acddba070069668d62bcb1c3cdaf2b05`; triple conjunction `ef9768a127472d7ce0746fdf21164d33e5117ea4`.
- Staged selector `d176a9a69366e192e6fa75bc1039661e977f0bfa`; measure guard `4a1364204dd1e720c09d835ec3995c165047de98`; context split `2da58508f2132660ad317ee63d5cb043d58285f0`; config `9b93205cb47bc7718685b9d41b263778107801ce`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`; freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`; PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## EXPLICIT NEXT STEPS — CONTINUATION CONTRACT
1. Stay only on `v143-contextual-prune-lobo`; never main/Production/frontend/Bass/Lead.
2. Preserve family #10 accepted baseline and percentages **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
3. Run a definitive GitHub CPU-only proof for `modal/v145_rhythm_decoder.py` + `modal/tests/test_v145_rhythm_decoder.py`.
4. If the proof fails, fix only within the frozen preregistered contract and rerun CPU proof; checkpoint changes.
5. If proof passes, persist proof metadata and checkpoint it.
6. Only after CPU proof, design the next CPU stage for better timing inference/sequence decoding; do not use gold at runtime.
7. No live Modal/L4/GPU/audio benchmark until separately and explicitly authorized by the user.

## Current stop point
- V144 accepted baseline unchanged and fully protected.
- Family #14 fully sealed.
- V145 preregistration frozen at `5a5c59d...`.
- V145 core implementation commit `17f08592...`; tests commit `42cb52a8...`.
- Immediate next action: definitive CPU unit-test proof only.
