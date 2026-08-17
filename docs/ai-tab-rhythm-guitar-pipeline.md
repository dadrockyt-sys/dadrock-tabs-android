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
      -> Rhythm Guitar stem
      -> proven carrier/candidate feature producer
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
  -> proven upstream carrier/candidate producer
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

Training/feature-engineering authority currently being traced:

`analyzer/develop_gomyway_v143_final_multifamily_training_only.py`

Important resolved import detail:

```python
import confirm_gomyway_3676_patch_rhythm24_v133_conjunction_guard_reserved_9mod16_over1024_v134 as v134
```

The historical alias chain leading toward the upstream candidate producer is:

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

The next analyzer milestone is to identify and reuse the exact `recall`-side callable that creates the candidate carrier rows/features from arbitrary separated Rhythm Guitar audio.

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
4. Separate or isolate the Rhythm Guitar stem using the chosen production separation path.
5. Build the exact carrier schema expected by V143.
6. Build the exact 148-feature V143 schema in authoritative order.
7. Score only through `V143ProductionEngine`.
8. Produce selected notes and techniques without professional-reference leakage.
9. Return valid AI-Tab response metadata through `/api/analyze-audio-tab`.
10. Render the polished DadRock Tabs PDF.
11. Grade the rendered result offline against the supplied professional human-written Rhythm Guitar reference.
12. Pass the agreed professional-quality acceptance threshold.

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
