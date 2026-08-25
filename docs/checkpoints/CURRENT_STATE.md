# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; professional musical accuracy first, professional PDF second.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No tuning/selection from it.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved capture / baseline
- Authorized historical run `32805316807`; trigger SHA `74b0f815ff3f66f325220975c410621503de440f`; pinned capture commit `c1451df43cc1162edb38aa3f3300b7af4d9b527`.
- Baseline: eligible `984`; retained attacks `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Independent guitar evidence
- Exact approved source `public/gomywayfullaitest.m4a` verified SHA; no Modal needed.
- Robust electric TabCNN checkpoint SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`; exact-audio evidence `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`.
- Use only as independent positive consensus, never blind replacement.

## Attack V3 / Primary V4 / Combined Content V5
- Attack V3: baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **`891` retained**; selected/rendered `1214/1209`; drops `5`; measures `113/113`; validation commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`, SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Primary V4: 34 lower-primary corrections accepted only where exact electric model pairwise favors new lower primary; validation commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`, SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- Combined V5 = Attack V3 + Primary V4; validation `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`, SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: retained attacks `891`; selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented/unplayable/invalid pitch, relocation, new inference, or new threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- **V5 remains `freezeReady=false` only because downstream technique/sustain has not yet been recomputed for 166 rescued attacks.**

## V5 voicing feasibility
- Five drops fully explained and should not drive resolver relaxation: m19/s6 `[52,86]`, m40/s14 `[40,78]`, m63/s14 `[47,78]` exceed 28-semitone resolver span; m113/s13 `[41,43]` and m113/s14 `[43,44]` are unavoidable low-E same-string collisions.

## Professional renderer / V5 PDF
- `lib/createV143RhythmPdf.js` upgraded commit `08ee3bcc1cec3428641741a8281206aa4218cb8d`.
- V5 render materializer `analyzer/materialize_v143_combined_content_shadow_v5_render_stream.py`, commit `a6505ba21e30af1b0e985b945de71ae3698bf08f`.
- Successful V5 PDF workflow run `32821861294`, artifact `9553423573`, persisted commit `2fcfd22f729e14dcd0bf5469f5f0af0a4a44b646`.
- Exact render: `1209` events / `891` onsets / `113` measures; baseline metadata preserved `933`; neutral baseline `34`; neutral rescued `242`; technique events `21`; remapped legato `20`; dropped legato `1`.
- PDF: 6 Letter pages, 1,748,093 bytes, SHA256 `bbd67f9054a3a112f4b24e5e22b3b3fc31b125e36ebdb97c36d693ace0ffa99b`; stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- First/middle/last visual inspection passed at 1209-event density: no clipping, broken glyphs, unreadable systems, or obvious collisions. PDF remains inspection-only / not freeze-ready because rescued performance metadata is neutral.

## Downstream evidence inspection — PASSED
- Evidence-only inspector `analyzer/inspect_v143_baseline_downstream_metadata.py`: initial `037e1c717ea1db34907984bda1013ef7f9de8302`, expanded nested inspection `fc7f2fbd7824dea13f9885cdf355701819efa77c`.
- Artifact-only guarded workflow `.github/workflows/v143-inspect-baseline-downstream-metadata.yml` current commit `07782c3339dd8072221a5c0fbb1f583204dc1bfb`.
- Successful expanded run `32839631383`, artifact `9559978873`; protected runtime and pinned CPU materialization passed; no Modal/pro reference.
- Baseline nested fields: all 967 events contain `duration`, `rhythmSustain`, `rhythmTechniques`; 669 contain `rhythmSustainShadow`; 25 contain `legatoEvidence` plus legato target/continuation fields.
- `sustainDiagnostics`: annotated 669/967, event/pitch/attack timing unchanged, tie/let-ring not inferred, reference-free, runtime labels not required.
- `semanticGuard`: primary events 725, secondary 242; stripped audio technique labels 18, invalid primary legato 8, secondary legato 21; pitch/string-fret/attack timing/event count unchanged.
- `precisionReplayEvidence`: 984 eligible attacks / 10,585 candidate pitches / 970 selected / 725 primary; `sourceViewEvidenceReady=true`, `attackPolicyReplayReady=true`, `precisionStrengthRecomputeReady=true`.
- Sustain distribution from exact baseline: durationSteps 1:679, 2:144, 3:64, 4:31, 5:9, 6:8, 7:12, 8:5, 9:4, 10:4, 11:2, 12:1, 15:1, 16:1, 21:1, 26:1; tiers short 679 / medium 144 / long 144.
- Existing techniques: 942 empty; 25 one-technique events = hammer-on 4, pull-off 4, slide-down 7, slide-up 10; all source `reference-free-audio-legato-evidence`.

## Exact downstream implementation source — FOUND (major milestone)
- The original authorized-run wrapper `analyzer/v143_repaired_timing_precision_candidate_product_modal.py` at trigger SHA `74b0f815ff3f66f325220975c410621503de440f` explicitly imports the exact downstream modules. We do **not** need to reverse-engineer thresholds.
- Exact modules fetched from the historical trigger SHA (and key ones still exist on current branch):
  - `analyzer/v143_rhythm_sustain_consensus_shadow.py`
  - `analyzer/v143_precision_sustain_promotion.py`
  - `analyzer/v143_rhythm_legato_evidence.py`
  - `analyzer/v143_rhythm_semantic_primary_note_guard.py`
  - `analyzer/v143_rhythm_bend_consensus.py`
  - `analyzer/v143_rhythm_bend_evidence.py`
- Exact sustain config in source: sample rate 44100, frame 4096, hop 512, harmonic count 4, sigma 38 cents, relative threshold 0.18, tail floor multiplier 2.4, absolute floor 1e-10, minimum view duration 0.04 s. Consensus requires both source views and max view-duration disagreement `<= max(0.06, 0.75 * stepSeconds)`; accepted duration is min(view durations), hard-ended before next same-string attack.
- `v143_precision_sustain_promotion.py` promotes only when shadow duration exceeds detector duration and strict two-view agreement holds; attack/pitch are preserved.
- `v143_rhythm_legato_evidence.py` is the exact reference-free cross-separated pitch-path/reattack implementation; bend and semantic guard source are also preserved.
- **Do not invent or tune any replacement thresholds now that exact source is known.**

## Remaining blocker: exact separated source views
- Exact downstream code needs the two separated guitar source views used by the authorized run: `direct-demucs6s-guitar.wav` and `bsroformer-demucs6s-guitar.wav`.
- Original wrapper creates them via `analyzer/v143_deterministic_separator.py` and `analyzer/v143_seeded_separator.py`.
- Authorized trigger `74b0f815...` and current branch both prove the exact Demucs musical parameters are `shifts=1`, `overlap=0.10`, `segment=6`; there is no separator-flag drift between those revisions.
- Authorized run `32805316807`, job `97674196169` logs show the direct Demucs stage ran CPU-only; BS-RoFormer is the CUDA/GPU stage. Therefore the direct source view can be reproduced without Modal/GPU, while the BS-RoFormer/cascade view remains the external-compute blocker unless preserved bytes are recovered.
- Current seeded BS-RoFormer separator requires CUDA; normal GitHub CPU cannot reproduce that view exactly. No new Modal/GPU use is authorized.
- Authorized run artifact `9548666053` was inspected and contains only manifest/product/guard/report/lock JSON, **not stems**.
- Historical artifact API lookups for runs `32503444051` and `32806344264` currently return 404, so those specific run artifacts cannot presently be relied upon as stem storage.
- Therefore the preferred path remains locating any preserved workflow artifact containing the exact BS-RoFormer guitar view (or byte-identical source arrays); direct Demucs repeatability can be tested CPU-only if useful.

## Current integrity
- Branch head before the 2026-08-25 separator-provenance checkpoint update: `d6cecb794b93a3bbb6883948789f9dbcdbf3ecd0`.
- Protected runtime remains exact.
- No Production/main change; no professional scorer/reference; no new Modal/L4 usage.

## Next exact actions
1. Search historical V143 workflow runs/artifacts for preserved `bsroformer-demucs6s-guitar.wav`, `bsroformer-instrumental.wav`, or byte-identical analysis-view arrays; prioritize runs that introduced/tested deterministic/seeded separator repeatability.
2. Fully map exact legato/bend/semantic-guard function signatures and dependencies from trigger SHA `74b0...` so the replay wrapper uses source unchanged.
3. If exact BS-RoFormer source view is recovered, build a CPU-only V5 downstream replay using preserved BS-RoFormer view + exact direct Demucs reconstruction + exact existing algorithms; validate every rescued attack and preserve `1209/891/113`, timing and tempo.
4. Re-render V5 PDF with recomputed downstream metadata and enforce renderer fidelity.
5. Only after downstream completeness is proven consider the closed professional score gate; do not tune against the professional reference.
6. No Modal/L4 without fresh explicit authorization.
7. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
