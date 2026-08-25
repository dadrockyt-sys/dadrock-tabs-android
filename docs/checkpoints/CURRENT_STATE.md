# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce a genuinely professional guitar-tab PDF, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities never rerun/rescore: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved paid capture — CPU replay source of truth
- Successful authorized run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one Modal command consumed, automatic retry disabled.
- Counts: eligible attacks `984`; retained `725`; pruned `259`; replay pitch hypotheses `10585`; selected pitches `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Durable manifest `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer `analyzer/materialize_v143_precision_fixture.py`.

## Attack state
- Legacy precision: ratio >=0.70 retain; 0.60-0.70 required composite local max; <0.60 prune; positive requires attack>0 and body>-0.25.
- Attack shadow V2: added `148` to baseline -> `873`; its below-0.60 local-peak component rescued `25`, but exact electric consensus supports only `5/25` of those and independently supports `38` previously-unrescued positive subfloor attacks.
- **Attack shadow V3 is now the strongest validated reference-free attack shadow:** preserve baseline `725` + all existing exception-band `123` + electric-consensus subfloor `43` -> `891` retained attacks.
- Relative to V2, V3 removes `20` unsupported subfloor-local rescues and adds `38` electric-supported nonlocal rescues: net `+18` attacks.
- V3 replay yields selected pitches `1214`, rendered pitches `1209`, voicing drops `5`; rescued component contributes selected `244`, rendered `242`, drops `2`.
- V3 leaves `93` pruned attacks: `87` remaining positive and `6` nonpositive.
- Newly rescued attacks still lack the original producer's full downstream two-stem bend/legato/sustain evidence, so V3 is **not freeze-ready**.

## Exact approved audio is now locally recoverable without Modal
- Repository contains exact approved audio at `public/gomywayfullaitest.m4a`.
- Research-only CPU workflow `.github/workflows/v143-research-approved-audio-fetch.yml` verifies SHA before upload.
- Run `32815950324` succeeded; artifact `9551396214`; local research copy was verified byte-exact SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- This removes the previous blocker that specialized source models could only be tested on a non-approved re-encoding.

## Specialized guitar evidence
### Acoustic GuitarSet HCQT+Mel model
- MIT project `ErenReyhanlioglu/Guitar-Transcription`; fold1 checkpoint SHA256 `2572b3fe58429668ec9aeaee56bf40af265726a6c3652151b176b21da2bde953`, Git blob `82094eecad83603b331b1bfbce0f0310f8942df8`.
- Exact-approved grid-only CPU probe completed on all `984` V143 attacks.
- Baseline retained: active `425/725`, discrete model-tab/candidate overlap `144/725` (`19.9%`), median max candidate multipitch probability `0.2911`.
- V3 primary direction: new lower probability higher `19/43`, old upper higher `24/43`; therefore this acoustic-domain model does **not** independently support V3 and is not used as a primary consensus gate.

### Robust electric-guitar TabCNN — strongest independent source model
- DAFx 2024 `robust-guitar-tabs/code`; repository license `CC0-1.0`; checkpoint published with Zenodo record `11406378` (TabCNN + GuitarProFX).
- Checkpoint MD5 `ce168b2cd426f81a2a78499214e40605`; SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`.
- Research workflow run `32815631220` successfully acquired the public checkpoint; artifact `9551275181`; no Modal/L4.
- Exact model contract reproduced: 22050 Hz, hop 512, CQT 192 bins / 24 bins-octave / C1, -80..0 dB -> 0..1, 9-frame context, six strings, frets 0-19 + silence.
- Exact-approved full-grid CPU probe:
  - baseline retained `725`: model active `577` (`79.6%`), discrete model-tab/candidate overlap `348` (`48.0%`), median max candidate probability `0.391995`;
  - V2 exception-band `123`: active `96`, overlap `60` (`48.8%`), median `0.386752` — essentially baseline-like independent support;
  - V2 subfloor local peaks `25`: active `15`, overlap `5` (`20.0%`), median `0.093627`;
  - remaining positive subfloor nonlocal `105`: active `73`, overlap `38` (`36.2%`), median `0.300974`;
  - remaining nonpositive `6`: active `2`, candidate overlap `0`.
- Exact electric evidence persisted at `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json`, commit `f783f9c551e0efb8b9807e7bfe2a964826e18fee`.
- This independent model is useful as a **positive consensus source**, not a blind replacement: even on exact audio it misses many current V143 notes.

## Harmonic primary progression
### V3 — V143 physical evidence only
- `analyzer/v143_contextual_harmonic_primary_shadow_v3.py`; validator `analyzer/v143_contextual_harmonic_primary_shadow_v3_replay_validator.py`.
- V3 corrected `43/725` primaries using same-measure local support OR stricter two-view extra-harmonic support; attacks unchanged; invented/unplayable 0.
- V3 was deliberately not frozen because an independent source model had not yet confirmed the direction.

### V4 — strongest independent primary correction
- Exact-approved robust electric TabCNN supplies the independent criterion.
- Decision: accept a V3 lower-primary correction only when the external electric model's **max legal string/fret probability for the proposed lower primary is strictly greater than that for the old upper primary** at the same exact grid frame. Pairwise only; **no new numeric threshold**.
- Exact result: V3 proposed `43`; electric consensus accepts `34`, rejects `9`.
- Across all 43 V3 proposals, electric model favors new lower `34`, old upper `9`; median new-minus-old probability `+0.104154`; its discrete top tablature chooses new `16` times vs old `2`.
- V4 accepted intervals: octave `29`, 19 semitones `3`, two octaves `2`.
- Primary MIDI64 count `202 -> 187`.
- Exact replay after V4: attacks `725 -> 725`; selected pitches `970 -> 970`; rendered pitches `967 -> 967`; voicing drops remain `3`; invented pitch `0`; invalid primary `0`; unplayable primary `0`.
- Validator: `analyzer/v143_contextual_harmonic_primary_shadow_v4_replay_validator.py`, commit `6a1dd9285dacc863ccb9f0a6a7e508b719ea2c38`.
- Durable validation: `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`; local full validation SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- V4 remains a shadow and is now incorporated unchanged into the combined V5 content shadow below.

## Attack shadow V3 — CPU replay PASSED and durable
- Below the old 0.60 transient floor, the robust electric model's discrete predicted tablature pitch intersects the existing V143 candidate MIDI universe on `43` attacks: `5/25` V2 local-peak rescues + `38/105` previously-unrescued positive subfloor attacks; `0/6` nonpositive.
- Durable source evidence: `debug/v143-contextual-prune/electric-tabcnn-subfloor-attack-evidence.json`, commit `bb7d5d2050bce1c6a5f3995df2c741468a43b014`.
- Deterministic validator: `analyzer/v143_contextual_prune_attack_shadow_v3_replay_validator.py`, commit `d00e2699f07f60b6a5b76d81fc7197f9e5f23e8c`.
- Passing replay run `32818611451`, job `97711880585`; exact validation JSON SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Exact result: eligible `984`; baseline `725`; exception-band rescues `123`; electric subfloor rescues `43`; total rescues `166`; V3 retained `891`; remaining pruned `93`.
- Exact content: selected/rendered `1214/1209`; total voicing drops `5`; no invented pitch, invalid primary, unplayable primary, grid collision, or missing measure.
- Passing output durably committed at `debug/v143-contextual-prune/attack-shadow-v3-replay-validation.json`, commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`.
- `freezeReady=false` because downstream technique/sustain was not recomputed for newly rescued attacks.

## Combined content shadow V5 — CURRENT STRONGEST CONTENT SHADOW
- New deterministic validator: `analyzer/v143_contextual_prune_combined_content_shadow_v5_replay_validator.py`, commit `3e15b4689cbaf72fd086b7142033b980c9ac401a`.
- Policy: **Attack V3 + already-validated Primary V4**, with V4 applied only to its exact 34 matching pre-existing baseline attacks. No V4 correction touches a newly rescued attack.
- CPU workflow `.github/workflows/v143-combined-content-shadow-v5-replay.yml`, commit `6f705afb5f9f83e4bd70e9fe648e5c3fb4236f64`, replayed the immutable pinned candidate and guarded the protected runtime plus exact durable V3/V4 evidence blobs.
- Run `32819028013`, job `97713095027` passed every substantive step. Materializer again reported `Modal/L4 invoked false` and `professional reference invoked false`.
- Exact combined validation JSON SHA256: `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Exact combined counts: retained attacks `891`; selected pitches `1214`; rendered pitches `1209`; voicing drops `5`; remaining pruned attacks `93`; measures covered `113/113`.
- Baseline portion after V4 remains selected/rendered `970/967`, drops `3`, primary MIDI64 `187`.
- Rescued portion remains selected/rendered `244/242`, drops `2`, rescued primary MIDI64 `47`.
- Combined primary MIDI64 count is `234`.
- All `34` V4 primary corrections land on baseline attacks; corrections on rescued attacks `0`.
- No invented pitch, invalid primary, unplayable primary, unobserved attack/pitch, attack relocation, new inference, or new numeric threshold. All validator invariants passed.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- Exact output durably committed at `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`.
- Artifact ID `9552426114`; uploaded artifact ZIP digest `b829262dfc3f74dfb1c15d8f207ed32ff493d2185e296b0e9e5a3392b35ab1c2`.
- V5 is **not freeze-ready** solely because the newly rescued attacks still lack recomputed downstream technique/sustain evidence; professional scoring remains closed.

## PDF/string-fret state
- `lib/createV143RhythmPdf.js` is already a structured graphical six-line renderer; historical PDF fidelity reached `1.0`. Musical content correctness remains the main blocker.
- Current stateless voicing resolver cannot infer performer-intended positions from MIDI alone. The electric TabCNN can provide independent string/fret evidence; use it conservatively as consensus only where it agrees with V143-observed pitch.
- Current combined V5 voicing drops are exactly five attacks: m19/s6 `[52,86] -> [52]`; m40/s14 `[40,78] -> [40]`; m63/s14 `[47,78] -> [78]`; m113/s13 `[41,43] -> [41]`; m113/s14 `[43,44] -> [43]`.

## Research infrastructure / cleanup
- Draft PR #20 `v143-research-checkpoint-fetch` exists only to trigger bounded CPU research workflows. **Never merge it.**
- Temporary research workflows live only on `v143-contextual-prune-lobo`; remove them after needed public artifacts/provenance are durably captured.
- No Modal/L4 used in this entire specialized-model / V3 / combined-V5 replay phase.

## Current integrity
- Branch head immediately before this checkpoint update: `b0dce933d8686d0dbd1c1a7da78460053a71739f`.
- Protected runtime reverified exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` immediately before this checkpoint update.
- No Production/main change; no professional scorer/reference; no freeze-ready candidate yet.

## Next exact actions
1. Investigate **electric-model string/fret consensus** on combined V5, but only where the model agrees with an already-observed/selected V143 MIDI; quantify whether any current deterministic voicing can be improved without changing pitch identity.
2. Treat the five existing voicing-drop attacks as the first focused cases; do not invent notes or force model positions when the model lacks consensus.
3. Resolve downstream technique/sustain evidence for the `166` rescued attacks before any freeze/professional scoring.
4. Keep timing and tempo frozen; keep Attack V3 and Primary V4 criteria unchanged unless new source-only evidence proves a defect.
5. Improve conventional notation appearance only after musical content and technique/sustain are materially stronger.
6. Remove temporary CPU research workflows after their durable evidence is secured.
7. No Modal/L4 without fresh explicit authorization.
8. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
