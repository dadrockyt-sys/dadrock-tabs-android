# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce genuinely professional guitar tablature, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved capture / baseline
- Authorized historical run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`.
- Baseline: eligible `984`; retained attacks `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Independent guitar evidence
- Exact approved source `public/gomywayfullaitest.m4a` verified SHA; no Modal needed.
- Robust electric TabCNN checkpoint SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`; exact-audio evidence `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`.
- Use only as independent positive consensus, never blind replacement.

## Attack V3 — strongest attack shadow
- Baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **`891` retained**.
- Durable validation `debug/v143-contextual-prune/attack-shadow-v3-replay-validation.json`, commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`, SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Exact: selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented/unplayable/invalid pitch.
- `freezeReady=false`: 166 rescued attacks lack recomputed downstream technique/sustain.

## Primary V4 — strongest primary correction
- 34 lower-primary corrections accepted only where exact electric model pairwise favors new lower primary over old upper primary; no new scalar threshold.
- Durable validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`, SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- Baseline after V4 remains selected/rendered `970/967`, drops `3`.

## Combined Content V5 — CURRENT STRONGEST MUSICAL CONTENT SHADOW
- Attack V3 + validated Primary V4; all 34 V4 corrections touch baseline attacks only.
- Durable validation `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`, SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Exact: retained attacks `891`; selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented pitch, invalid/unplayable primary, unobserved attack/pitch, relocation, new inference, or new threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- V5 remains **not freeze-ready** because technique/sustain has not been recomputed for rescued attacks.

## V5 voicing feasibility
- Five drops fully explained: 3 physically assignable but over resolver 28-semitone span (m19/s6 `[52,86]`, m40/s14 `[40,78]`, m63/s14 `[47,78]`); 2 unavoidable low-E same-string collisions (m113/s13 `[41,43]`, m113/s14 `[43,44]`).
- Do not relax the resolver merely to force them through.

## Professional PDF renderer — substantial upgrade complete
- `lib/createV143RhythmPdf.js` upgraded at commit `08ee3bcc1cec3428641741a8281206aa4218cb8d` without changing analyzer/pitch/timing evidence.
- New engraving: clean sheet-style header, 3 measures/system, TAB mark/barlines/measure numbers, rehearsal marks, rhythm stems + beat-local beaming, graphical slides/hammer/pull/bends/vibrato/sustain, technique lanes, compact continuation headers, professional footer/page numbering, and removal of full debug timing grid.
- Synthetic fixture `scripts/v143-professional-pdf-fixture.mjs`; successful visual run `32820654412`, bot commit `a5655d56df411cd3011c42807dc9119019b9858d`. Visual inspection: no clipping/broken glyphs; major commercial-quality improvement. Synthetic PM/let-ring ranges can still be visually consolidated if those techniques become present in final content.

## Real preserved 113-measure PDF render — PASSED
- Real candidate schema inspection run `32821063375`, job `97719080566`, bot commit `dc2c2ad...`: pinned product exposes a direct structured `events` array of **967** baseline render events with string/fret/measure/step/sustain/technique fields; no note reconstruction or guessing required.
- Real render script `scripts/v143-render-real-candidate-pdf.mjs` commit `4b3b958d181ea37fa26bb1e4a083b061e8700ae5`; summary-field fix `e4e7b62e8d600d08d8a8c3ca3a690cab4ddc8c55`.
- Workflow `.github/workflows/v143-render-real-candidate-pdf.yml` commit `abdebb07d1d1600efc8cdeb5cb1a89dfc09e53fb`.
- **Passing real render run `32821330353`, job `97719895086`.** Protected runtime guard passed; materializer reported Modal/L4 false and professional reference false.
- Exact render: source/projected events `967/967`; unique measures `113`; unique onsets `725`; max notes/populated measure `18`; max chord size `5`; multi-note onsets `209`; section count `8`; tempo `129.19921875`; E Standard; 4/4.
- PDF: **6 Letter pages**, 1,738,077 bytes, SHA256 `3b47dfa93b8ad05b7de94c6d51f65acc9fa2d9a05701e1daecb3cdf78c0c768f`.
- Durable render commit `2470225d9cb726e35a07459e29783997a3447699`: `debug/v143-contextual-prune/real-candidate-professional-pdf/` contains PDF, first/middle/last inspection PNGs, report, pdfinfo, and hashes. Artifact `9553226034`.
- Visual inspection of first/middle/last pages: no clipping, dense chords and two-digit frets readable, clean headers/rehearsal marks/barlines, good commercial-tab appearance. Last page has extra lower whitespace but is acceptable. Internal title `V143 Approved Rhythm Reference` is inspection-only and **not final customer-facing metadata**.
- Critical limitation: this successful real PDF renders the **baseline 967-event stream**, not strongest V5 `1209` rendered-note content. It proves the engraving renderer can carry a real 113-measure song professionally; it is not the final musical PDF.

## V5 render-stream materializer + professional shadow PDF — PASSED
- CPU-only render materializer `analyzer/materialize_v143_combined_content_shadow_v5_render_stream.py` added at commit `a6505ba21e30af1b0e985b945de71ae3698bf08f`.
- It recomputes fresh V5, binds durable Attack V3 and Combined V5 SHA256 values, preserves baseline performance metadata only where exact `(measure, step, midi)` identity survives, remaps surviving legato targets, and emits neutral metadata for rescued content rather than inventing technique/sustain.
- V5 PDF render script `scripts/v143-render-v5-shadow-pdf.mjs` commit `10916a1989478f1747c30fcc4d395c6d1522cb32`; workflow `.github/workflows/v143-render-v5-shadow-professional-pdf.yml` commit `a1b0f01b8f3adfee2fa63bda31ef39c5ba2a84bf`.
- Successful workflow persisted evidence at bot commit `2fcfd22f729e14dcd0bf5469f5f0af0a4a44b646` in `debug/v143-contextual-prune/v5-professional-pdf/`.
- Exact materialization: rendered events `1209`; retained onsets `891`; measures `113`; baseline events `967`; rescued rendered events `242`; baseline metadata preserved on `933`; neutral baseline events `34`; neutral rescued events `242`; technique events `21`; remapped legato links `20`; dropped legato links `1`; Primary V4 correction attacks `34`; validation passed.
- Exact render: `1209` events, `891` onsets, `113` measures, max notes/populated measure `22`, max chord size `5`, multi-note onsets `272`, technique types hammer-on/pull-off/slide-down/slide-up, section count `7`.
- V5 PDF: **6 Letter pages**, 1,748,093 bytes, SHA256 `bbd67f9054a3a112f4b24e5e22b3b3fc31b125e36ebdb97c36d693ace0ffa99b`; render-stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- This PDF is explicitly `freezeReady=false`, `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- Visual inspection of the **V5** first/middle/last persisted snapshots from workflow run `32821861294`, artifact `9553423573`, passed: no clipping, broken glyphs, unreadable dense systems, or obvious fret/text collisions at the higher 1209-event density; dense chords and two-digit frets remain legible. The final page retains acceptable lower whitespace.
- The remaining blocker is downstream technique/sustain recomputation for the 166 rescued attacks; rescued events are intentionally neutral in this inspection render.

## Downstream technique/sustain source investigation — ACTIVE
- Modern V143 runtime wrapper imports `external_processing.v143_audio`, `external_processing.v143_models`, and `external_processing.v143_product`, but those implementation modules are not committed/searchable on this branch. Repository/commit search has not found a modern source copy of `build_reference_free_rhythm_product`; therefore **no replacement thresholds/rules will be invented**.
- Historical Java commit `ac46281f8112cd16a959d9c37f8936270ad4f716` contains old sustain-engine work, but it is treated as historical context only, not V143 source truth.
- Added evidence-only inspector `analyzer/inspect_v143_baseline_downstream_metadata.py` at commit `037e1c717ea1db34907984bda1013ef7f9de8302`. It reads the immutable pinned product only, validates exact `967/725/113`, summarizes all existing performance metadata distributions/signatures and non-neutral contexts, and scans non-event product fields for source/evidence/diagnostic paths. It performs **zero inference or musical mutation**.
- Added guarded CPU-only workflow `.github/workflows/v143-inspect-baseline-downstream-metadata.yml` at commit `dfc2706d02e2ef192a424dbb039d5a505d2b1eb1`. It re-verifies the protected runtime blob, rematerializes the immutable paid capture from pinned commit `c1451df...`, runs only the inspector, persists compact JSON evidence, and invokes no Modal/professional reference.
- Inspection workflow result is pending; next step is to use its exact evidence to determine whether a source-faithful replay is possible without guessing.

## Current integrity
- Branch head before this checkpoint update: `dfc2706d02e2ef192a424dbb039d5a505d2b1eb1`.
- Protected runtime guard passed in prior real baseline and V5 shadow render workflows; new metadata-inspection workflow also contains an explicit protected-runtime guard.
- No Production/main change; no professional scorer/reference; no new Modal/L4 usage.

## Next exact actions
1. Read the guarded baseline downstream-metadata inspection result and identify any exact candidate-side source/evidence/diagnostic fields supporting modern technique/sustain replay.
2. If exact source support exists, build a CPU-only, source-only downstream **technique/sustain replay** for all 166 rescued attacks using that evidence only; no professional reference and no new Modal/L4. If it does not exist, do not invent thresholds—trace the V143 runtime packaging/provenance further.
3. Validate exact rescued-attack coverage and prove no technique/duration invention beyond what source/runtime evidence supports; preserve timing/tempo.
4. Re-materialize V5 with recomputed downstream metadata, re-render the professional PDF, and enforce `1209/891/113` content identity plus renderer fidelity.
5. Only after downstream completeness is proven consider the closed professional score gate; do not tune against the professional reference.
6. No Modal/L4 without fresh explicit authorization.
7. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
