# Open-corpus harmonic candidate-ranking experiment — preregistration

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **PREREGISTERED BEFORE ANY OCTAVE-CONFUSION WINNER RESULT**
Classification: parallel V169-style development; V168 unchanged.

## Why this experiment exists

Guitar-TECHS P1 and independent-player P2 both showed that a literal fundamental can be weaker than its second harmonic while a multi-harmonic lower-vs-+12 score still retained the correct lower reference pitch. The exact P1 formula replicated on P2 without modification.

Those results are promising but reference-grounded: the tested lower pitch was already known. This next experiment is stricter. For each known single-note event it creates the predeclared octave-confusion set `{midi-12, midi, midi+12}` and makes the **winner selection from audio only**. The reference MIDI is used only to construct the controlled benchmark candidate set and to score correctness afterward; it is not used inside the candidate score or tie-break.

This is still a controlled confusion benchmark, not end-to-end candidate generation. A later experiment must use candidates produced without reference-derived pitch sets.

## Frozen candidate score V1

For candidate fundamental frequency `f`, measure narrow-band FFT power at `h*f` for harmonics `h=1..8`, using the existing fixed ±35-cent bands and the same event windows/alignment procedure already frozen in `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`.

Let `E1..E8` be those powers and `S` be power at the **subharmonic** `f/2`.

Frozen harmonic weights:
`w = [1.00, 0.85, 0.72, 0.62, 0.54, 0.48, 0.42, 0.38]`.

Define:
- `T = sum(w[h] * E[h])` for h=1..8;
- `O = 1.00*E1 + 0.72*E3 + 0.54*E5 + 0.42*E7`;
- `subPenalty = 1 + 0.75 * S/(T + eps)`;
- **candidateScore = (T + O) / subPenalty**.

Rationale:
- a false pitch one octave low can align the true harmonic series mainly onto its even-numbered harmonics; the added absolute odd-harmonic term `O` should penalize that failure mode without requiring a strong literal E1;
- a false pitch one octave high has its `f/2` near the actual lower fundamental, so `S` provides a symmetric subharmonic penalty;
- the formula has no reference value, MIDI-distance prior, lowest-pitch preference, string prior, or winner-side ground-truth input.

## Candidate set / tie rule

For each event with all candidates in MIDI 0..127, rank exactly:
`[midi-12, midi, midi+12]`.

Winner = maximum `candidateScore`.

Exact numerical ties are broken by the **smallest MIDI number**, prospectively and without reference use.

## Event framing

Use the same fixed P1/P2 event framing already used by the prior harmonic study:
- global capture alignment scan over -0.12..+0.12 seconds in 10 ms increments;
- analysis windows at onset+offset plus deltas `{0.08, 0.13, 0.18, 0.24}`;
- use the window with maximum first-five-harmonic evidence for each candidate/event;
- FFT window 0.186 s, max FFT size 32768, ±35-cent harmonic bands.

The alignment/event onset comes from the public development reference and therefore this experiment is explicitly a feature benchmark, not a deployment simulation.

## Frozen evaluation outputs

For each of four development capture sets:
- P1 direct input;
- P1 mic/amp;
- P2 direct input;
- P2 mic/amp;

report:
- evaluated event count;
- true-pitch winner count/rate;
- false-low (`midi-12`) winner count/rate;
- false-high (`midi+12`) winner count/rate;
- true-vs-best-wrong score margin median and p10;
- weak-fundamental subset (`E1 < E2`) true-winner rate;
- very-weak subset (`E1 < 0.5*E2`) true-winner rate where examples exist.

## V1 prospective success gate

Call V1 a **candidate-feature PASS** only if ALL are true:
1. true pitch wins at least **95%** of evaluated events in each of the four P1/P2 capture sets;
2. true pitch wins at least **90%** of weak-fundamental events in every capture set with >=10 weak events;
3. no capture set has >5% false-low winners;
4. no capture set has >5% false-high winners.

If V1 fails, checkpoint the failure before defining any V2. Do not silently retune this exact V1 after results.

Even a V1 PASS is not yet an end-to-end breakthrough. Before integrating into a transcription challenger, freeze the passed score and validate it on a separate corpus or reference-blind candidate stream not used to define V1.

## V168 / safety boundary

- V168 Policy A/B unchanged.
- GOAT holdout selection unchanged.
- V168 reference-facing score calls remain 0.
- No GOAT/Lenny professional reference content may enter this experiment.
- CPU only; fresh explicit authorization required before GPU/CUDA/Modal.
- No `main` / Production changes.
