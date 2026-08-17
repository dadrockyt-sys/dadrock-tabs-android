# DadRock Tabs AI-Tab — Rhythm Guitar Pipeline

**Status:** Active production-integration anchor  
**Canonical branch:** `v143-ai-tab-production-integration`  
**Purpose:** Define and track the complete Rhythm Guitar path for `dadrocktabs.com/ai-tab`. When this pipeline is complete and validated, it becomes the reference implementation for the Bass Guitar and Lead Guitar pipelines.

## Canonical end-to-end flow

```text
dadrocktabs.com/ai-tab
  -> app/ai-tab/page.js
  -> private Vercel Blob audio upload
  -> app/api/analyze-audio-tab/route.js
  -> ANALYZER_API_URL
  -> external production compute
      -> audio conversion
      -> instrument separation
      -> Rhythm Guitar stem(s)
      -> generic candidate/timing-grid generation
      -> exact proven carrier feature extraction
      -> V143 feature construction
      -> V143ProductionEngine
      -> notes + techniques + metadata
  -> AI-Tab response
  -> DadRock Tabs preview/PDF renderer
  -> professional Rhythm Guitar PDF
  -> offline comparison against the human-written professional reference
```

## Architecture rules

- GitHub is the source of truth for production code and pipeline documentation.
- Codespaces are for quick inspection, edits, tests, and file creation; completed work is committed and pushed back to GitHub.
- Vercel handles the website/UI/API orchestration layer.
- Heavy audio conversion, separation, and analyzer inference must run on external production compute, not in the Codespace and not inside a constrained Vercel function.
- `V143ProductionEngine` remains the authoritative V143 scoring implementation.
- Production inference must be reference-free. Human/professional reference material is used only for offline validation/grading.
- Frozen training/reference artifacts must not be casually modified.
- Historical Go My Way research `main()` wrappers are evidence/authority, not production request handlers.
- Reuse exact proven feature math and ordering; do not recreate V143 logic from memory.

## Website/UI entry point

Canonical frontend file:

`app/ai-tab/page.js`

Current Rhythm Guitar user path:

1. User uploads supported audio.
2. Audio is uploaded to private Vercel Blob storage.
3. User selects `rhythm` as the transcription type.
4. The page POSTs the uploaded audio reference and song metadata to `/api/analyze-audio-tab`.
5. The returned tab/metadata is passed to the preview/PDF path.

## Vercel API bridge

Canonical route:

`app/api/analyze-audio-tab/route.js`

Responsibilities:

- Validate uploaded audio reference, song, artist, and transcription type.
- Read `ANALYZER_API_URL`, `ANALYZER_API_TOKEN`, and `BLOB_READ_WRITE_TOKEN` from environment configuration.
- Forward the analyzer request to external production compute.
- Return normalized analyzer output to the AI-Tab page.

Expected analyzer response surface includes:

- `generatedTab`
- `tuning`
- `tempo`
- `timeSignature`
- `keySignature`
- `difficulty`
- `techniques`
- `confidence`
- `noteCount`

## Rhythm analyzer target

The Rhythm Guitar production runtime must perform this proven chain:

```text
separated Rhythm Guitar audio
  -> generic candidate events + measure/step timing grid
  -> exact proven carrier feature extraction
  -> candidate rows containing rows[*]["features"]
  -> base carrier matrix
  -> phase features/interactions
  -> V143 multi-family feature construction
  -> exact V143 148-feature schema
  -> V143ProductionEngine.score_matrix(...)
  -> production decisions
  -> notes/techniques/metadata
```

The runtime adapter must assert that its final feature ordering exactly matches `engine.feature_names` before scoring.

## V143 authority

Primary scorer:

`analyzer/v143_production_engine.py`

Verification/replay path:

`analyzer/replay_v143_production_engine.py`

Training/feature-engineering authority:

`analyzer/develop_gomyway_v143_final_multifamily_training_only.py`

Important resolved import detail:

```python
import confirm_gomyway_3676_patch_rhythm24_v133_conjunction_guard_reserved_9mod16_over1024_v134 as v134
```

The historical alias chain remains useful for provenance:

```text
v134
  -> v124
  -> v1
  -> recurrent
  -> ridge
  -> patch
  -> richer
  -> onset
  -> prof
  -> recall
```

However, the production integration no longer needs to keep descending this chain searching for a single magical `recall` request handler. The direct V143 carrier boundary has now been verified.

## Verified V143 carrier boundary

### Direct carrier source consumed by V124/V143

`analyzer/confirm_gomyway_3676_patch_rhythm24_v122_reserved_5mod16_over1024_v124.py` defines:

```python
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
```

Therefore the direct base-carrier artifact feeding the V124/V143 path is:

`public/gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json`

Its `candidateSlots` rows provide the carrier substrate ultimately consumed as `rows[*]["features"]` by V143.

This is a more precise production boundary than treating `recall.CANDIDATE_PATH` as the direct V143 carrier source. `recall.CANDIDATE_PATH` remains part of the historical candidate/event and protection/validation lineage, but V124 directly reads the spectro-temporal patch-stability carrier artifact.

### Exact carrier producer identified

The artifact is produced by:

`analyzer/profile_gomyway_3676_onset_slot_spectro_temporal_patch_stability_v1.py`

Verified reusable feature functions in that file include:

- `band_log_power(...)`
- `stem_patch(...)`
- `pair_patch(...)`

`stem_patch(...)` measures a temporal/spectral patch around a candidate time across five frequency bands and multiple offsets, including rise/decay/post-slope/burst summaries.

`pair_patch(...)` combines two stem measurements into deterministic carrier features using paired mean/agreement values.

### Important production limitation of the historical wrapper

The historical producer `main()` is **not** a generic uploaded-audio production callable. It is a Go My Way research/diagnostic wrapper that:

- reads a fixed historical source artifact;
- reads the protected historical candidate event set;
- builds its timing grid from that protected candidate;
- loads two historical winner/alternate stem sources;
- attaches labels for downstream diagnostic evaluation;
- writes a fixed Go My Way output/manifest.

Production must **not** run that research wrapper against user uploads and must **not** bring its labels/professional-reference evaluation path into runtime inference.

The correct integration strategy is to preserve/reuse the exact proven feature math and schema while replacing the hard-coded research orchestration with a clean runtime adapter for arbitrary uploaded Rhythm Guitar audio.

## Production adapter boundary

The production Rhythm adapter should have two clean upstream responsibilities before V143:

### 1. Candidate/timing generation

From arbitrary separated Rhythm Guitar audio, produce reference-free candidate events with enough timing information to map each candidate to the measure/step grid expected by the proven carrier/V143 path.

This stage must not depend on protected Go My Way candidate files or professional labels.

### 2. Exact carrier extraction

For each candidate time:

1. Obtain the required production stem inputs using the validated separation strategy.
2. Apply the exact proven spectro-temporal patch feature math.
3. Apply the exact paired carrier-combination math.
4. Produce `candidateSlots` rows containing the authoritative `features` dictionary/schema.
5. Feed those rows into the exact V143 feature-building path.
6. Assert the final 148 feature names/order against `V143ProductionEngine.feature_names`.
7. Score only through `V143ProductionEngine.score_matrix(...)`.

Do not prematurely collapse the historical two-stem feature contract to a single stem. If production uses a different stem arrangement, equivalence must be demonstrated by validation rather than assumed.

## Immediate next milestone

Stop broad historical analyzer archaeology.

The next milestone is now narrowly defined:

1. Put the authoritative V143 scorer/replay source files on this GitHub branch if they are still only present in the Codespace.
2. Identify the **smallest reusable, reference-free candidate-event/timing-grid implementation** already present in source.
3. If no clean generic callable exists after a targeted inspection, create a new production adapter around the proven pure functions rather than executing historical research `main()` wrappers.
4. Prove on an arbitrary separated Rhythm Guitar input that the adapter produces the exact carrier feature schema expected by V143.
5. Prove the final constructed matrix matches the authoritative 148-feature schema before any Modal/API deployment work.

## PDF/output target

The final Rhythm Guitar path must produce a professional DadRock Tabs PDF using the existing generation/preview/PDF infrastructure.

Relevant existing routes include:

- `app/api/generate-tab/route.js`
- `app/api/generate-tab-preview/route.js`
- `app/api/generate-tab-pdf/route.js`
- `app/api/pdf-preview/route.js`

The production analyzer output must be authoritative before PDF quality is graded.

## Completion gate for Rhythm Guitar

Rhythm Guitar is considered complete only when a real user-style upload can successfully perform:

1. Upload audio from `dadrocktabs.com/ai-tab`.
2. Select Rhythm Guitar.
3. Convert/download the uploaded source on production compute.
4. Separate or isolate the Rhythm Guitar stem inputs using the chosen production separation path.
5. Generate reference-free candidate events and timing/grid mapping from the uploaded performance.
6. Build the exact carrier schema expected by V143 using the proven feature math.
7. Build the exact 148-feature V143 schema in authoritative order.
8. Score only through `V143ProductionEngine`.
9. Produce selected notes and techniques without professional-reference leakage.
10. Return valid AI-Tab response metadata through `/api/analyze-audio-tab`.
11. Render the polished DadRock Tabs PDF.
12. Grade the rendered result offline against the supplied professional human-written Rhythm Guitar reference.
13. Pass the agreed professional-quality acceptance threshold.

## Reuse rule for Bass and Lead Guitar

Do not independently redesign the website/API/deployment pipeline for Bass or Lead Guitar.

When Rhythm Guitar reaches the completion gate, this file becomes the reference specification. Bass and Lead should reuse the same proven infrastructure wherever possible:

```text
shared AI-Tab UI
  -> shared private upload
  -> shared Vercel API bridge
  -> shared external-compute request contract
  -> instrument-specific separation/analyzer implementation
  -> shared normalized response contract
  -> shared preview/PDF infrastructure
```

Only the instrument-specific analyzer/separation/feature/model stages should diverge unless testing proves another layer must change.

Planned derivative documents after Rhythm is complete:

- `docs/ai-tab-bass-guitar-pipeline.md`
- `docs/ai-tab-lead-guitar-pipeline.md`

Each derivative document should explicitly reference this Rhythm Guitar file as the baseline architecture and list only the intentional instrument-specific differences.

## Working discipline

For future work on this branch:

1. Inspect GitHub first.
2. Use Codespace only when execution or quick editing is required.
3. Commit/push meaningful source changes promptly so GitHub remains authoritative.
4. Update this file whenever a major pipeline stage is proven, replaced, or completed.
5. Do not mark Rhythm Guitar complete until the full user-upload-to-professional-PDF test passes end to end.
