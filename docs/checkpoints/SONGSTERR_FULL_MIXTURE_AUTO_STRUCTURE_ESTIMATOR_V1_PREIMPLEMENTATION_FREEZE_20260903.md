# FULL_MIXTURE_AUTO_STRUCTURE_ESTIMATOR_V1 — PRE-IMPLEMENTATION FREEZE

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`REFERENCE-BLIND CPU WAVEFORM ESTIMATOR AUTHORIZED / SHADOW ONLY / REFERENCE SCORING NOT AUTHORIZED`**

## Purpose

Build the first genuinely full-mixture structure estimator for the DadRock dual-context path. Unlike V34 tempo diagnostics, this estimator must derive structure from the original/normalized mixture waveform itself rather than note events or a separated guitar carrier.

This is independently designed DadRock research motivated by the already recorded public Songsterr architecture clues. It is not a reconstruction of Songsterr private code.

## Scientific boundary

Allowed:

- pure CPU Python;
- standard-library waveform/sample processing;
- deterministic synthetic waveform fixtures;
- full-mixture PCM as the only future runtime signal source;
- output in the frozen Phase 3 trusted mixture-observation schema;
- shadow-only Phase 3/4 consumption after a later separately frozen wiring step.

Forbidden:

- GuitarSet, SplitMySong, GOAT or any reference corpus read/score;
- Basic Pitch/transcribed note events as estimator input;
- V143/separated guitar carrier as estimator input;
- analyzer-reported tempo/measureGrid as estimator truth;
- GPU/CUDA/Modal;
- Product/PDF mutation;
- Production deployment/promotion.

## Frozen module

`analyzer/full_mixture_auto_structure_estimator_v1.py`

Primary API:

```python
estimate_full_mixture_structure_v1(samples, sample_rate) -> dict
```

Input samples are mono float-like PCM values. A future adapter may downmix normalized stereo to mono, but that runtime adapter is outside this phase.

## Frozen signal front-end

- analysis window: **20 ms**;
- hop: **10 ms**;
- frame energy: mean absolute amplitude;
- novelty: positive frame-energy increase over the median of the previous **8** frames;
- normalize novelty by its global maximum when non-zero;
- onset peak threshold: normalized novelty >= **0.18**;
- local peak radius: **2 hops**;
- onset refractory period: **70 ms**;
- fewer than **4** accepted onsets => tempo unresolved.

This is a first-principles CPU onset-strength front-end. It does not use separated sources or note labels.

## Frozen tempo method

Candidate quarter-note BPM grid: **50.0–220.0 BPM in 0.5 BPM steps**.

For each candidate period P:

1. compute weighted circular phase coherence of accepted onset times modulo P;
2. compute an inter-onset compatibility term from accepted gaps against integer multiples/submultiples of P within a **10% relative tolerance**;
3. combined score = **0.70 phase coherence + 0.30 gap compatibility**.

Select the highest score; deterministic ties choose the candidate nearest the V34-style folded median onset gap, then the lower BPM.

Tempo resolves only when:

- at least 4 onsets;
- winning combined score >= **0.42**.

Reported tempo confidence = winning combined score clamped to `[0,1]`.

## Frozen beat phase

Use the weighted circular mean of accepted onset times modulo the winning quarter-note period. This phase defines the beat lattice used only by this estimator's downstream meter/feel logic.

## Frozen meter/downbeat scope

V1 may emit only:

- `3/4`;
- `4/4`;
- unresolved.

It must **not** guess 6/8 or other compound meters in V1.

For each candidate meter length M in `{3,4}` and every downbeat offset `0..M-1`:

- map onset strength to nearest beat index when within **18% of a beat period**;
- compute mean strength at the candidate downbeat position versus all other metric positions;
- accent contrast = `(downbeatMean - otherMean) / max(downbeatMean, epsilon)`;
- coverage = fraction of metric positions with at least one mapped onset;
- score = **0.75 accentContrast + 0.25 coverage**.

Meter resolves only when:

- winning score >= **0.18**;
- winning score exceeds the other meter's best score by >= **0.04**.

Otherwise time signature remains unresolved.

Meter confidence is the winning score clamped to `[0,1]`.

## Frozen pickup method

Pickup is estimated only when tempo and meter are resolved.

Using the selected downbeat offset, identify the first full-measure downbeat at or after audio time zero. Convert its distance from time zero to quarter-note beats.

- if first downbeat is within **0.20 beat** of zero => pickup `0`;
- otherwise pickup = rounded distance in beats to **3 decimal places**;
- pickup must remain within `[0,32]`, else unresolved.

This phase assumes denominator 4 because V1 meter output is restricted to 3/4 and 4/4.

## Frozen feel method

Feel is inferred only after tempo resolves.

For accepted onset times not within **15% of a beat**:

- straight evidence = closeness to half-beat (`0.5`);
- triplet evidence = best closeness to `1/3` or `2/3` beat;
- evidence window = within **12% of a beat** around target subdivision;
- require at least **4 off-beat** onset observations;
- best family must have normalized evidence >= **0.45** and exceed the other by a factor >= **1.25**.

Then emit `straight` or `triplet`; otherwise feel remains unresolved (`null` in the estimator observation; Phase 3 will retain `auto`).

## Frozen trusted observation output

The estimator returns a Phase 3-compatible observation:

```json
{
  "version": 1,
  "provenance": {
    "sourceKind": "full-mixture",
    "sourceIdentity": "request-audio",
    "referenceBlind": true,
    "referenceRuntimeInputUsed": false
  },
  "tempoBpm": {"value": 120.0, "confidence": 0.7, "method": "waveform-onset-periodicity-v1"},
  "timeSignature": {"value": {"numerator":4,"denominator":4}, "confidence": 0.4, "method": "waveform-accent-meter-v1"},
  "pickupBeats": {"value":0.0, "confidence":0.4, "method":"waveform-downbeat-phase-v1"},
  "feel": {"value":"straight", "confidence":0.6, "method":"waveform-subdivision-evidence-v1"},
  "diagnostics": {...}
}
```

Unresolved fields are `null`/omitted rather than guessed.

The observation must always assert full-mixture/reference-blind provenance. No caller-supplied source kind is accepted by this module.

## Frozen deterministic synthetic tests — A1–A12

A1. Silence => all fields unresolved, no exception.

A2. Too few clicks (<4) => tempo unresolved.

A3. Uniform 120 BPM quarter-note click train => tempo resolves near 120 BPM (absolute error <= 1 BPM).

A4. Uniform 90 BPM quarter-note train => tempo resolves near 90 BPM (absolute error <= 1 BPM).

A5. 4/4 train with deterministic strong accent every four beats => meter resolves 4/4.

A6. 3/4 train with deterministic strong accent every three beats => meter resolves 3/4.

A7. Ambiguous unaccented beat train => meter remains unresolved rather than guessing.

A8. One-beat pickup before accented 4/4 downbeat => pickup resolves near 1.0 beat (absolute error <= 0.15 beat).

A9. Straight eighth-note offbeats => feel resolves `straight`.

A10. Triplet subdivisions => feel resolves `triplet`.

A11. Ambiguous/no offbeat subdivision evidence => feel unresolved.

A12. Output provenance/schema: full-mixture, request-audio, referenceBlind=true, referenceRuntimeInputUsed=false; no Production/reference authorization fields are introduced.

Synthetic audio may use deterministic impulses/click envelopes generated entirely by the verifier. No external audio asset is permitted.

## Integration boundary

Phase 5 estimator implementation/testing does **not** connect it to `/api/analyze-audio-tab` yet.

Current Phase 3 route must continue to pass `mixtureObservation: null` until a separate post-result wiring freeze proves how normalized request audio reaches this estimator without Modal/GPU/Production changes.

## Safety accounting

- reference score calls = 0;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- Basic Pitch events used as estimator input = false;
- separated carrier used as estimator input = false;
- Modal invoked = false;
- GPU used = false;
- Product/PDF modified = false;
- Production modified = false;
- Production promotion authorized = false.

## Success meaning

A synthetic contract pass proves only that the waveform-derived estimator mechanics behave according to this pre-frozen design. It is **not** an accuracy claim on real songs and does not authorize reference-facing scoring or Product use.
