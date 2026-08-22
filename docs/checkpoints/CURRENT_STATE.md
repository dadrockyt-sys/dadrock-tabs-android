# CURRENT STATE — V143 contextual-prune / measures 1–16 producer recovery

Updated: 2026-08-21
Branch: `v143-contextual-prune-lobo`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`
Prior recovery checkpoint: `412208c946737e9902ab78a19db5fa48c439fdd7`

## Objective

Recover and source-prove the deterministic historical pipeline that produced the preserved measures 1–16 reference-free raw/onset carrier caches, without retraining, changing thresholds, modifying production, or relying on professional/reference labels at runtime.

## Current status

The upstream producer gap is now substantially source-proven. The historical Python source has been archived onto this research branch under:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

The archive was rebased on top of the prior checkpoint and pushed successfully, allowing the Codespace to be shut down. GitHub-side source reads now work against the archived files.

No analyzer execution, retraining, threshold changes, production edits, or deployments were performed during this archaeology.

## Closed / solved

- Historical 36-feature reconstruction layer: solved/preserved by the earlier checkpoint.
- Downstream assembler recovery: preserved by the earlier checkpoint lineage.
- Historical 1–16 raw-attack cache writer: identified and source-inspected.
- Historical 1–16 onset-spectrum cache writer: identified and source-inspected.
- Exact Basic Pitch wide-recall sweep table: recovered.
- Exact Basic Pitch candidate call parameters: recovered.
- Deterministic two-view guitar stem contract: recovered.
- Onset-spectrum CQT settings, windows, normalization, schema, and serialization: recovered.

## Raw-attack cache producer

Historical writer:

`analyzer/v143_intro_capture_raw_attack_cache.py`

Output:

`public/training/v143-musical-reconstruction-calibration/intro-raw-attack-cache.json`

The local entrypoint reads the original audio bytes, sends them to `capture_raw_attack_evidence(...)`, and serializes the returned object directly with:

`CACHE_PATH.write_text(json.dumps(result, indent=2) + "\n")`

The returned cache explicitly reports:

- `scope: professional-measures-1-16-raw-reference-free-attacks`
- `referenceFree: True`
- `professionalReferenceUsedByAnalyzer: False`
- `runtimeLabelsRequired: False`
- `productionModified: False`

### Source-proven raw-audio -> raw-attack chain

1. source audio bytes -> temporary uploaded audio file;
2. `legacy.inspect_audio_file(...)`;
3. `legacy.validate_audio_metadata(...)`;
4. `legacy.normalize_audio_file(..., normalized.wav)`;
5. `estimate_reference_free_timing(normalized)`;
6. `build_subdivision_grid(**timing.candidate_adapter_kwargs())`;
7. `build_deterministic_rhythm_stem_bundle(normalized).validate()`;
8. each deterministic guitar view is processed across all historical wide-recall sweeps;
9. Basic Pitch detection via `note_events_from_predict(...)`;
10. each detection parsed by `parse_note_event(...)` into onset, offset, MIDI, amplitude;
11. guitar-range filtering;
12. wide-grid filtering at 0.30 s;
13. measures 1–16 filtering;
14. production-grid acceptance annotation at 0.10 s;
15. direct JSON serialization to `intro-raw-attack-cache.json`.

### Exact historical Basic Pitch sweep table

Recovered from `v143_candidate_timing_adapter.py`:

```python
HISTORICAL_WIDE_RECALL_SWEEPS = (
    ("o030_f020", 0.30, 0.20),
    ("o025_f015", 0.25, 0.15),
    ("o020_f012", 0.20, 0.12),
    ("o015_f010", 0.15, 0.10),
)
```

`PRODUCTION_SWEEPS` uses only the widest/highest-recall final tuple:

`("o015_f010", 0.15, 0.10)`

### Exact Basic Pitch call contract

`note_events_from_predict(...)` loads `basic_pitch.inference.predict` and calls it with:

- caller-supplied onset threshold;
- caller-supplied frame threshold;
- minimum note length: 20 ms;
- minimum frequency: 80 Hz;
- maximum frequency: 1400 Hz.

The adapter guitar MIDI range is 40..88.

`parse_note_event(...)` accepts the historical dict/list event shapes and returns:

`start_f, end_f, pitch_i, amp_f`

or `None` for invalid/non-finite events.

### Raw event schema

Each stored event includes:

- `eventId`
- `stemIndex`
- `stemName`
- `sweepName`
- `onsetThreshold`
- `frameThreshold`
- `rawIndex`
- `midi`
- `amplitude`
- `onsetTime`
- `offsetTime`
- `duration`
- `nearestMeasure`
- `nearestStep`
- `nearestGlobalStep`
- `nearestGridTime`
- `signedGridResidualSeconds`
- `absoluteGridResidualSeconds`
- `withinProductionGridTolerance`

The cache also carries beat/grid metadata and raw/accepted/sweep/stem counts.

## Deterministic guitar views

`v143_rhythm_deterministic_stem_provider.py` delegates to the deterministic separator and returns exactly two independent guitar views:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental -> Demucs6s Guitar.

`v143_deterministic_separator.py` enforces:

- deterministic seed: 143;
- Demucs shifts: 1;
- Demucs overlap: 0.10;
- Demucs segment size: 6.

`v143_seeded_separator.py` confirms the frozen graph and output contract:

- direct output: `direct-demucs6s-guitar.wav`;
- cascade output: `bsroformer-demucs6s-guitar.wav`;
- RoFormer single stem: Instrumental;
- RoFormer batch size: 1;
- soundfile enabled;
- reference-free metadata.

## Reference-free timing

`v143_reference_free_timing.py` is now available in the archived source. Confirmed constants include:

- analysis sample rate: 22050 Hz;
- STFT window: 1024 samples;
- STFT hop: 256 samples;
- Hann window;
- tempo search: 55–210 BPM;
- 4/4 bar model.

It derives timing from normalized full-mix audio without labels/professional reference data and exposes beat times plus first-beat/bar-phase metadata to the candidate adapter.

## Raw-attack clustering used by onset-spectrum producer

`v143_intro_raw_attack_temporal_diagnostic._cluster_events(...)` is reference-free for clustering. It groups raw events by `(measure, midi)` and merges detections within 30 ms onset proximity. Each resulting cluster carries median onset time plus independent stem/sweep support and amplitude statistics.

The professional reference path present elsewhere in the diagnostic file is used for offline diagnostic evaluation, not by `_cluster_events(...)` itself and is not passed to the onset-spectrum remote capture worker.

## Onset-spectrum cache producer

Historical writer:

`analyzer/v143_intro_capture_onset_spectrum_cache.py`

Output:

`public/training/v143-musical-reconstruction-calibration/intro-onset-spectrum-cache.json`

This producer consumes:

- original source audio bytes;
- reference-free clusters derived from `intro-raw-attack-cache.json`;
- the same deterministic two-view guitar stem bundle.

It first converts same-measure candidate-pitch clusters into physical onset groups. Candidate clusters within 30 ms of the group's first attack are collapsed into one physical onset group while preserving the candidate MIDI set.

### Exact onset-spectrum analysis settings

Recovered constants:

- target sample rate: 22050 Hz;
- hop length: 128 samples;
- bins per octave: 36;
- CQT MIDI range: 28..112;
- guitar MIDI range: 40..88;
- onset grouping tolerance: 30 ms;
- exactly two deterministic guitar views required.

Each view is loaded, converted to mono when needed, cropped through last onset + 0.40 s, resampled to 22050 Hz if necessary, then transformed by `librosa.cqt(...)` with:

- `hop_length=128`;
- `fmin=midi_to_hz(28)`;
- `n_bins=(112-28+1) * 3`;
- `bins_per_octave=36`;
- `filter_scale=0.75`.

The stored spectral substrate is:

`log(abs(CQT) + 1e-9)`

### Exact spectral windows

For each physical onset, each view stores three semitone vectors:

- `attackMax`: onset - 0.020 s through onset + 0.045 s, max reducer;
- `earlyMean`: onset + 0.020 s through onset + 0.095 s, mean reducer;
- `sustainMean`: onset + 0.070 s through onset + 0.180 s, mean reducer.

For each MIDI 28..112, the producer uses the center CQT bin plus/minus one bin (three bins total when available). The resulting 85-value semitone vector is normalized by subtracting that window's median spectral floor, then rounded to 6 decimals.

Each onset row carries the reference-free onset-group metadata plus:

- `viewA.attackMax`
- `viewA.earlyMean`
- `viewA.sustainMean`
- `viewB.attackMax`
- `viewB.earlyMean`
- `viewB.sustainMean`

The returned cache reports:

- `cacheVersion: 1`
- `scope: reference-free-physical-onset-whole-spectrum-cache`
- sample-rate/hop/CQT metadata;
- `candidateStemCount`;
- `onsetGroupCount`;
- `rows`;
- `referenceFree: True`;
- `professionalReferenceUsedByAnalyzer: False`;
- `runtimeLabelsRequired: False`;
- `productionModified: False`.

The local entrypoint serializes the remote result directly with:

`OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n")`

## Important negative finding

`v143_intro_capture_raw_attack_harmonic_cache.py` is downstream, not the original raw-attack producer. It already consumes `intro-raw-attack-cache.json` and uses cached onset times to capture additional harmonic evidence.

Likewise the raw-attack temporal/ranking diagnostics and learned-grid selector are downstream consumers/evaluators, not the initial audio-to-cache writer.

## Preserved evidence

Existing preserved cache/evidence snapshot:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

Historical Python source archive now pushed to this branch:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

The archive includes a manifest / checksum material created during preservation, so the remaining work can proceed GitHub-only.

## Environment status

The Codespace is no longer required for current source archaeology and can be stopped/deleted to avoid further compute charges.

GitHub REST access previously hit intermittent 403 rate limits, but after the historical source archive was pushed the archived source became readable through the GitHub connector.

## Hard constraints

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main` or production.
- Do not retrain.
- Do not alter historical thresholds to force an expected result.
- Do not use professional/reference labels at runtime.
- Preserve historical source behavior before replaying or changing implementation.
- Do not reopen Codespace unless a specific source/evidence gap cannot be resolved from the archived GitHub material.

## Next safe steps

1. Compare the source-proven producer schema/parameters against the preserved `intro-raw-attack-cache.json` and `intro-onset-spectrum-cache.json` manifests/artifacts to verify structural compatibility and provenance.
2. Trace the remaining downstream carrier assembly from onset-spectrum rows into the already-recovered 36-feature substrate, confirming exact field mapping and ordering against preserved artifacts.
3. Confirm no unarchived dependency is required for deterministic replay.
4. Only after source/artifact equivalence is established, plan a deterministic replay test; do not retrain or change thresholds.
5. Update this checkpoint before any runtime replay.

## Resume directive

Continue GitHub-only. The historical raw-attack and onset-spectrum cache producers are now source-proven, including exact Basic Pitch sweeps, deterministic stem contract, reference-free timing constants, CQT settings, spectral windows, normalization, and JSON serialization. Next prove source-to-preserved-artifact equivalence and the exact carrier-to-36-feature mapping before considering runtime replay.
