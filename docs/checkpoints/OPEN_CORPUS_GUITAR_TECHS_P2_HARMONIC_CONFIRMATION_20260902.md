# Open-corpus Guitar-TECHS P2 harmonic-octave confirmation

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`  
Classification: **INDEPENDENT-PLAYER CONFIRMATION / PARALLEL V169-STYLE DEVELOPMENT / NOT V168**

## Purpose

P2 was reserved immediately after the first successful P1 result as an independent-player confirmation of the **exact same frozen P1 harmonic formula**. No harmonic weights, band widths, weak-fundamental thresholds, or success metrics were changed after seeing P1 and before this P2 run.

P1 result checkpoint:
- `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P1_HARMONIC_RESULT_20260902.md`;
- creation commit `5ef3a3dff39e46e31527e2ef7824a655338a2539`.

P2 confirmation workflow was created at commit:
`3ad977f11d3eba3af6324d80a626ef315476a3b1`.

## Public corpus identity

Dataset: Guitar-TECHS, Zenodo record `14963133`, P2 single-note archive.

`P2_singlenotes.zip`:
- official Zenodo MD5 `40fbf03d8b04bb2cf42df20f36dc2254` verified **PASS**;
- observed SHA256 `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`;
- 18 archive entries;
- synchronized per-string MIDI plus direct-input, mic/amp, ego, and exo captures.

Inputs used:
- `P2_singlenotes/midi/midi_allsinglenotes.mid`;
- `P2_singlenotes/audio/directinput/directinput_allsinglenotes.wav`;
- `P2_singlenotes/audio/micamp/micamp_allsinglenotes.wav`.

No third-party audio/reference bytes were committed to the repository.

## Frozen implementation reused

Analysis source remained:
`validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`

The P2 report explicitly recorded:
- `formulaChangedAfterP1=false`;
- `v168PoliciesModified=false`;
- `goatHoldoutSelectionModified=false`;
- `v168ReferenceFacingScoreCalls=0`.

GitHub Actions:
- run `33575653483`;
- job `100078933242`;
- conclusion **SUCCESS**;
- CPU-only, Ubuntu 24.04 / Python 3.10.21.

The exact P1 synthetic self-test again passed before P2.

## P2 results

The P2 MIDI contained **137** notes across six per-string tracks (23/23/23/22/23/23 notes).

### Direct input
- analyzed notes: **137**;
- sample rate: 48 kHz;
- duration: 552.0 s;
- estimated MIDI-to-audio offset: -0.08 s;
- literal f0 weaker than 2f0: **13.86861313868613% = 19/137**;
- literal f0 < half 2f0: **0.0% = 0/137**;
- exact frozen P1 harmonic score preferred the true lower pitch over +12 semitones: **100.0% overall**;
- among weak-fundamental notes: **100.0% = 19/19**;
- median odd/even support: `11.935522532478922`;
- median true-minus-octave margin: `0.909773723392629`.

### Mic/amp
- analyzed notes: **137**;
- sample rate: 48 kHz;
- duration: 552.0003541666666 s;
- estimated MIDI-to-audio offset: -0.07 s;
- literal f0 weaker than 2f0: **8.02919708029197% = 11/137**;
- literal f0 < half 2f0: **2.9197080291970803% = 4/137**;
- exact frozen P1 harmonic score preferred the true lower pitch: **100.0% overall**;
- among weak-fundamental notes: **100.0% = 11/11**;
- among very-weak-fundamental notes: **100.0% = 4/4**;
- median odd/even support: `18.556828551730433`;
- median true-minus-octave margin: `0.9396754431215367`.

P2 aggregate report SHA256:
`840dea4d62b0adbf2ca24ea5ff49103a0c5bc4597afd012200a169c548cc3ce2`

Artifact:
- `guitar-techs-p2-harmonic-confirmation`;
- artifact ID `9826574099`;
- artifact ZIP SHA256 `c48751a75d489ffbd0b7d1e96aa67aae230d0e522908339118aad6d93f10af7c`.

## Combined evidence

The exact P1 formula now preferred the lower ground-truth pitch over the +12-semitone interpretation on:
- P1 DI: 142/142;
- P1 mic/amp: 142/142;
- P2 DI: 137/137;
- P2 mic/amp: 137/137.

Total capture-note evaluations: **558/558 = 100%**.

For notes where literal f0 was weaker than 2f0:
- P1 DI 67/67;
- P1 mic/amp 40/40;
- P2 DI 19/19;
- P2 mic/amp 11/11.

Combined weak-fundamental evaluations: **137/137 = 100%**.

For the very-weak subset (`f0 < 0.5 * 2f0`):
- P1 DI 44/44;
- P1 mic/amp 21/21;
- P2 DI none;
- P2 mic/amp 4/4.

Combined very-weak evaluations with examples present: **69/69 = 100%**.

## Interpretation

This **replicates the P1 signal on an independent professional player with different hardware/capture conditions without changing the formula**. It materially strengthens the case that a strict binary `fundamentalPresent` condition is leaving usable guitar-pitch evidence on the table.

This is now a **candidate breakthrough in feature design**, but it is not yet proof of end-to-end transcription improvement. The test still begins from a known reference pitch and asks lower-vs-upper-octave support. The next required scientific step is a true candidate-selection experiment in which the algorithm receives competing pitch hypotheses and must choose using audio-only harmonic evidence, including false lower-octave candidates.

## Next safe experiment

Freeze a reference-blind **candidate harmonic-coherence score** before testing it on a reserved corpus/capture set. The score should reward multi-harmonic coherence and specifically require odd-harmonic evidence so a false pitch one octave low cannot win merely because its second harmonic coincides with the actual fundamental.

Development/tuning may use P1/P2 because they are now explicitly development data. Preserve EGSet12 as benchmark-only by default; do not inspect/tune on it yet.

## V168 unchanged

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**  
V168 reference-facing score calls: **0**.

No GPU/CUDA/Modal was used. `main` / Production were not modified.
