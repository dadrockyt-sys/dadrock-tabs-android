# Jimmy PAIge Astra — Zero-New-Spend Audio Engine Inventory V1

Status: read-only source inventory; no model/audio execution
Date: 2026-09-19 UTC
Repository baseline inspected: `main` at `bb992d901e78ab19645f8edc8e330d5a142ebd8e`

## Decision

The repository contains enough software to build a bounded first development comparison, but it does not contain a proven three-role audio engine.

Best first candidate for an authorized development comparison:

```text
full mix
  -> htdemucs_6s bass or generic guitar stem
  -> pinned Basic Pitch note events
  -> Astra structure/rhythm/fretboard stages
  -> explicit delivery gate
```

This is a candidate, not a quality or rights clearance. It has a direct bass stem and generic guitar stem, fits the existing component inventory and avoids training a new model. It does not distinguish lead from rhythm guitar, and the existing CPU separator timeout is outside Astra's intended 1200-second analyzer ceiling.

## Repository findings

### Whole-mix Basic Pitch analyzer

Source: `analyzer/modal_analyzer.py`, Git blob `c9e407abf1ee12fc986837e55ab9e6561809de4e`.

- Modal Python 3.11 image installs unpinned `basic-pitch` plus FFmpeg.
- The same `predict(audio_path)` call is used for lead, rhythm and bass.
- The selected role changes only tuning/fingering preferences after note inference.
- The analyzer performs no source separation and returns tempo/time signature as null.
- Output is capped at 320 rendered notes even though the upload limit is 15 minutes.
- Worker timeout is 600 seconds with 4096 MB.

Interpretation: useful as a cheap diagnostic baseline and for isolated single-instrument audio. It does not prove that the requested role was extracted from a full mix. Spotify's own README says Basic Pitch works best on one instrument at a time.

Licensing/source evidence:

- Spotify Basic Pitch software license is Apache-2.0, LICENSE blob `dc22a7345838b69ab77a02ff021584383b52d0e8`.
- README blob `97f122a9a1d27417553f7c25c6dd4683b0172e30` describes polyphonic instrument-agnostic AMT, pitch bends, multiple runtimes and the single-instrument limitation.
- Before use, Astra must pin an exact Basic Pitch package/model/runtime identity. Main's unpinned install is not reproducible enough for a benchmark.

### Existing six-stem separator

Sources:

- `analyzer/modal_bts_separator.py`, blob `b5529f5651205ebfee67d30c148df0e8d2391cda`.
- `analyzer/bts-audio-separation-requirements.txt`, blob `5c14da92a617e104a92a8cbb64f0c0d34be89409`.

Observed implementation:

- pins `audio-separator[cpu]==0.30.2`;
- defaults to `htdemucs_6s.yaml`;
- requires vocals, drums, bass, other, guitar and piano outputs;
- runs CPU-only with one shift, overlap 0.10 and segment size 6;
- allows the separation subprocess 3300 seconds;
- serves Backing Track Studio paths and output recombination, not `/ai-tab` event inference.

Interpretation: the only current source-level route to a direct bass and guitar stem. Bass maps naturally to the bass product request. Guitar is one generic stem and cannot, by itself, decide lead versus rhythm.

Operational blockers:

- the current 3300-second CPU allowance exceeds Astra's 1200-second analyzer ceiling;
- no measured Astra memory, latency or marginal cost exists;
- no downstream improvement against authoritative note events has been measured;
- the exact downloaded `htdemucs_6s` weight identity and its use terms have not been frozen.

Licensing/source evidence:

- `audio-separator` software is MIT, LICENSE blob `47f04d39e8804def1c9afe7ae594eebec92d3e05`; README blob `8b6c73d3168243179b14c0f4980940da9d0e9546` documents CPU/GPU use and multiple model families.
- The upstream Demucs repository is MIT, LICENSE blob `a45a376fb0fcd4a3de06b6c096e62028929a2dcb`; README blob `fe7e77b992b7918eba9491119d313abf5bc3eff1` calls the six-source guitar/piano model experimental and notes guitar is only “okay” in quick testing.
- Software licenses do not automatically establish the license/terms of every separately downloaded model weight. Freeze and review the exact selected weight before a real or commercial path.
- The original Meta Demucs repository says it is no longer maintained. This raises maintenance risk, not an automatic technical rejection.

### Historical three-way “separation” benchmark

Source: `analyzer/modal_instrument_separation_benchmark_v5.py`, blob `b411bb1c19aa079b03a0ecc20e547583a63603e8`.

Despite its filename, V5 is not audio-source separation. It calls a legacy analyzer three times and filters notes into fixed MIDI registers:

- bass: MIDI 28–51
- rhythm: MIDI 52–63
- lead: MIDI 64–76

This can route pitch registers, but musical lead and rhythm parts overlap in pitch. It cannot satisfy Astra's requested-role extraction contract and must not be imported as the three-role solution. The protected analyzer and fixtures remain archived.

### Historical structure estimate

Source: `analyzer/modal_analyzer_v34.py`, blob `7cca1fb920057f2b181045b2f69c8cb21a40b43e`.

It estimates a beat interval from note-onset spacing and derives tempo, but does not establish meter, downbeats or authoritative structure. The idea may inform a clean future development candidate; the archived implementation is not Astra authority and cannot turn inferred note errors into correct structure.

## Capability matrix

| Candidate | Bass from mix | Generic guitar from mix | Lead/rhythm distinction | Notes/chords | Structure | Main blockers |
| --- | --- | --- | --- | --- | --- | --- |
| Whole-mix Basic Pitch | No role isolation | No role isolation | No | Yes, generic AMT | No | mixture interference; same inference for all roles; unpinned runtime |
| `htdemucs_6s` stem + Basic Pitch | Direct bass stem | Direct guitar stem | No | Candidate only | No | 3300s CPU allowance; model identity/terms; unmeasured downstream value |
| V5 register gates | Pitch-range proxy | Pitch-range proxy | No | Inherited legacy events | Inherited legacy | musically invalid role proxy; archived/protected line |
| Astra deterministic backend | Consumes events | Consumes events | Consumes declared role | Constructs tab; no AMT | Consumes structure | upstream audio evidence missing |

## Recommended staged development path

1. Keep the current whole-mix Basic Pitch behavior only as a baseline to beat. Pin it before any comparison.
2. For bass, compare whole-mix Basic Pitch with `htdemucs_6s` bass-stem -> Basic Pitch on authorized development material.
3. For guitar, compare whole mix with generic guitar-stem -> Basic Pitch. Claim only generic guitar transcription until role assignment is independently solved.
4. Treat lead/rhythm overlap as unresolved. On mixtures with two guitars and no qualifying role evidence, Astra should abstain instead of using fixed pitch ranges.
5. Compare complete metric vectors from `BENCHMARK_PLAN_V1.md`; do not select a candidate from separation quality or a single precision score.
6. Measure short, medium and long audio runtime before any product integration. Stop if the method cannot fit the 1200-second/4096-MB service target or existing-cost boundary.

## Next clean implementation step

Create a static, offline capability registry and preflight planner in `astra_backend/` that:

- knows the candidate/version identities without importing or running Python models;
- allows bass and generic-guitar candidates to declare their actual capabilities;
- refuses to claim lead/rhythm separation from a generic guitar stem or register gate;
- returns required evidence, resource/rights blockers and a planned stage graph;
- feeds no customer delivery path.

After that scaffold and tests are saved, an actual model/audio comparison still requires an explicitly identified authorized development population and execution approval under the existing budget boundary.
