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

The source-to-artifact structural chain has now also been traced through the preserved 36-feature grid selector. The preserved raw/onset artifacts are checksum-pinned, the surviving historical whole-onset carrier reproduces the same schema/constants/windows, and the exact historical 36-feature assembler has been re-read directly from the archived source.

No analyzer execution, retraining, threshold changes, production edits, or deployments were performed during this archaeology.

## Closed / solved

- Historical 36-feature reconstruction layer: solved/preserved by the earlier checkpoint and re-confirmed directly from archived historical source.
- Downstream assembler recovery: preserved by the earlier checkpoint lineage.
- Historical 1–16 raw-attack cache writer: identified and source-inspected.
- Historical 1–16 onset-spectrum cache writer: identified and source-inspected.
- Exact Basic Pitch wide-recall sweep table: recovered.
- Exact Basic Pitch candidate call parameters: recovered.
- Deterministic two-view guitar stem contract: recovered.
- Onset-spectrum CQT settings, windows, normalization, schema, and serialization: recovered.
- Preserved raw/onset cache identities: SHA-256 pinned by the copied Codespace manifest.
- Onset-spectrum row -> ordered 36-feature grid vector: source-proven from `v143_intro_learned_grid_event_selector.py`.
- Frozen correlation-safe 36-feature model linkage: preserved model confirms 100 ms window, L2 10.0, threshold 0.27, and neutralized columns 19/26/33.

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

## Source/artifact structural equivalence

The preserved Codespace snapshot has an explicit provenance record identifying source HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1` and stating that the files were copied unchanged with no retraining, threshold/model changes, or production edits.

The snapshot SHA-256 manifest pins the two upstream artifacts as:

- `intro-raw-attack-cache.json`: `698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`
- `intro-onset-spectrum-cache.json`: `eceb7468560ca8a967cf5d2de581cbab5932b9843941488e443dcfbf2b4eb1e7`

The surviving `v143_contextual_prune_reference_free_carrier.py` independently expresses the same four-sweep raw-event capture, 30 ms pitch clustering, 30 ms physical-onset grouping, two-view CQT substrate, exact three spectral windows, and 16-step section grid. Its carrier summary also marks the path reference-free and production-unmodified.

This closes structural/schema/parameter equivalence between the source-proven producer family and the preserved carrier lineage. It does **not** yet claim a byte-identical fresh regeneration of the two large caches; that remains a future deterministic replay gate.

## Exact onset-spectrum -> 36-feature mapping

The authoritative surviving assembler is:

`analyzer/v143_intro_learned_grid_event_selector.py`

Archived source blob:

`f26e622f8277d68f3649191879789f87acd4f77e`

For each `(measure, step)` grid location, `_grid_feature(...)` uses a 100 ms nearby-onset window in the frozen model configuration.

When a nearby onset row exists, feature indices 0..12 are exactly:

0. constant `1.0`
1. nearest signed onset residual / window seconds
2. nearest absolute onset residual / window seconds
3. second-nearest absolute residual / window seconds; defaults to `1.0` normalized when only one row exists
4. `min(nearby_row_count / 8, 2)`
5. nearest `candidateCount / 49`
6. nearest `sourceClusterCount / 16`
7. nearest `stemSupportMax / 2`
8. nearest `sweepSupportMax / 4`
9. `min(nearest.detectionCountSum / 32, 2)`
10. max nearby `stemSupportMax / 2`
11. max nearby `sweepSupportMax / 4`
12. `min(sum(nearby detectionCountSum) / 96, 2)`

If there is no nearby onset row, indices 0..33 are zero.

Indices 13..33 are three seven-value spectral summaries in this exact order:

`attackMax`, then `earlyMean`, then `sustainMean`.

For each window, `_spectral_summary(...)` clamps each view nonnegative, computes `mean_view = 0.5 * (viewA + viewB)`, and emits:

1. mean of `mean_view`
2. standard deviation of `mean_view`
3. largest value (`top1`)
4. `top1 - top2`
5. L2 norm of nonnegative view A
6. L2 norm of nonnegative view B
7. cosine similarity between the two nonnegative views (`viewCorrelation`)

Thus the three view-correlation columns are exactly 19, 26 and 33.

Indices 34 and 35 are always:

- `sin(2π * step / 16)`
- `cos(2π * step / 16)`

The preserved learned grid-event selector model contains 36 feature means and stds generated by this assembler. The preserved correlation-safe model keeps the same 36-column layout, uses `windowMs: 100`, `l2: 10.0`, `threshold: 0.27`, and explicitly neutralizes columns `[19, 26, 33]` named:

- `attackMax:viewCorrelation`
- `earlyMean:viewCorrelation`
- `sustainMean:viewCorrelation`

The corresponding frozen weights are zero, while the other feature statistics remain linked to the surviving 36-feature construction. This confirms the exact preserved carrier -> ordered feature vector -> frozen base-selector model handoff without inventing a replacement assembler.

## Important negative finding

`v143_intro_capture_raw_attack_harmonic_cache.py` is downstream, not the original raw-attack producer. It already consumes `intro-raw-attack-cache.json` and uses cached onset times to capture additional harmonic evidence.

Likewise the raw-attack temporal/ranking diagnostics and learned-grid selector are downstream consumers/evaluators, not the initial audio-to-cache writer.

## Dependency audit status

The first-party Python dependencies directly observed in the raw-attack/onset/carrier chain are present in the archived historical source inventory, including the Modal live endpoint, candidate timing adapter, reference-free timing module, deterministic stem provider/separator, seeded separator, `modal_analyzer`, onset diagnostic, learned spectral model and learned grid selector.

One final replay-readiness question remains before execution: prove the frozen external runtime/model asset contract used by `rhythm_image` / the separator stack is reproducible from the repository/environment configuration. The historical source archive proves the Python graph, but source presence alone is not enough to promise byte-identical third-party model outputs.

Therefore no deterministic runtime replay is authorized yet.

## Preserved evidence

Existing preserved cache/evidence snapshot:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

Historical Python source archive now pushed to this branch:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

The archive includes a manifest / checksum material created during preservation, so the remaining work can proceed GitHub-only.

## Environment status

The Codespace is no longer required for current source archaeology and can remain stopped/deleted to avoid further compute charges.

GitHub REST access previously hit intermittent 403 rate limits, but the archived source is currently readable through the GitHub connector.

## Hard constraints

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main` or production.
- Do not retrain.
- Do not alter historical thresholds to force an expected result.
- Do not use professional/reference labels at runtime.
- Preserve historical source behavior before replaying or changing implementation.
- Do not reopen Codespace unless a specific source/evidence gap cannot be resolved from the archived GitHub material.

## Next safe steps

1. Inspect `v143_modal_live_endpoint.py` and the deterministic separator/image definitions to inventory exact external package/model/runtime assets required for byte-identical replay.
2. Confirm those runtime assets are pinned or otherwise reproducible without reopening the Codespace.
3. If the dependency contract closes, prepare a deterministic replay plan that writes only research comparison artifacts and never overwrites the preserved caches.
4. Before any runtime replay, update this checkpoint with the exact proposed command, inputs, outputs, expected hashes/invariants and abort conditions.
5. Only then consider executing a replay; do not retrain, retune, alter thresholds, or modify production.

## Resume directive

Continue GitHub-only. Upstream producer source, preserved artifact identities, structural carrier equivalence and the exact onset-spectrum -> 36-feature assembler/model handoff are now source-proven. The remaining pre-replay task is to prove the frozen external dependency/model-asset contract used by the historical Modal separator stack. Do not execute the analyzer until that dependency audit is closed and checkpointed.