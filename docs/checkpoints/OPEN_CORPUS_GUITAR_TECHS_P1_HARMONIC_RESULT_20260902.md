# Open-corpus Guitar-TECHS P1 harmonic-octave study — first real result

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`  
Classification: **PARALLEL V169-STYLE DEVELOPMENT / NOT V168 / EXPLORATORY P1 RESULT**

## Frozen scientific boundary

The open-corpus breakthrough lane was preregistered before this real P1 aggregate result in:
- `docs/checkpoints/OPEN_CORPUS_BREAKTHROUGH_PREREGISTRATION_20260901.md`
- creation commit `f0b966df4881311456b5c455161431d8a771114e`.

The tested hypothesis was that lower-fundamental evidence can survive cases where the literal fundamental is weaker than the octave harmonic by using the odd-harmonic structure (3f0/5f0/7f0) that a +12-semitone interpretation cannot explain as its own harmonic series.

This lane is deliberately isolated from V168. It does not modify V168 Policy A/B, GOAT holdout selection, or V168 scoring.

## Public corpus identity

Dataset: Guitar-TECHS, public Zenodo record `14963133`, P1 single-note archive.

Downloaded archive:
- file `P1_singlenotes.zip`;
- official Zenodo MD5 verified PASS: `ca0c4674dde3805574685a313f7c39eb`;
- observed archive SHA256: `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`.

Inputs used inside the archive:
- `midi/midi_allsinglenotes.mid`;
- `audio/directinput/directinput_allsinglenotes.wav`;
- `audio/micamp/micamp_allsinglenotes.wav`.

No third-party audio/reference bytes were committed to the repository.

## Implementation

Analysis script:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`
- creation commit `3f67a134f646cc35f12e9c49e545e8b0c1df5fd1`.

Successful workflow head:
- commit `517d3e6a8c52bde0e3aae21f0c0804fd931f9ae1`;
- workflow `.github/workflows/open-corpus-guitar-techs-harmonic-study.yml`.

GitHub Actions:
- run `33575395022`;
- job `100078129343`;
- conclusion **SUCCESS**;
- Ubuntu 24.04 / Python 3.10.21;
- CPU-only.

Pinned analysis dependencies:
- numpy 2.1.3;
- soundfile 0.13.1;
- pretty_midi 0.2.11.

Synthetic weak-fundamental self-test passed before the real P1 run:
- fundamental/second ratio `0.006504821516786469`;
- odd/even score `0.5573768809186809`;
- true-minus-octave `0.21977413333145895`.

## P1 results

The MIDI contained 142 notes across six per-string tracks (23/24/23/24/25/23 notes).

### Direct input
- analyzed notes: **142**;
- sample rate: 48 kHz;
- duration: 552.0 s;
- estimated MIDI-to-audio offset: -0.11 s;
- literal fundamental weaker than second harmonic: **47.183098591549296%** (67/142);
- literal fundamental less than half the second harmonic: **30.985915492957748%** (44/142);
- frozen harmonic score preferred the true lower pitch over the +12-semitone interpretation: **100.0%** overall;
- among weak-fundamental notes: **100.0%** (67/67);
- among very-weak-fundamental notes: **100.0%** (44/44);
- median odd/even support: `1.2477667116098246`;
- median normalized true-minus-octave margin: `0.43499407504790505`.

### Mic/amp
- analyzed notes: **142**;
- sample rate: 48 kHz;
- duration: 552.0003541666666 s;
- estimated MIDI-to-audio offset: -0.10 s;
- literal fundamental weaker than second harmonic: **28.169014084507044%** (40/142);
- literal fundamental less than half the second harmonic: **14.788732394366198%** (21/142);
- frozen harmonic score preferred the true lower pitch over the +12-semitone interpretation: **100.0%** overall;
- among weak-fundamental notes: **100.0%** (40/40);
- among very-weak-fundamental notes: **100.0%** (21/21);
- median odd/even support: `2.585733682024488`;
- median normalized true-minus-octave margin: `0.6157824198109649`.

Aggregate report SHA256:
`e804caaeff90a45adee2270c7971b63d2cc9c57cd7c9a0a9c2bdd8f137f98d7a`

Artifact:
- name `guitar-techs-harmonic-study-report`;
- artifact ID `9826466130`;
- uploaded artifact ZIP SHA256 `dccf15a0db604163999fa694e2146d78cd3e922bdd84e50a4038cf1a040cd8e1`.

## Interpretation — promising, not yet a claimed breakthrough

This is a strong first signal that a binary `fundamentalPresent` requirement can discard legitimate guitar notes: nearly half of P1 DI notes had less energy at f0 than at 2f0, yet the pre-result harmonic-series score still favored the lower ground-truth pitch for every tested note, including all 44 very-weak-fundamental DI cases.

However, this P1 result alone is **not** sufficient to claim a general transcription breakthrough. The score is evaluated around known reference pitches and its lower-vs-octave construction structurally rewards odd-harmonic evidence. It must replicate on an independent player/capture set before being promoted to a serious candidate feature, and later must be tested in a reference-blind candidate-selection setting where false lower-octave hypotheses are also possible.

## Next frozen-safe experiment

Use **P2 single notes as an independent-player replication with the exact same harmonic formula and summary definitions**. Do not change weights, frequency-band widths, weak-fundamental thresholds, or success metrics based on this P1 result before P2 replication.

If P2 replicates strongly, then freeze a V169-style candidate feature and test it reference-blind on a separate development/validation split. P2 is therefore confirmatory for this exact P1 formula, not another tuning set.

## V168 remains unchanged

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**  
V168 reference-facing score calls: **0**.

No GPU/CUDA/Modal was used. `main` / Production were not modified.
