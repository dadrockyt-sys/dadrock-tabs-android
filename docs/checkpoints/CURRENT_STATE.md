# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-25 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead; produce genuinely professional guitar tablature, not merely a polished-looking PDF.**

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities never rerun/rescore: `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without fresh explicit user authorization. None is currently authorized.**
- Timing frozen unless new source-only evidence proves otherwise; tempo exactly `129.19921875`.

## Preserved paid capture — CPU replay source of truth
- Authorized run `32805316807`; pinned capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; one Modal command consumed historically, automatic retry disabled.
- Baseline counts: eligible attacks `984`; retained `725`; pruned `259`; replay pitch hypotheses `10585`; selected `970`; rendered `967`; voicing drops `3`; measures `1-113`.
- Candidate SHA256 `a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951`; replay validation `182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a`; compare `c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda`; lock `49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be`.
- Durable manifest: `analyzer/fixtures/v143_precision_v2_modal_capture_32805316807.json`; CPU materializer: `analyzer/materialize_v143_precision_fixture.py`.

## Exact approved source audio / independent guitar evidence
- Exact approved source is in repo at `public/gomywayfullaitest.m4a`; CPU research fetch run `32815950324`, artifact `9551396214`, byte-exact approved SHA verified. No Modal.
- Acoustic GuitarSet HCQT+Mel fold1 checkpoint SHA256 `2572b3fe58429668ec9aeaee56bf40af265726a6c3652151b176b21da2bde953`; useful negative/secondary evidence but did not independently support the lower-primary V3 direction.
- Robust electric-guitar TabCNN from DAFx 2024 `robust-guitar-tabs/code`, CC0-1.0; Zenodo record `11406378`; checkpoint MD5 `ce168b2cd426f81a2a78499214e40605`, SHA256 `1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`.
- Acquisition run `32815631220`, artifact `9551275181`, no Modal/L4.
- Exact model contract: 22050 Hz, hop 512, CQT 192 bins / 24 bins-octave / C1, -80..0 dB -> 0..1, 9-frame context, six strings.
- Exact-approved grid evidence persisted at `debug/v143-contextual-prune/electric-tabcnn-v3-consensus-evidence.json` commit `f783f9c551e0efb8b9807e7bfe2a964826e18fee`.
- Group evidence: baseline overlap `348/725`; exception-band `60/123`; V2 subfloor-local `5/25`; remaining positive subfloor-nonlocal `38/105`; nonpositive `0/6`.
- Use this model only as independent **positive consensus**, never as a blind replacement.

## Attack shadow V3 — strongest validated attack shadow
- Legacy precision: ratio >=0.70 retain; 0.60-0.70 exception-band local criterion; <0.60 prune; positive requires attack>0 and body>-0.25.
- V2 had retained `873`: baseline `725` + `123` exception-band + `25` subfloor-local.
- Electric exact-audio evidence supports only `5/25` V2 subfloor-local rescues but independently supports `38/105` previously-unrescued positive subfloor nonlocal attacks.
- V3 policy: baseline `725` + existing exception-band `123` + electric-consensus subfloor `43` = **`891` retained**. Relative to V2: remove 20 unsupported local-subfloor, add 38 supported nonlocal, net +18.
- Validator `analyzer/v143_contextual_prune_attack_shadow_v3_replay_validator.py`, commit `d00e2699f07f60b6a5b76d81fc7197f9e5f23e8c`.
- Passing CPU replay run `32818611451`, job `97711880585`; exact validation SHA256 `039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892`.
- Durable output `debug/v143-contextual-prune/attack-shadow-v3-replay-validation.json`, commit `8c1a36f2254197adabc1ed1e1ef65ba62853d073`.
- Exact V3: eligible `984`; retained `891`; pruned `93` (`87` positive + `6` nonpositive); selected/rendered `1214/1209`; voicing drops `5`; rescued component `244/242`, drops `2`; no invented/unplayable/invalid pitch or missing measure.
- `freezeReady=false`: rescued attacks lack recomputed downstream technique/sustain evidence.

## Harmonic Primary V4 — strongest validated primary correction
- V3 physical harmonic shadow proposed `43` lower-primary corrections.
- V4 accepts only when exact electric model max legal probability for proposed lower primary is strictly greater than old upper primary at same grid frame; pairwise comparison only, no new scalar threshold.
- Exact: accepts `34`, rejects `9`; model favors new `34/43`; median new-old probability `+0.104154`; discrete top tab chooses new `16` vs old `2`.
- V4 accepted intervals: octave `29`, 19 semitones `3`, two octaves `2`; baseline primary MIDI64 `202 -> 187`.
- Validator `analyzer/v143_contextual_harmonic_primary_shadow_v4_replay_validator.py`, commit `6a1dd9285dacc863ccb9f0a6a7e508b719ea2c38`.
- Durable validation `debug/v143-contextual-prune/contextual-harmonic-primary-shadow-v4-validation.json`, commit `a742a3df5b468ee54b6fadf72c0f111b8c824424`; full SHA256 `7eea032a2bdc12fcb0d5e0c4693bdc7a6ea06db447d1a28c0044192e724cad99`.
- Baseline after V4 remains attacks `725`, selected/rendered `970/967`, drops `3`; no invented/invalid/unplayable primary.

## Combined Content Shadow V5 — CURRENT STRONGEST CONTENT SHADOW
- Validator `analyzer/v143_contextual_prune_combined_content_shadow_v5_replay_validator.py`, commit `3e15b4689cbaf72fd086b7142033b980c9ac401a`.
- Policy: Attack V3 + exact already-validated Primary V4, with all 34 V4 corrections applied only to matching pre-existing baseline attacks; corrections on rescued attacks `0`.
- Workflow `.github/workflows/v143-combined-content-shadow-v5-replay.yml`, commit `6f705afb5f9f83e4bd70e9fe648e5c3fb4236f64`.
- Passing run `32819028013`, job `97713095027`; materializer reported Modal/L4 false and professional reference false.
- Exact combined validation SHA256 `eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee`.
- Durable output `debug/v143-contextual-prune/combined-content-shadow-v5-validation.json`, commit `b0dce933d8686d0dbd1c1a7da78460053a71739f`; artifact `9552426114`, ZIP digest `b829262dfc3f74dfb1c15d8f207ed32ff493d2185e296b0e9e5a3392b35ab1c2`.
- Exact combined: retained attacks `891`; pruned `93`; selected/rendered `1214/1209`; voicing drops `5`; measures `113/113`; combined primary MIDI64 `234`.
- Baseline post-V4: `970/967`, drops `3`, primary MIDI64 `187`; rescued: `244/242`, drops `2`, primary MIDI64 `47`.
- No invented pitch, invalid/unplayable primary, unobserved attack/pitch, relocation, new inference, or new numeric threshold.
- `referenceFree=true`, `professionalReferenceUsed=false`, `modalInvoked=false`, `productionModified=false`.
- V5 remains **not freeze-ready** only because technique/sustain has not been recomputed for the 166 rescued attacks.

## V5 voicing-feasibility audit — PASSED and durable
- Exact V3 resolver contract reverified: standard tuning open MIDI high-to-low `(64,59,55,50,45,40)`, `MAX_FRET=24`, hard `MIDI span <=28`, unique/order-valid strings.
- Audit script `analyzer/v143_contextual_prune_voicing_feasibility_audit.py`, commit `58e72f8ffeb948c92dfee91172665406477547af`.
- CPU workflow `.github/workflows/v143-voicing-feasibility-audit.yml`, commit `1542cd539f7d4478951dd1d2ed2094b6123e25dc`.
- Passing run `32819559047`, job `97714646838`; protected runtime and exact V5 SHA guards passed; no Modal/reference/production changes.
- Exact audit SHA256 `b86e18609793095887324dbafad8d7940f275bb3cd60a0d0feb67de9e3c2c85a`.
- Durable output `debug/v143-contextual-prune/voicing-feasibility-audit.json`, commit `bbe3ff799096303dc196654cf1a7637707fdc8d8`; artifact `9552611189`, ZIP digest `3d96b0efd43821d5d3912253dd6fa8d805924deb0221f1561c2d29645260e065`.
- **All five V5 drops are fully explained without changing pitch identity:**
  - m19/s6 `[52,86] -> [52]`: physically assignable, MIDI span `34` > resolver cap `28`; example 52=D string fret2, 86=high-E fret22.
  - m40/s14 `[40,78] -> [40]`: physically assignable, span `38` > 28; example 40=low-E open, 78=high-E fret14.
  - m63/s14 `[47,78] -> [78]`: physically assignable, span `31` > 28; example 47=A string fret2, 78=high-E fret14.
  - m113/s13 `[41,43] -> [41]`: unavoidable string collision; both notes only legal on low-E (frets1/3).
  - m113/s14 `[43,44] -> [43]`: unavoidable string collision; both notes only legal on low-E (frets3/4).
- Classification: resolver MIDI-span limit `3`, unavoidable string collision `2`, individually-unplayable `0`, other `0`.
- Consequence: electric string/fret evidence can potentially adjudicate **whether the three wide-span pitch pairs are genuinely simultaneous musical content**, but cannot make the two m113 low-E pairs simultaneous without changing pitch/time identity. Do not relax the resolver cap merely to force them through.

## PDF state
- `lib/createV143RhythmPdf.js` is already a structured graphical six-line renderer; historical PDF fidelity reached `1.0`. Musical correctness remains the main blocker.
- Conventional notation appearance should be improved only after content and technique/sustain are stronger.

## Research infrastructure
- Draft PR #20 `v143-research-checkpoint-fetch` is only a CPU research trigger. **Never merge it.**
- Temporary CPU workflows live only on this research branch; remove them after durable evidence is secured.
- No Modal/L4 used in the specialized-model, Attack V3, V5, or voicing-audit work.

## Current integrity
- Branch head immediately before this checkpoint update: `bbe3ff799096303dc196654cf1a7637707fdc8d8`.
- Protected runtime reverified exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` immediately before this checkpoint update.
- No Production/main change; no professional scorer/reference; no freeze-ready candidate yet.

## Next exact actions
1. Recover/reconstruct the exact-approved electric TabCNN probe code sufficiently to emit **per-string/per-fret evidence at the three physically-assignable wide-span drops** m19/s6, m40/s14, m63/s14. Use pairwise/argmax evidence only; no new threshold and no pitch invention.
2. Determine whether electric evidence supports both selected pitches simultaneously at those frames; if not, treat this as content evidence rather than relaxing the 28-semitone resolver cap.
3. Do not attempt to force m113/s13 or m113/s14 into simultaneous voicings; their selected pitch pairs are physically same-string collisions under the frozen tuning/fret contract.
4. Resolve downstream technique/sustain evidence for all `166` rescued attacks before any freeze/professional scoring.
5. Keep timing/tempo, Attack V3 criteria, and Primary V4 criteria frozen unless new source-only evidence proves a defect.
6. Improve notation appearance after content + technique/sustain are materially stronger.
7. Remove temporary CPU workflows after evidence is durable.
8. No Modal/L4 without fresh explicit authorization.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, PDF fidelity=1.0.
