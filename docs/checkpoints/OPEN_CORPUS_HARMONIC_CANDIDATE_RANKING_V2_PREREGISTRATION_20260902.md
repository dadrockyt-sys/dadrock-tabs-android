# Open-corpus harmonic candidate-ranking V2 — preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **V2 FROZEN BEFORE ANY REAL P1/P2 CANDIDATE-RANKING RESULT**
Classification: parallel V169-style development; V168 unchanged.

## Evidence boundary

Candidate-ranking V1 failed at its synthetic guard before any Guitar-TECHS P1/P2 archive was downloaded or any real candidate winner was observed. Dedicated V1 fail checkpoint:
- `docs/checkpoints/OPEN_CORPUS_HARMONIC_CANDIDATE_RANKING_V1_SYNTHETIC_FAIL_20260902.md`
- creation commit `a506577498dce1583913e0a1fe23de1d0611f45e`.

Therefore V2 is being defined with **0 real P1 candidate-ranking winner observations and 0 real P2 candidate-ranking winner observations**.

The V2 change is based only on:
1. the already-checkpointed P1/P2 reference-grounded finding that odd-harmonic evidence can support a lower pitch even when literal f0 is weak; and
2. the V1 synthetic failure showing that a literal `f/2` penalty alone is insufficient for an octave-too-high candidate.

## Controlled candidate benchmark

For each Guitar-TECHS single-note event, the controlled candidate set remains exactly:
`{midi-12, midi, midi+12}`.

The public reference MIDI constructs this controlled benchmark set and is used after ranking to determine correctness. It is **not** an input to the V2 candidate score or tie-break.

This remains a feature benchmark, not an end-to-end candidate generator.

## Frozen V2 score

For a candidate frequency `f`, measure narrow-band FFT power at `h*f` for harmonics `h=1..8` using the same fixed ±35-cent bands as the prior study.

Let `E1..E8` be those powers and:
`M = max(E1..E8, eps)`.

Compress candidate harmonic dynamic range with a fixed fourth-root transform:
`Qh = (Eh / M)^0.25`.

Frozen harmonic-participation weights:
`w = [1.00, 0.85, 0.72, 0.62, 0.54, 0.48, 0.42, 0.38]`.

Define candidate harmonic coverage:
`C = sum(w[h] * Qh)` for h=1..8.

Now evaluate the **lower-octave odd-harmonic hypothesis** at frequencies:
`f/2, 3f/2, 5f/2, 7f/2`.

Let their powers be `L1, L3, L5, L7`, normalized against the same candidate `M`, and define:
`L = 1.00*(L1/M)^0.25 + 0.72*(L3/M)^0.25 + 0.54*(L5/M)^0.25 + 0.42*(L7/M)^0.25`.

Frozen V2 score:
`candidateScoreV2 = C / (1 + 0.50 * L/(C + eps))`.

Winner = maximum V2 score. Exact numerical ties are broken by smallest MIDI, prospectively.

## Why V2 differs from V1

V1 could choose +12 because a false upper-octave candidate may treat the real `2*f0` as its own fundamental while its penalty inspects only the potentially weak literal true `f0`.

V2 instead asks whether the candidate has broad harmonic participation **and** whether an octave-lower hypothesis has odd-harmonic support. For a false +12 candidate, the lower true hypothesis can be visible at `3f/2`, `5f/2`, and `7f/2` even when `f/2` itself is weak.

The fourth-root compression is fixed to prevent one extremely strong partial from dominating a candidate that explains very few harmonics.

## Frozen framing / analysis surface

Preserve the existing development framing:
- sample-rate native FFT analysis;
- 0.186 s analysis window;
- FFT size = next power of two up to 32768;
- ±35-cent band power using band maximum;
- global development-corpus alignment scan -0.12..+0.12 s in 10 ms increments;
- per-candidate windows at onset+alignment+`{0.08, 0.13, 0.18, 0.24}` seconds;
- each candidate chooses the window with maximum sum of its first five raw harmonic powers;
- candidates exactly `[-12, 0, +12]` semitones.

## Synthetic development guard — must pass before real data

Before P1/P2 download or real ranking, V2 must select MIDI 45 (A2, 110 Hz) over MIDI 33/57 for **all four** fixed one-second, 48 kHz synthetic harmonic-amplitude fixtures:

1. `normal-decay`: `[1.00, 0.70, 0.50, 0.35, 0.25, 0.18, 0.12, 0.08]`
2. `weak-fundamental`: `[0.08, 1.00, 0.75, 0.10, 0.55, 0.08, 0.35, 0.05]`
3. `even-heavy-distortion`: `[0.25, 1.00, 0.15, 0.70, 0.10, 0.45, 0.08, 0.30]`
4. `very-even-heavy`: `[0.10, 1.00, 0.05, 0.80, 0.02, 0.60, 0.01, 0.40]`

These fixtures are design/sanity cases, not independent validation data. Failure of any fixture rejects V2 before real data.

## Real P1/P2 prospective V2 success gate

Only if the four synthetic guards pass may the workflow download P1/P2 and evaluate real controlled candidates.

Call V2 a **candidate-feature PASS** only if ALL are true:
1. true pitch wins >= **95%** of evaluated events in each of P1 DI, P1 mic/amp, P2 DI, P2 mic/amp;
2. true pitch wins >= **90%** of weak-fundamental events in every capture set with >=10 weak events;
3. false-low (`midi-12`) winners <= **5%** in every capture;
4. false-high (`midi+12`) winners <= **5%** in every capture.

Report true-vs-best-wrong normalized margin median, p10 and minimum, but do not use those diagnostics to alter this V2 gate.

If V2 fails on real data, checkpoint before any V3. Do not silently retune V2 after seeing results.

A V2 PASS still requires separate-corpus/reference-blind validation before integration into any transcription challenger.

## V168 / safety boundary

- V168 Policy A/B unchanged.
- GOAT holdout selection unchanged.
- V168 reference-facing score calls remain 0.
- No GOAT/Lenny professional reference content in this experiment.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- No `main` / Production changes.
