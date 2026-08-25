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

## Preserved baseline / V5 content
- Authorized historical run `32805316807`; trigger SHA `74b0f815ff3f66f325220975c410621503de440f`; pinned capture commit `c1451df43cc1162edb38aa3f3300b7af4d9b527`.
- Baseline: eligible `984`; retained attacks `725`; selected pitches `970`; rendered events `967`; voicing drops `3`; measures `1-113`; candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.
- Exact approved source `public/gomywayfullaitest.m4a`; robust electric TabCNN checkpoint SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`; evidence `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`.
- Attack V3: baseline `725` + exception-band `123` + electric-consensus subfloor `43` = **`891` retained**; selected/rendered `1214/1209`; drops `5`; measures `113/113`; validation commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`.
- Primary V4: 34 lower-primary corrections accepted only where exact electric model pairwise favors new lower primary; validation commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`.
- Combined V5 = Attack V3 + Primary V4; validation `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`, SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- V5 exact: retained attacks `891`; selected/rendered `1214/1209`; drops `5`; measures `113/113`; no invented/unplayable/invalid pitch, relocation, new inference, or new threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- V5 remains `freezeReady=false` only because downstream technique/sustain has not yet been recomputed for 166 rescued attacks.

## V5 renderer / PDF
- Renderer `lib/createV143RhythmPdf.js` upgrade commit `08ee3bcc1cec3428641741a8281206aa4218cb8d`; V5 render materializer commit `a6505ba21e30af1b0e985b945de71ae3698bf08f`.
- Successful V5 PDF workflow run `32821861294`, artifact `9553423573`, persisted commit `2fcfd22f729e14dcd0bf5469f5f0af0a4a44b646`.
- Exact render: `1209` events / `891` onsets / `113` measures; baseline metadata preserved `933`; neutral baseline `34`; neutral rescued `242`; technique events `21`; remapped legato `20`; dropped legato `1`.
- PDF: 6 Letter pages, 1,748,093 bytes, SHA256 `bbd67f9054a3a112f4b24e5e22b3b3fc31b125e36ebdb97c36d693ace0ffa99b`; stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Visual inspection passed for first/middle/last pages, but PDF is not freeze-ready because rescued performance metadata is still neutral.

## Downstream evidence / exact replay source
- Evidence-only inspector commits `037e1c717ea1db34907984bda1013ef7f9de8302` and `fc7f2fbd7824dea13f9885cdf355701819efa77c`; successful expanded run `32839631383`, artifact `9559978873`.
- Baseline nested metadata: all 967 events have `duration`, `rhythmSustain`, `rhythmTechniques`; 669 have `rhythmSustainShadow`; 25 have legato evidence/target/continuation fields.
- Existing techniques: 942 empty; 25 one-technique = hammer-on 4, pull-off 4, slide-down 7, slide-up 10; all source `reference-free-audio-legato-evidence`.
- Original authorized-run wrapper `analyzer/v143_repaired_timing_precision_candidate_product_modal.py` at trigger SHA `74b0f815...` explicitly provides the exact downstream call order; no threshold reconstruction is allowed.
- Exact replay order: bends consensus -> legato enrichment -> semantic guard -> rebuild assembly -> direct/cascade pitch-energy views -> sustain shadow -> sustain promotion.
- Replay-critical modules are byte-identical between trigger and current branch:
  - `v143_rhythm_bend_consensus.py` `7434e0e2ea8849942fa53d61a0efcc022638c2a2`
  - `v143_rhythm_bend_evidence.py` `2f5a9e6d8feb90bad26f16de1ca59507f55e9ca3`
  - `v143_rhythm_legato_evidence.py` `69991ecab59438f18321a42ed27fd9a7aa2c4390`
  - `v143_rhythm_semantic_primary_note_guard.py` `d233b1982599c807248529744127da832d1eddbc`
  - `v143_rhythm_sustain_consensus_shadow.py` `7bc16d01fd688394f22fd925c78544628fcb4b51`
  - `v143_precision_sustain_promotion.py` `7542d726159795c42a3c54c17dd2f965bff2e327`
  - helper `v143_rhythm_sustain_technique_enricher.py` `bbfb577d8528a9ddfebbb7fd448062c0274fb1c7`
- Exact sustain constants: pre-onset 0.12 s, guard 0.03 s, attack 0.10 s, sustain offset 0.04 s, threshold fraction 0.18, max inactive gap 0.10 s, max sustain 3.0 s, same-string guard 0.01 s, 4 subdivisions/beat; consensus is conservative minimum across required views.
- Sustain promotion rewrites `rhythmSustain` for every event from `rhythmSustainShadow` (one-step default when no shadow); do not substitute the earlier mistaken “only if longer” interpretation.

## Exact separated source-view blocker — updated archaeology
- Exact downstream replay needs `direct-demucs6s-guitar.wav` + `bsroformer-demucs6s-guitar.wav` from the approved source.
- Authorized run `32805316807` logs prove direct Demucs ran CPU-only; BS-RoFormer/cascade requires CUDA/GPU. No new GPU/Modal is authorized.
- Authorized run artifact `9548666053` contains manifest/product/guard/report/lock JSON only, not stems. Historical artifacts for runs `32503444051` and `32806344264` are unavailable (404).
- Aug 21 SHA `42daa2df...` packaging/modal-smoke runs retain zero artifacts.
- Aug 24 determinism artifacts from `f086412...`, `d2db253...`, `b1520a8...`, `c8f18da...`, `7713f13...` are log-only; early versions failed cross-worker exactness. The successful `7713f13...` Modal-smoke retained no artifact.

### Important final Aug 24 determinism result
- Latest seeded-separator history commit is `0b3d73bb5f68fee0f76e4fb2827c1f982ea117eb` (`Disable oneDNN in baseline Demucs research child`); there are no later commits to `analyzer/v143_seeded_separator.py` on this branch.
- Its dual-band run is `32692406659`; run conclusion is `failure` only because the broader historical replay gate still failed, **not because separator repeatability failed**.
- Retained artifact `9508202377` (`v143-dual-band-cross-container-behavior-log`) is live through 2026-08-31 and contains only `dual-band-cross-container-behavior.log`, no stems.
- The log uses the exact approved source SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Across **three independent L4 workers**, separator output is byte-identical at the PCM level:
  - `directStemPcmExactAcrossWorkers=true`
  - `cascadeStemPcmExactAcrossWorkers=true`
- Exact deterministic output identities from all three workers:
  - normalized input SHA256 `ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`
  - direct WAV file SHA256 `0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`
  - direct PCM SHA256 `2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`
  - cascade WAV file SHA256 `546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41`
  - cascade PCM SHA256 `75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba`
  - both stems: 44,100 Hz, 9,324,544 frames, stereo.
- The log confirms the cascade path: normalized source -> BS-RoFormer instrumental `input-normalized_(Instrumental)_model_bs_roformer_ep_317_sdr_12.wav` -> Demucs guitar -> `bsroformer-demucs6s-guitar.wav`.
- Although separator PCM is now proven deterministic on the approved full source, `carrierSemanticExactAcrossWorkers=false`; downstream decision exactness across workers is true, and historical exact replay count is still 0. Do not confuse current deterministic separator output with proof that it equals the older authorized-run stem bytes.
- Paired Modal-smoke run `32692406651` failed and retains zero artifacts.
- Repository code search finds neither final direct/cascade file hash nor `bsroformer-demucs6s-guitar.wav` as preserved content; exact source-view bytes are still not recovered.

## Current integrity
- Protected runtime remains exact.
- No Production/main change; no professional scorer/reference; no new Modal/L4 usage in this continuation.
- Historical artifacts were only downloaded/inspected; no historical workflow was rerun.
- Exact downstream implementation remains available; the only replay blocker is recovering/proving the required source-view bytes.

## Next exact actions
1. Search all remaining Aug 24–25 V143 workflow artifacts/manual runs/caches/checkpoints for preserved final direct/cascade bytes or byte-identical derived pitch-energy arrays, using the final hashes above as identifiers.
2. Inspect workflow definitions/history to determine whether any successful/manual run uploaded stems under a different artifact name or persisted them outside normal Actions artifacts.
3. If exact authorized source views are recovered/proven, build CPU-only V5 downstream replay with exact downstream modules/order; preserve `1209/891/113`, timing and tempo.
4. Re-render V5 PDF with recomputed downstream metadata and enforce renderer fidelity.
5. Only after downstream completeness is proven consider the closed professional score gate; do not tune against the professional reference.
6. No Modal/L4 without fresh explicit authorization.
7. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
