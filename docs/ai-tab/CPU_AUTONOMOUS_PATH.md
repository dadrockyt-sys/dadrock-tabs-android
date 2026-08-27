# DadRock `/ai-tab` — CPU autonomous transcription path

Updated: 2026-08-27 UTC

## Goal

Produce professional-quality guitar tablature and PDF from audio **without human correction** while avoiding Modal/L4/CUDA/GPU execution. CPU-only GitHub Actions and local deterministic/pretrained CPU inference are allowed under the standing project policy.

## Why the architecture is changing

The V153 attribution work proved that the existing measure-level pitch-content metric can move because a pitch exists elsewhere in the same measure even when the edited event has no local timing support. Event 347's accepted D4 at measure 35 step 9 received coarse pitch-content credit from a Gold D4 at step 4, five grid steps away and outside even the ±2-step gross timing tolerance. Therefore future architecture decisions must prioritize **local onset-aware pitch correctness**, not coarse measure-level pitch histograms.

The old approach also starts from a fixed event stream and tries to repair individual pitches. That is not a plausible route from low note/onset accuracy to professional transcription. The reset starts again at audio and treats note detection, onset timing, sequence decoding, fretboard placement, techniques, and PDF notation as separate stages.

## Frozen stage order

1. **Audio normalization** — exact historical/source audio identity, deterministic decode.
2. **CPU source separation** — Demucs six-source model; use its `guitar` stem as a predefined transcription input. The original mix remains a control.
3. **CPU pretrained note transcription** — Spotify Basic Pitch, fixed published default thresholds, guitar frequency range only. No Gold/reference is available during transcription.
4. **Local timing-aware evaluation** — primary metric is same-pitch onset matching at ±0.5 sixteenth-note step; gross diagnostic at ±2 steps. Measure-level pitch-content is diagnostic only.
5. **Reference-free evidence fusion** — only if stage 3 materially beats the old baseline: combine pretrained note proposals with the existing HPSS/CQT harmonic evidence and onset evidence. No Gold-driven threshold sweeps.
6. **Sequence decoder** — dynamic programming/beam search over complete musical phrases using recurrence, voice leading, chord consistency, hand span, fret movement, string reuse, and playable-position constraints. This replaces isolated one-event edits.
7. **Automatic string/fret assignment** — globally optimized fretboard path rather than independent nearest-position choice.
8. **Technique inference** — bends/slides/hammer-ons/pull-offs from pitch contours and onset/non-onset transitions, using the already-developed contour evidence where useful.
9. **Notation and PDF** — preserve the 100% render-event/PDF identity contract.
10. **Automatic confidence/self-consistency** — compare predefined reference-free inference views and fail conservatively when evidence conflicts; no human correction step.

## Phase-gate philosophy

A stage only advances if it improves the metric it is responsible for. Pitch recognition is judged by local onset-aware pitch matching. Fretboard decoding is judged only after pitch/onset quality is proven. PDF work remains downstream and cannot compensate for weak transcription.

## Cost boundary

- GitHub-hosted CPU: allowed.
- CPU pretrained inference: allowed.
- CPU source separation: allowed.
- Gold/reference scoring on frozen outputs: allowed.
- Modal / NVIDIA L4 / CUDA / GPU execution: **requires fresh explicit user authorization before execution**.

## Immediate experiment

V154 Phase A compares predefined, reference-free CPU transcription branches on the exact historical `gomywayfullaitest.m4a` audio:

- `raw-basic-pitch`: Basic Pitch directly on the normalized mix.
- `demucs6-guitar-basic-pitch`: Basic Pitch on the CPU Demucs `htdemucs_6s` guitar stem.

Both branches are constructed before Gold is opened. No threshold sweep, candidate search, human correction, or post-score tuning is permitted. The purpose is to determine whether a modern pretrained audio front end materially exceeds the existing accepted baseline's ~6.7% local pitch-timing F1 on the same calibration track.
