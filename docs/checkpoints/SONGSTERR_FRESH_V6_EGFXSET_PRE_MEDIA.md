# Songsterr Fresh V6 — EGFxSet Pre-Media Review

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `BLOCKED_AUTHORIZATION_PRE_MEDIA`
Media delta: `0`

## Scope

This checkpoint records metadata-only research for the optional $0 one-file external audio smoke test authorized by `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`. It is not V6 correctness validation, does not authorize Basic Pitch/V6/correctness, and does not replace the budget-paused physical holdout.

Archived V143/Gomyway, Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, and reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched and closed.

## Candidate

Dataset: **EGFxSet — Electric Guitar Effects dataset**
Canonical dataset record: Zenodo DOI `10.5281/zenodo.7044411`, version 1.0.
Independent project description: `https://egfxset.github.io/`.

Published metadata establishes that EGFxSet contains all notes of a standard-tuned 22-fret Stratocaster and that each clean tone has independent string/fret annotation. The official project documentation defines the string-fret tuple as string number `1..6` and fret `0..22`, with `0` denoting an open string.

Zenodo exposes `Clean.zip` with MD5 `cdb1b401960f56becc8640387910e78a`. Its server-side ZIP preview exposes member paths without downloading or decoding audio. A suitable candidate member is:

- archive: `Clean.zip`
- archive MD5: `cdb1b401960f56becc8640387910e78a`
- member: `Clean/Bridge/6-0.wav`
- published physical label: string `6`, fret `0`
- tuning: standard guitar EADGBE
- expected MIDI: `40` (E2)
- preview-reported member size: about `723.0 kB`

The ISMIR 2022 EGFxSet publication is licensed CC BY 4.0; the project describes the dataset as open access. No audio bytes were downloaded, decoded, listened to, or processed during this review.

## Plausibly untouched check

The active branch was reviewed from HEAD `cf222e7f7017ae814290abdddca7b3f0ddf9cbfd`. The latest 100 commit metadata entries searched in this review contained no `EGFx` / `EGFxSet` reference. This is supporting evidence only, not a proof that no historical local access ever occurred.

The candidate was selected from independent metadata before any audio access. No alternate EGFxSet file has been decoded or auditioned.

## Current pipeline entry and physical-position mapping

Current isolated-guitar transcription entry point:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`

Its primary output contains decoded note events with `startSeconds`, diagnostic end, integer `midi`, and confidence. It directly imports and invokes Spotify Basic Pitch exactly once. The frozen defaults match the current V6 settings: minimum MIDI 40, maximum MIDI 88, onset threshold 0.5, frame threshold 0.3, minimum note length 127.7 ms, bends false, melodia true.

The deterministic fresh core is model-free and maps MIDI to playable string/fret positions using standard guitar tuning MIDI `[40,45,50,55,59,64]`. For MIDI `40`, `enumeratePlayablePositions()` yields only the low-E open string: string `6`, fret `0`. Therefore this candidate avoids fretboard ambiguity if Basic Pitch emits MIDI 40.

## Frozen one-file smoke-test procedure

This procedure is now fully frozen prospectively but **must not be executed under the current authorization state**.

1. Candidate identity is fixed to Zenodo version 1.0 `Clean.zip`, archive MD5 `cdb1b401960f56becc8640387910e78a`, member `Clean/Bridge/6-0.wav`.
2. Independent expected label is fixed to string `6`, fret `0`, MIDI `40` under standard EADGBE tuning.
3. No listening, waveform inspection, trimming, onset hand-labeling, denoising, EQ, gain tuning, threshold changes, retries, or alternate-candidate substitution is permitted after execution begins.
4. Run the existing `transcribe_isolated_guitar_basic_pitch.py` exactly once with its frozen V6 defaults on CPU and no optional diagnostic sidecars required for this smoke test.
5. File-level pitch rule is fixed without onset truth and without event selection: the primary decoded-note artifact must be non-empty and the set of MIDI values across **all emitted notes** must equal exactly `{40}`. Repeated/segmented MIDI-40 events are allowed. An empty artifact or any emitted MIDI other than 40 is `FAIL_PITCH`. V6 onset-match scoring is not used and no onset truth is invented.
6. Physical-position rule: map every emitted MIDI event through the unchanged deterministic standard-guitar mapping. `PASS_POSITION` requires every emitted event to resolve exactly to string `6`, fret `0`, reconstructed MIDI `40`. Any unresolved/different position is `FAIL_POSITION`.
7. Runtime rule: `PASS_RUNTIME` requires the one Basic Pitch invocation and deterministic mapping to complete and produce the expected parseable artifacts without retry. Any execution/parsing failure is `FAIL_RUNTIME`.
8. Overall smoke PASS requires `PASS_RUNTIME`, `PASS_PITCH`, and `PASS_POSITION`. Report note count and emitted MIDI histogram for diagnostics. A PASS is encouraging smoke evidence only; a FAIL is diagnostic only.
9. Do not authorize V6, correctness, model validation, customer eligibility, or delivery from this result.

No scoring choice remains to be made after observing candidate output.

## Authorization blocker

The live current-state checkpoint remains:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`

The required transcription entry directly invokes Basic Pitch. Under the checkpoint rule, execution must therefore stop before media access or inference and document the required explicit authorization rather than silently run it.

Required permission, if the user chooses to grant it later:

> Authorize exactly one non-authorizing Basic Pitch smoke run on the frozen EGFxSet candidate `Clean/Bridge/6-0.wav`, using the existing frozen defaults and deterministic mapper, solely for diagnostic external smoke evidence. This does not authorize V6 correctness, model validation, customer eligibility, delivery, tuning, retries, alternate candidates, or any closed/reserved dataset line.

Until that permission exists, status remains `BLOCKED_AUTHORIZATION_PRE_MEDIA` and `MEDIA_DELTA=0`.
