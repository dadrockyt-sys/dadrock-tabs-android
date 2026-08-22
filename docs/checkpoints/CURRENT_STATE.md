# CURRENT STATE — V143 contextual-prune / measures 1–16 producer recovery

Updated: 2026-08-21
Branch: `v143-contextual-prune-lobo`
Checkpoint base commit: `071ac6320a372f1f7b25f1593202cd72d43e67b2`
Historical source commit under investigation: `4d735846fbd834cc4c722f2cb48727e4629647f1`

## Objective

Recover and source-prove the deterministic historical pipeline that produced the preserved measures 1–16 reference-free raw/onset carrier caches, without retraining, changing thresholds, modifying production, or relying on professional/reference labels at runtime.

## Closed / solved

- The historical 36-feature reconstruction layer is considered solved and preserved by the prior checkpoint.
- The downstream assembler recovery is preserved at checkpoint base `071ac6320a372f1f7b25f1593202cd72d43e67b2`.
- The remaining deterministic-replay gap is upstream: raw audio -> preserved measures 1–16 raw/onset-spectrum carrier caches.
- Historical/source investigation is GitHub-first. Codespace use has been limited to read-only Git archaeology because GitHub API access has repeatedly hit 403 rate limits.

## Historical files recovered from local Git history

The historical analyzer tree at `4d735846fbd834cc4c722f2cb48727e4629647f1` contains the relevant V143 intro family, including:

- `analyzer/v143_intro_capture_raw_attack_cache.py`
- `analyzer/v143_intro_capture_onset_spectrum_cache.py`
- `analyzer/v143_intro_capture_raw_attack_harmonic_cache.py`
- `analyzer/v143_intro_capture_spectral_pitch_cache.py`
- `analyzer/v143_intro_raw_attack_temporal_diagnostic.py`
- `analyzer/v143_intro_raw_attack_harmonic_rank_diagnostic.py`
- `analyzer/v143_intro_learned_grid_event_selector.py`
- `analyzer/v143_intro_learned_onset_spectral_set_model.py`
- plus the other historical `v143_intro_*` diagnostics / selectors / decoders visible in the historical tree.

## Producer identification

### Raw-attack cache

`analyzer/v143_intro_capture_raw_attack_cache.py` is the actual writer for:

- `intro-raw-attack-cache.json`

The script reads the original audio bytes, calls a Modal worker, and serializes the returned result directly with:

- `CACHE_PATH.write_text(json.dumps(result, indent=2) + "\n")`

The returned object explicitly identifies its scope as:

- `professional-measures-1-16-raw-reference-free-attacks`

and reports:

- `referenceFree: True`
- `professionalReferenceUsedByAnalyzer: False`
- `runtimeLabelsRequired: False`
- `productionModified: False`

### Proven raw-audio -> raw-attack chain

Inside `capture_raw_attack_evidence(source_audio: bytes, suffix: str = ".m4a")` the historical source shows this chain:

1. uploaded source audio bytes are written to a temporary source file;
2. `legacy.inspect_audio_file(...)` inspects source metadata;
3. `legacy.validate_audio_metadata(...)` validates it;
4. `legacy.normalize_audio_file(..., normalized.wav)` creates normalized audio;
5. `estimate_reference_free_timing(normalized)` obtains timing without professional reference data;
6. `build_subdivision_grid(**timing.candidate_adapter_kwargs())` creates the timing grid;
7. `build_deterministic_rhythm_stem_bundle(normalized).validate()` creates deterministic candidate rhythm stems;
8. each candidate stem is processed across `HISTORICAL_WIDE_RECALL_SWEEPS`;
9. detection is performed by:
   `note_events_from_predict(stem, onset_threshold=float(onset_threshold), frame_threshold=float(frame_threshold))`;
10. every detected raw note event is parsed by `parse_note_event(raw)` into:
    `onset, offset, midi, amplitude`;
11. events outside the configured guitar MIDI range are rejected;
12. events are mapped to the nearest subdivision-grid slot and filtered first by the historical wide-grid tolerance, then annotated against the production-grid tolerance;
13. accepted raw events are serialized into `intro-raw-attack-cache.json`.

Confirmed raw-event fields include at least:

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
- nearest-grid / residual / production-grid acceptance metadata

The returned cache also includes timing/grid metadata and counts such as `rawEventCount`, `productionAcceptedEventCount`, sweep/stem counts, tempo, source duration, and grid tolerance values.

### Exact dependency locations recovered

At historical commit `4d735846...`, the raw-attack producer imports its core timing / note-event behavior from:

`analyzer/v143_candidate_timing_adapter.py`

Relevant definitions located by historical grep:

- line ~21: `HISTORICAL_WIDE_RECALL_SWEEPS`
- line ~117: `parse_note_event(...)`
- line ~189: `note_events_from_predict(...)`

These definitions have been located but their complete source bodies / exact sweep values have not yet been captured into this checkpoint. That is the next raw-attack source-proof step.

## Important negative finding

`analyzer/v143_intro_capture_raw_attack_harmonic_cache.py` is downstream, not the missing raw-attack producer. It already references `intro-raw-attack-cache.json` and uses cached onset times to capture candidate-specific harmonic evidence from the source audio. Do not treat it as the original raw-attack cache generator.

Likewise, `v143_intro_raw_attack_temporal_diagnostic.py` and the learned-grid / ranking scripts are consumers/diagnostics of the preserved carrier layer, not the initial raw-audio cache writer.

## Onset-spectrum cache

Historical grep found the direct writer candidate:

- `analyzer/v143_intro_capture_onset_spectrum_cache.py` -> `intro-onset-spectrum-cache.json`

This file has been identified but its full producer body has NOT yet been source-inspected. Do not infer its FFT/window/hop/sample-rate/normalization settings from other scripts until this source is read directly.

A separate historical audio-onset reference script, `analyzer/analyze_gomyway_chorus_35_step0_audio_onset_v1.py`, was previously inspected and uses FFmpeg decode, sample rate 22050, frame size 1024, hop 256, Hann window, `rfft`, magnitude spectra and L1 normalization. These values are reference evidence only and are NOT yet authoritative for `intro-onset-spectrum-cache.json`.

## Preserved evidence / cache layer

A prior evidence snapshot under:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

contains the preserved intro JSON artifacts, including the raw-attack and onset-spectrum caches, with provenance / SHA-256 manifests from the earlier recovery work.

A larger historical Python-source archive under:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

has been proposed so the remaining archaeology can continue GitHub-only and the Codespace can be shut down. As of this checkpoint, do NOT assume that archive has been committed unless it is independently visible on the branch.

## Current blockers / environment status

GitHub REST/core API access is currently intermittently blocked by `403 API rate limit exceeded` for the connected user. GitHub search endpoints have sometimes remained usable while fetch/content endpoints are blocked.

Because of that, the historical source was inspected through the already-open Codespace using only read-only commands such as `git log`, `git grep`, and `git show`. No analyzer execution, training, threshold changes, production edits, or deployments were performed during this archaeology.

## Hard constraints

- Branch work only on `v143-contextual-prune-lobo`.
- Do not modify `main` or production.
- Do not retrain.
- Do not alter historical thresholds merely to reproduce an expected answer.
- Do not use professional/reference labels at runtime.
- Do not execute the analyzer merely to guess missing provenance while source history remains available.
- Codespace should be used only when necessary for read-only historical recovery; move source evidence into GitHub and shut it down as soon as practical to avoid unnecessary Codespace cost.
- Preserve evidence and exact historical behavior before proposing any new implementation.

## Next safe steps

1. Inspect `analyzer/v143_candidate_timing_adapter.py` at `4d735846...`, specifically the exact `HISTORICAL_WIDE_RECALL_SWEEPS`, `parse_note_event`, and `note_events_from_predict` definitions.
2. Inspect the complete historical `analyzer/v143_intro_capture_onset_spectrum_cache.py` source and prove its input path, audio preprocessing, frame/window/hop/FFT/normalization behavior, event/carrier schema, and serialization.
3. Trace any dependencies used by that onset-spectrum producer until the raw-audio -> cache path is source-complete.
4. Prefer committing a read-only historical Python-source snapshot under `analyzer/v143-intro-1-16-evidence/historical-source-4d735846/` with a manifest and SHA-256 list, so future work can proceed through GitHub without keeping Codespace running.
5. Once both raw-attack and onset-spectrum producers are source-proven, update this checkpoint again before any deterministic replay attempt.

## Resume directive

Resume from source archaeology, not from runtime experimentation. The raw-attack cache writer and its high-level producer chain are now identified. Finish the exact `v143_candidate_timing_adapter.py` definitions, then inspect `v143_intro_capture_onset_spectrum_cache.py`. Only after both historical producer paths are fully source-proven should deterministic replay be considered.
