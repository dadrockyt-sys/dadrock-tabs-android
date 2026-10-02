# Clean Stem Separation and Bleed Suppression Architecture V1

Date: 2026-10-02
Branch: `astra-work`
Status: **DESIGN ONLY / NO MODEL EXECUTION**

## Objective

Produce cleaner isolated instrument stems for downstream recognition and tablature by treating source separation as a staged inference problem:

`mix -> coarse multi-stem separation -> target recognition -> bleed estimation -> residual/cross-stem cleanup -> consistency reconstruction -> quality gate`

The goal is not mathematically perfect isolation. The goal is to minimize musically misleading bleed while preserving the target instrument strongly enough for note transcription.

## Why one-pass separation is insufficient

A single separator can:
- leave guitar harmonics in bass;
- leave cymbals/snare transients in guitar;
- leak vocals into sustained guitar;
- split one instrument across target + other;
- smear transients;
- create holes if masks are made too aggressive.

Therefore "cleaner" cannot simply mean stronger noise gating.

## Stage 1 — six-stem coarse separation

Preferred technical family for evaluation:
- BS-RoFormer / MelBand-RoFormer class;
- six stems: vocals, drums, bass, guitar, piano, other.

Reason:
- direct guitar and bass stems are materially more useful than a four-stem `other` bucket;
- current public separation systems based on BS-RoFormer expose guitar/bass/piano separately;
- modern ensemble systems explicitly optimize bleedlessness as well as source fullness.

Do not freeze a production checkpoint until license/weight provenance is cleared.

## Stage 2 — mixture-consistency residual

Let:
- `x` = original mixture
- `s_i` = preliminary separated stems

Compute:
`r = x - sum_i(s_i)`

The residual is not assumed to be "noise." It is evidence of separation error.

Use it only as a diagnostic and later as a constrained redistribution source.

Hard rule:
- cleaned stems should sum back toward the original mixture;
- cleanup must not create energy from nowhere;
- target preservation outranks aggressive silence.

## Stage 3 — cross-stem competition map

For each time-frequency bin, estimate whether energy belongs more strongly to:
- guitar
- bass
- drums
- vocals
- piano
- other

Rather than independently gating every stem, calculate relative confidence between stems.

Example:
- a 3 kHz transient strong in drums and weak in bass should be suppressed from bass;
- a 90 Hz sustained harmonic strong in bass and weak in guitar should be suppressed from guitar;
- shared harmonic energy with similar confidence should remain soft/uncertain rather than be hard-deleted.

This avoids the common failure where all stems independently retain the same bleed.

## Stage 4 — target-preserving bleed suppressor

For each target stem `T`:

1. build a target-confidence mask from the target separator output;
2. build an interference-confidence mask from all competing stems;
3. identify only high-confidence interference;
4. attenuate interference gradually;
5. preserve ambiguous bins;
6. retain transients belonging to the target;
7. reconstruct with original mixture phase or phase-consistent reconstruction where supported.

Recommended first-pass attenuation:
- soft suppression, not binary zeroing;
- never remove a bin solely because another stem has energy there;
- require a confidence margin before attenuation.

No numeric suppression threshold should be frozen before a rights-cleared synthetic/paired development set exists.

## Stage 5 — target recognizer feedback

Use the unified recognition layer as a verifier, not as a separator.

Examples:
- cleaned bass should remain confidently bass-like;
- cleaned guitar should remain guitar-like;
- drum probability in cleaned bass should decrease;
- vocal probability in cleaned guitar should decrease.

If cleanup reduces target confidence more than interference confidence, reject the cleaned version and keep the pre-cleaned stem.

This creates a fail-safe against over-cleaning.

## Stage 6 — note-aware cleanup for guitar/bass

After a rough target transcription exists, use predicted note/harmonic structure only as a **secondary confidence cue**.

For a hypothesized note with fundamental `f0`:
- expected harmonic bands: `f0, 2f0, 3f0, ...`
- protect energy near those harmonics;
- attenuate competing-stem energy farther from target harmonics more aggressively;
- never delete unmatched energy merely because the transcriber failed to explain it.

This is especially useful for:
- bass fundamentals vs kick drum;
- distorted guitar harmonics vs cymbals;
- long sustained guitar/bass notes vs vocal bleed.

It must never be allowed to manufacture notes that were not acoustically present.

## Stage 7 — optional second separator / ensemble agreement

Where compute allows, compare two independent separators or two checkpoints.

Use agreement:
- energy present in target stem in both systems -> high target confidence;
- energy assigned to target by one system but a competing stem by another -> ambiguous;
- energy consistently assigned to another instrument -> high bleed confidence.

This is preferable to simply averaging stems.

An ensemble can improve robustness because different separators make different leakage errors.

## Stage 8 — consistency reconstruction

After cleanup, enforce approximately:

`clean_vocals + clean_drums + clean_bass + clean_guitar + clean_piano + clean_other ~= original_mix`

Any removed target-stem energy should either:
- be reassigned to a competing stem where confidence is high; or
- remain in `other/residual`.

Do not silently discard substantial mixture energy.

## Quality metrics

For paired synthetic/known-stem development material, measure:

### Target preservation
- SI-SDR / SDR where legitimate ground truth exists
- target spectral energy retained
- note-event recall before vs after cleanup

### Bleed suppression
- interference energy reduction
- recognition probability of competing instruments
- false note events attributable to competing stems
- cross-stem duplicate-event rate

### Consistency
- reconstruction error: `x - sum(clean_stems)`
- phase/transient artifact checks

### Downstream utility
The most important project metric:
- note transcription precision/recall/F1 on cleaned target vs raw separated target.

A separator improvement that sounds cleaner but reduces transcription accuracy is not a win for Jimmy PAIge.

## Proposed experiment ladder

### S0 — synthetic mixtures
Use isolated rights-cleared guitar/bass/control samples already cataloged.
Construct mixtures from independently known components at prospectively frozen levels.

Purpose:
- prove bleed detector and consistency math;
- test whether cleanup removes known interferers without harming known target.

This would create exact stem ground truth cheaply, but it is a separate empirical boundary and is not authorized by this design document.

### S1 — paired real multitracks
Use real isolated instrument + corresponding real mix.

Purpose:
- evaluate actual separator leakage and cleanup.

### S2 — full-song validation
Only after S0/S1 pass:
- real songs;
- six-stem separation;
- recognition;
- cleaned target transcription;
- tab mapping.

## Important distinction: synthetic mixtures

Synthetic mixtures are valid for testing the cleanup algorithm because the exact original components are known.

They are **not** sufficient evidence that the system separates mastered commercial music equally well.

## Recommended architecture

```
original mix
   |
   v
6-stem RoFormer
   |
   +--> vocals
   +--> drums
   +--> bass ------+
   +--> guitar ----+--> cross-stem confidence
   +--> piano -----+        |
   +--> other -----+        v
   |                  bleed suppressor
   |                        |
   +------ residual --------+
                            |
                       recognizer gate
                            |
                     note-aware guard
                            |
                   mixture consistency
                            |
                     cleaned stems
                            |
               instrument transcription
                            |
                      tab decoder
```

## Current recommendation

Do not chase "zero audible bleed" as the primary optimization target.

Optimize for:
1. target-note preservation;
2. reduction of false notes caused by other stems;
3. deterministic mixture consistency;
4. measurable downstream transcription improvement.

A tiny amount of harmless audible bleed is preferable to deleting a real guitar or bass note.

## Current boundary

No separator checkpoint was downloaded.
No audio was processed.
No synthetic mixtures were created.
No inference or empirical optimization was performed.

The next safe preparation step is to define a rights-cleared synthetic mixture matrix from the existing guitar/bass/control fixture pool, with frozen gain/SNR combinations and exact expected components, while leaving execution disabled.
