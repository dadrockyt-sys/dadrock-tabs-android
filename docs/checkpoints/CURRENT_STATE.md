# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-score musical improvement must remain general/reference-free and requires a fresh audio run before rescoring.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

## CPU gate 1 — GREEN

Canonical `debug/v143-contextual-prune/rhythm-preholdout-static-preflight.json` is schema 7, `passed:true` from source commit `f84e4b1504fb648799341fbf68255664fb95dc0b` / Actions run `32622951910`.

Key proof: 400 events, 100 measures, frozen/PDF SHA `6475a7d68071a8810890982e1c06c0d39f99e85d646680706233ceed5a58b37e`, fidelity 1.0, polished full+preview PDF rendered, product/real-audio/runtime safety contracts green, reference unopened, Production unchanged.
Canonical promotion commit: `1f995f876e52f091c404002e340b062e373cbe05`.

## CPU gate 2 — GREEN

`debug/v143-contextual-prune/rhythm-professional-holdout-self-test.json` is schema 6, `passed:true`, source commit `1c64d91fff0fb13f4982c212267c22f2951061f7`.

It proves runtime isolation, complete synthetic scorer reference contract, final wrapper positive path >=0.99, PDF fidelity 1.0, zero critical mismatches, partial-reference hard failure, leakage hard failure, PDF mismatch hard failure, static product→professional-PDF glue, branding, event/hash identity. Real professional reference was not opened and Production was not modified.

Both required CPU gates are established green.

## Fresh real-audio pre-holdout — GREEN AND LOCKED

Exactly one intentional GPU trigger was made by commit:
`1df4a6c55123ae1c4c4b37530f306d43da69bbdd` — `Run locked fresh Rhythm real-audio preholdout`.

Fresh Actions run: `32623173615`.
Compact proof: `debug/v143-contextual-prune/rhythm-professional-preholdout-real-audio.json` schema 2, `passed:true`.

Fresh approved-audio proof:
- source fixture: `public/gomywayfullaitest.m4a`
- source SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- source bytes: 3,478,611
- `referenceFree:true`
- `professionalReferenceUsed:false`
- `referenceRuntimeInputUsed:false`
- `runtimeLabelsRequired:false`
- `v143RuntimeSafetyVerified:true`
- 358 frozen events
- 112 unique measures
- frozen event SHA = PDF event SHA = `f5e18ed4469b10ccfbae0a7f993d5e32a8e9552867aa50fb0d3fe2d90a82d06a`
- PDF-event fidelity exactly 1.0
- full PDF: 1,686,160 bytes / 4 pages
- preview PDF: 1,678,667 bytes / 4 pages
- renderer projection exact
- reference unopened throughout freeze/render
- live endpoint unchanged
- Production unchanged
- Production promotion unauthorized
- no failed checks

Workflow artifact:
- artifact ID `9489025699`
- name `rhythm-professional-preholdout-real-audio`
- GitHub artifact digest / downloaded ZIP SHA256 `e0c5f94d09f79430f4aa03c156a3d3fc32431bf79abc541ab65dde3d815e4f2c`
- full PDF SHA256 `986c78f0b35f0d3c90a0be86cee8842b16dccc928c412dedb6a14ffcc879b2c6`
- preview PDF SHA256 `052ed9f0a843581cb38a50caeb52fe8989f044b8a4fc619fe07d2bf9d7d8b915`

Permanent lock:
`debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json`
commit `61424df2afecf99d1179cdc328915f795f26662c` — `Lock fresh Rhythm preholdout artifact`.

The downloaded artifact was independently inspected. Fresh full/preview PDFs have clean DadRock branding, readable professional TAB systems, no observed clipping/overlap on inspected pages, and the preview lock/watermark behaves as intended. Musical correctness is intentionally not inferred from appearance.

## Professional scorer phase — COMPLETE CLEAN SOURCE RECOVERED

The fresh reference-free freeze/PDF prerequisite was green before any professional source recovery.

The user identified `main/public/Professionalexample.jpg`. It was recovered scorer-side from immutable commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577` without modifying `main` or Production.

Recovery workflow:
- `.github/workflows/rhythm-professional-reference-recovery.yml`
- workflow creation commit `d07b3a714133703e77b233ec1dd9a978c4b2cfb3`
- Actions run `32624327056`
- report `debug/v143-contextual-prune/rhythm-professional-reference-recovery.json`, `passed:true`
- scorer-only artifact ID `9489261810`
- artifact digest `c99d243520f274adfa9e817ec0b143617d9c95f50eb7817551049f3727e3207a`

Immutable professional source proof:
- path `public/Professionalexample.jpg` at immutable commit above
- SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- 979,815 bytes
- JPEG RGB, 2160×3840
- exact 3×3 / nine-panel stitched professional source
- visible title `Are You Gonna Go My Way`
- visible artist `Lenny Kravitz`
- revision `2026-07-12`
- `Overdriven Guitar`
- `Craig Ross | 1953 Gibson Les Paul Goldtop | Rhythm Guitar`
- visual panel review covers the complete song from measure 1 through the final ending system after measure 112; the existing source-derived measure map identifies the complete range as measures 1–113 and nine source panels.
- the clean Library screenshot `1000116180.jpg` independently matches the recovered Chorus source around measures 33–35.

`validation/rhythm_holdout/reference/reference-inventory.json` is now updated to `completeReferenceAvailable:true`. `finalScoringAuthorized` remains false only because a fresh scorer-only event-level transcription of this immutable source is still required. Historical development references remain excluded and cannot be promoted as the final holdout.

## Immediate next steps

1. Freshly transcribe the immutable nine-panel professional-human source scorer-side into `reference.schema.json` format under the ignored reference area; do not use historical development event labels as final ground truth.
2. Validate all measures 1–113, 16-step placement, string/fret/MIDI consistency, durations/techniques only where source evidence is explicit, and complete-source provenance/hash.
3. Set `completeReferenceTranscriptionReady:true` and authorize final scoring only after that transcription passes completeness checks.
4. Score the already-locked fresh frozen stream from run `32623173615`; do **not** rerun analyzer merely to score.
5. Run completeness → isolated scorer → final wrapper. Require professional score >=0.99, zero critical mismatches, fidelity 1.0.
6. If score misses, change only general/reference-free musical logic; then a brand-new fresh real-audio run/freeze is mandatory before rescore.
7. Once the real professional gate passes, verify DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
