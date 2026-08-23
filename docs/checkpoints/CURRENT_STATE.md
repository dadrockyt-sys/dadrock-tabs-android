# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-23
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Absolute rules

Work only on `v143-contextual-prune-lobo`. Do not modify/merge `main`, deploy/alter live V143 Modal, promote Production, make payments, redeem tokens, send customer emails, weaken thresholds, or call Bass/Lead professional structured output early.

Required Rhythm path:
`user audio → Rhythm → reference-free Jimmy PAIge → authenticated events → exact professional preview/full PDF → post-freeze professional-human holdout score`

Preview/full must use the same authenticated/frozen stream. Browser/PDF may not invent placement. Professional human reference is scorer-only and may never be read/trained/tuned/selected by runtime. Any post-reference musical improvement must remain general/reference-free and requires a brand-new fresh real-audio run/freeze before any professional rescore.

**Save this checkpoint frequently.**

## Completion gate

Rhythm is complete only with professional score >=0.99, zero critical mismatches, and PDF-event fidelity exactly 1.0. Then create `Final Rhythm Pipeline`. Bass remains paused until then; Lead remains after Bass.

## Previously established green gates

CPU static preflight is schema 7 / green. CPU professional-holdout self-test is schema 6 / green. Runtime isolation, professional PDF routing, branding, reference anti-leakage, wrapper hard failures, and exact PDF-event fidelity were established before professional source recovery.

Fresh approved-audio pre-holdout run `32623173615` was green and locked before any professional source recovery:
- approved fixture `public/gomywayfullaitest.m4a`
- source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- 358 frozen Rhythm attack events
- 112 unique measures, measures through 113
- full/preview PDF event fidelity exactly 1.0
- runtime safety: `referenceFree:true`, `professionalReferenceUsed:false`, `referenceRuntimeInputUsed:false`, `runtimeLabelsRequired:false`, `v143RuntimeSafetyVerified:true`
- live endpoint unchanged, Production unchanged, promotion unauthorized
- workflow artifact ID `9489025699`, name `rhythm-professional-preholdout-real-audio`
- permanent artifact lock: `debug/v143-contextual-prune/rhythm-professional-preholdout-artifact-lock.json`

That frozen run is now a historical structural baseline only because musical mapping code has subsequently changed.

## Professional scorer source recovery

The fresh reference-free prerequisite was green before source recovery.

Immutable professional source was recovered scorer-side only from `main/public/Professionalexample.jpg` at commit `e0f91e74c815b9ecdf0a72fae6d1523414b34577` without modifying `main` or Production.

Recovery proof:
- Actions run `32624327056`
- `debug/v143-contextual-prune/rhythm-professional-reference-recovery.json`, passed
- scorer-only artifact ID `9489261810`
- source SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`
- JPEG RGB 2160×3840, 979,815 bytes
- exact 3×3 / nine-panel complete professional source
- source visually spans the complete song, measures 1–113
- clean Library screenshot `1000116180.jpg` independently matches the recovered Chorus source around measures 33–35

`validation/rhythm_holdout/reference/reference-inventory.json` records complete source availability. A fresh scorer-side event transcription has not yet been persisted and no valid final professional score has been declared.

The professional source remains scorer-only. Do not use source notes, labels, string/fret choices, or historical development labels to tune runtime musical logic.

## Current musical blocker found from fresh reference-free output

The fresh reference-free artifact from run `32623173615` was inspected without professional-source input.

The V143 detector already carries many simultaneous `pitchHypotheses` per selected rhythmic attack (358 selected attacks from the frozen selection), but the old `analyzer/v143_rhythm_guitar_note_mapper.py` emitted only one dominant MIDI per selected attack and marked `jointChordVoicingResolved:false`. The renderer and `v143_rhythm_output_adapter.py` already support multiple same-onset notes on unique strings. Therefore polyphony was being discarded upstream in note mapping/assembly rather than by the PDF renderer.

Reference-free exploratory evidence from the locked analyzer output showed a median of roughly two strong conservative simultaneous hypotheses per selected attack after source-consensus/amplitude/grid/duration screening. No professional reference was used to derive those screening observations.

## Reference-free polyphonic mapper — IMPLEMENTED, CPU PROOF GREEN

General musical correction committed on this branch:

1. Commit `cc56e64589fcc9bae3032b55133e8b73ba5fd956` — `Add reference-free polyphonic Rhythm note mapping`
   - rewrites `analyzer/v143_rhythm_guitar_note_mapper.py`
   - keeps frozen V143 attack selection/timing immutable
   - always retains the frozen dominant MIDI
   - admits secondary notes only from the same attack's existing reference-free `pitchHypotheses`
   - requires repeated/source-consistent evidence above detector floor, onset-grid agreement, and minimum duration
   - suppresses weak +/-1-semitone estimator ambiguity while allowing genuinely strong close dyads
   - limits output to six physical strings and a conservative guitar pitch span
   - resolves a deterministic non-crossing joint standard-tuning guitar voicing with unique strings
   - does not invent notes outside source hypotheses
   - does not use professional reference or runtime labels
   - secondary recovered chord tones do not duplicate attack-level bend/slide/mute/etc. technique attributes

2. Commit `c235a1535138f86ea44c4bbcb8334500c45cba7b` — `Harden Rhythm assembly for polyphonic attacks`
   - distinguishes frozen selected attack count from rendered note count
   - permits one selected attack to emit multiple guitar notes
   - requires every selected attack to remain represented
   - requires frozen dominant MIDI to remain present
   - requires every rendered MIDI to exist in that attack's frozen pitch hypotheses
   - requires unique `(measure, step, stringIndex)` occupancy
   - preserves frozen timing, score/rank/selection and pitch-hypothesis evidence
   - fails closed on unresolved/reference-dependent mappings

3. Commit `e6820f0782eba3d79854b9a140851ffc1d99afb0` — `Add CPU proof for reference-free Rhythm polyphony`
   - synthetic checks cover single-note stability, strong chord expansion, unique strings, weak near-unison suppression, six-string cap, technique non-duplication, attack-count vs note-count semantics, and assembly safety flags.

4. Commit `f015715a291ff3f9c2a9da9f633f1b5bef63352a` — `Add CPU gate for reference-free Rhythm polyphony`
   - exact-SHA, CPU-only workflow; no professional source, no GPU, no Production modification.

Persisted green proof:
- `debug/v143-contextual-prune/rhythm-polyphony-cpu-proof.json`
- run `32631065756`, attempt 1
- source commit `f015715a291ff3f9c2a9da9f633f1b5bef63352a`
- proof commit `b769a5c834ce03f47d3e4019ac7cf51a7bf04493`
- `passed:true`, `verifyOutcome:"success"`
- `referenceFree:true`
- `professionalReferenceUsed:false`
- `referenceRuntimeInputUsed:false`
- `runtimeLabelsRequired:false`
- `productionModified:false`
- `productionPromotionAuthorized:false`

Local reference-free replay of the mapper against the locked 358-event analyzer artifact emitted 1,020 guitar-note events across the same 358 attack locations with no duplicate `(measure, step, string)` occupancy and every emitted MIDI traceable to an original attack hypothesis. This is exploratory implementation validation only, not a professional score and not yet a fresh freeze.

## Product/runtime compatibility checked

Existing downstream product code is already compatible with attack count != rendered-note count:
- `analyzer/v143_rhythm_output_adapter.py` groups multiple same-onset notes on unique strings and reports `noteCount=len(events)` while `selectedCount` can remain the rhythmic attack count.
- `lib/jimmyPaigeAnalysisPayload.js` consumes authenticated render events and `noteCount`; it does not require `selectedCount == noteCount`.
- `app/api/analyze-audio-tab/route.js` forwards analyzer output and does not impose that equality.
- `lib/createV143RhythmPdf.js` and `lib/v143RenderContract.js` already render same-onset chords and reject duplicate `(measure, step, stringIndex)` occupancy rather than rejecting polyphony.

## Safe fresh GPU execution path confirmed — live endpoint will not be altered

`.github/workflows/rhythm-professional-preholdout-real-audio.yml` runs:
`python -m modal run analyzer/v143_ai_tab_product_canary_modal.py::run`

`analyzer/v143_ai_tab_product_canary_modal.py` creates an isolated Modal app (`dadrock-v143-ai-tab-product-canary`) and reuses the live Rhythm **image definition**, not the deployed live endpoint. It explicitly reports `liveEndpointDeployedOrModified:false` and `productionModified:false`.

`analyzer/v143_modal_live_endpoint.py` defines `V143_MODULES`, which explicitly packages both `v143_rhythm_guitar_note_mapper` and `v143_rhythm_event_assembly` plus the rest of the V143 stack into `rhythm_image` from the checked-out branch source. Therefore a fresh `modal run` can exercise the new branch mapper/assembly in an isolated ephemeral canary without deploying or modifying live V143 Modal.

Important: the real-audio workflow only push-triggers when its own workflow file changes, so mapper commits did **not** accidentally trigger GPU work. A deliberate workflow-file trigger is required for exactly one fresh candidate run.

## CPU orchestration note

The older persisted schema-7 static preflight remains green, but `debug/v143-contextual-prune/rhythm-preholdout-static-v2-run.json` still has not appeared after the earlier validation-path push. Do not interpret that missing V2 marker as a mapper failure: the dedicated mapper/assembly CPU proof above is independently green. The current self-test workflow is still the older mutable-checkout/cross-static-write version; avoid touching validation paths again until that orchestration is stabilized or until after the isolated real-audio candidate is safely locked.

## Immediate next steps

1. Preserve the green polyphony CPU proof and do not tune from the professional source.
2. Intentionally trigger exactly one fresh isolated approved-audio product-canary run by a controlled edit to `.github/workflows/rhythm-professional-preholdout-real-audio.yml`; do not deploy live V143 Modal.
3. Require the new run to preserve runtime safety, positive event count, complete measure coverage, polished preview/full PDF, exact event/hash equality, PDF-event fidelity 1.0, reference sealed, live endpoint unchanged, and Production unchanged.
4. Inspect the fresh artifact before any professional scoring. Confirm the new output actually exercised `noteMapping.version:2` / polyphonic expansion and that attack/note semantics remain valid end-to-end.
5. Lock that fresh artifact as the new candidate freeze.
6. Only then may scorer-side professional transcription/scoring proceed. Require score >=0.99 and zero critical mismatches.
7. If score misses, change only general/reference-free musical logic and repeat the mandatory fresh-audio freeze before any rescore.
8. Once the real professional gate passes, verify DadRock `/ai-tab` user end-to-end and create `Final Rhythm Pipeline`.
